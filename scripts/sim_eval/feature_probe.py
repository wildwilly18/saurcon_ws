#!/usr/bin/env python3
"""Report GFTT/ORB counts and weakest two-second frame interval of a logged run."""
import argparse,csv,json
from pathlib import Path
import cv2
import numpy as np

def probe(run,stride=1,start=-float("inf"),end=float("inf")):
    stamps={int(r[2]):float(r[0]) for r in csv.reader((run/'log.csv').open()) if len(r)>2 and r[1]=='frame'}
    rows=[]; orb=cv2.ORB_create(nfeatures=1500)
    for file in sorted((run/'frames').glob('*.jpg'))[::stride]:
        stamp=stamps.get(int(file.stem),float('nan'))
        if not start<=stamp<=end: continue
        im=cv2.imread(str(file),0)
        if im is None: continue
        pts=cv2.goodFeaturesToTrack(im,2000,.01,7)
        f=im.astype(np.float32); mean=cv2.boxFilter(f,-1,(9,9)); contrast=np.sqrt(np.maximum(cv2.boxFilter(f*f,-1,(9,9))-mean*mean,0))
        rows.append([stamps.get(int(file.stem),float('nan')),0 if pts is None else len(pts),len(orb.detect(im,None)),float(np.mean(contrast>10))])
    if not rows: raise ValueError('No frames in requested interval')
    a=np.array(rows); a=a[np.argsort(a[:,0])]; windows=[]
    for t in a[:,0]:
        m=(a[:,0]>=t)&(a[:,0]<t+2)
        if a[-1,0]>=t+2: windows.append((float(np.median(a[m,1])),float(t),float(np.max(a[m,1]))))
    result={'run':str(run),'frames':len(a),'percentiles':[0,5,25,50,75,95,100], 'gftt':np.percentile(a[:,1],[0,5,25,50,75,95,100]).tolist(),'orb':np.percentile(a[:,2],[0,5,25,50,75,95,100]).tolist(),'median_contrast_fraction':float(np.median(a[:,3])),'worst_2s_median_start_max':min(windows) if windows else None,'two_second_windows_all_frames_below_150':sum(mx<150 for _,_,mx in windows)}
    return result,rows
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);p.add_argument('--stride',type=int,default=1);p.add_argument('--output',type=Path);p.add_argument('--start',type=float,default=-float('inf'));p.add_argument('--end',type=float,default=float('inf'));a=p.parse_args()
    result,rows=probe(a.run,a.stride,a.start,a.end);print(json.dumps(result,indent=2))
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
        with a.output.with_suffix('.csv').open('w') as f:
            w=csv.writer(f);w.writerow(['t','gftt','orb','contrast_fraction']);w.writerows(rows)
