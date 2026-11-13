#!/usr/bin/env python3
"""Spot-check image detections against projected ground-truth cones (no depth).

Saves annotated samples and reports detections over 15 pixels from any true cone
base. This is a screening metric; inspect annotations for occlusion/association.
"""
import argparse,csv,json,math,sys
from pathlib import Path
import cv2,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src/saurcon_plan'))
from saurcon_plan.cones import ConeDetector
from saurcon_plan.track import Track
p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);p.add_argument('world',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
rows=list(csv.reader((a.run/'log.csv').open()));gt=np.array([[float(r[0]),*map(float,r[2:5])] for r in rows if len(r)>4 and r[1]=='gt']);gt=gt[np.argsort(gt[:,0])];gt[:,3]=np.unwrap(gt[:,3])
frames=[(float(r[0]),int(r[2])) for r in rows if len(r)>2 and r[1]=='frame' and gt[0,0]<=float(r[0])<=gt[-1,0]]
cones=Track.from_world(a.world).cones;fx=320/math.tan(1.204/2);det=ConeDetector(fx,fx,320,200,camera_height=.137)
results=[]
for j in np.linspace(0,len(frames)-1,20,dtype=int):
    t,index=frames[j];im=cv2.imread(str(a.run/'frames'/f'{index:06d}.jpg'))
    x,y,yaw=[np.interp(t,gt[:,0],gt[:,k]) for k in (1,2,3)]
    c,s=math.cos(yaw),math.sin(yaw);d=cones-(x,y);z=c*d[:,0]+s*d[:,1]-.219;left=-s*d[:,0]+c*d[:,1];valid=z>.2
    uv=np.column_stack([320-fx*left[valid]/z[valid],200+fx*.137/z[valid]])
    ds=det.detect(im);bad=0
    for q in ds:
        distance=float(np.linalg.norm(uv-(q.u,q.v),axis=1).min()) if len(uv) else float('inf')
        bad+=distance>15;cv2.circle(im,(int(q.u),int(q.v)),8,(0,0,255) if distance>15 else (0,255,0),1)
    for u,v in uv:
        if 0<=u<640 and 0<=v<400:cv2.drawMarker(im,(int(u),int(v)),(255,255,0),cv2.MARKER_CROSS,6,1)
    cv2.imwrite(str(a.out/f'{index:06d}.jpg'),im)
    results.append({'frame':index,'t':t,'detections':len(ds),'unmatched_over_15px':bad})
res={'frames':len(results),'detections':sum(r['detections'] for r in results),'unmatched':sum(r['unmatched_over_15px'] for r in results),'samples':results};(a.out/'audit.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
