#!/usr/bin/env python3
"""Build a deterministic, tag-free asymmetric RGB-D warehouse course."""
from pathlib import Path
import math, json, copy
import numpy as np
import cv2
import xml.etree.ElementTree as E
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(731)
t=np.linspace(0,2*np.pi,6000,endpoint=False)
r=8+1.5*np.cos(3*t)+.7*np.sin(2*t)
p=np.column_stack([1.35*r*np.cos(t), r*np.sin(t)])
d=np.roll(p,-1,axis=0)-p
s=np.r_[0,np.cumsum(np.linalg.norm(d,axis=1))]
length=s[-1]
ss=np.arange(0,length,.65)
gates=np.column_stack([np.interp(ss,s,np.r_[p[:,i],p[0,i]]) for i in range(2)])
tang=np.roll(gates,-1,axis=0)-np.roll(gates,1,axis=0); tang/=np.linalg.norm(tang,axis=1)[:,None]
norm=np.column_stack([-tang[:,1],tang[:,0]])
tree=cKDTree(p)
root=E.Element('sdf',version='1.9'); w=E.SubElement(root,'world',name='warehouse_irregular')
source=E.parse(ROOT/'worlds/racetrack.world').getroot().find('world')
for e in source:
    if e.tag not in ('model','include','light','scene'):w.append(copy.deepcopy(e))
E.SubElement(w,'scene').append(E.fromstring('<ambient>0.38 0.38 0.38 1</ambient>'))
w.append(E.fromstring('<light name="sun" type="directional"><direction>-.3 .2 -1</direction><diffuse>.8 .8 .8 1</diffuse><cast_shadows>true</cast_shadows></light>'))
E.SubElement(w.find('scene'),'background').text='.18 .22 .28 1'
objects=[]
def box(name,x,y,z,sx,sy,sz,color,yaw=0,collision=True):
    m=E.SubElement(w,'model',name=name);E.SubElement(m,'static').text='true'
    E.SubElement(m,'pose').text=f'{x} {y} {z} 0 0 {yaw}'
    l=E.SubElement(m,'link',name='body')
    g=E.fromstring(f'<geometry><box><size>{sx} {sy} {sz}</size></box></geometry>')
    v=E.SubElement(l,'visual',name='surface');v.append(copy.deepcopy(g))
    mat=E.SubElement(v,'material');rgba=' '.join(map(str,(*color,1)))
    E.SubElement(mat,'ambient').text=rgba;E.SubElement(mat,'diffuse').text=rgba
    if collision:E.SubElement(l,'collision',name='solid').append(g)
box('floor',0,0,-.05,36,30,.1,(.43,.44,.45))
for i,(x,y,sx,sy) in enumerate([(0,14.5,36,.2),(0,-14.5,36,.2),(17.5,0,.2,29),(-17.5,0,.2,29)]):box(f'wall_{i}',x,y,1.4,sx,sy,2.8,(.60,.64,.68))
# Sparse irregular floor repairs: ordinary visual texture, no fiducials or route hints.
for i in range(250):
    x,y=rng.uniform(-17,17),rng.uniform(-14,14); c=float(rng.uniform(.29,.53))
    box(f'concrete_patch_{i}',x,y,.0006,rng.uniform(.08,.5),rng.uniform(.03,.2),.001,(c,c,c),float(rng.uniform(-3,3)),False)
for i,(c,n) in enumerate(zip(gates,norm)):
    yaw=math.atan2(tang[i,1],tang[i,0])
    for side,sgn in [('a',1),('b',-1)]:
        q=c+sgn*1.1*n
        inc=E.SubElement(w,'include');E.SubElement(inc,'uri').text='model://rc_cone'
        E.SubElement(inc,'name').text=f'cone_gate_{i:03}_{side}'
        E.SubElement(inc,'pose').text=f'{q[0]:.5f} {q[1]:.5f} 0 0 0 {yaw:.5f}'
# Deliberately different silhouettes and colors around the loop, close to camera height.
palette=[(.15,.30,.48),(.23,.40,.29),(.38,.25,.42),(.45,.39,.29)]
for i in range(0,len(gates),5):
    for side in (-1,1):
        q=gates[i]+side*2.65*norm[i]
        # Conservatively enclose every cluster in a 0.9 m disc, outside the 2.2 m lane.
        if tree.query(q)[0]<2.1 or abs(q[0])>16 or abs(q[1])>13:continue
        k=len(objects);objects.append(q.tolist());color=palette[(i//5)%4]
        h=float(rng.uniform(.45,1.5));yaw=float(rng.uniform(-.7,.7))
        box(f'cabinet_{k}',*q,h/2,1,.6,h,color,yaw)
        # Slats and contrasting small inset panels on both faces yield non-repeating corners.
        for j in range(7):
            xx=float(rng.uniform(-.40,.40)); zz=float(rng.uniform(.09,max(.1,h-.05)))
            for face in (-1,1):
                local=np.array([xx,face*.305]);rot=np.array([[math.cos(yaw),-math.sin(yaw)],[math.sin(yaw),math.cos(yaw)]])
                a=q+rot@local
                shade=float(rng.uniform(.15,.8))
                box(f'panel_{k}_{j}_{face}',*a,zz,.08,.012,.065,(shade,shade,shade),yaw,False)
        # Offset cartons, pallet slats and uprights give actual depth discontinuities.
        for j in range(3):
            z=h+.10+j*.12
            box(f'carton_{k}_{j}',q[0]+.10*math.sin(k+j),q[1],z,.45-j*.07,.42,.18,(.48+j*.08,.44+j*.06,.34+j*.06),yaw+j*.15)
        for sign in (-1,1):box(f'post_{k}_{sign}',q[0]+sign*.62,q[1],.5,.07,.07,1,(.18,.21,.25))
spawn=gates[0];yaw=math.atan2(tang[0,1],tang[0,0])
inc=E.SubElement(w,'include');E.SubElement(inc,'uri').text='model://rc_ackermann_vehicle';E.SubElement(inc,'name').text='rc_vehicle'
E.SubElement(inc,'pose').text=f'{spawn[0]} {spawn[1]} .05 0 0 {yaw}'
# Appearance-only enrichment. Separate RNG streams preserve the course sidecar and
# every existing obstacle pose/collision, including the original generation RNG.
texture_dir=ROOT/'models/feature_warehouse_materials/textures'
texture_dir.mkdir(parents=True,exist_ok=True)
def texture(name,seed,size,kind):
    gen=np.random.default_rng(seed)
    base=gen.normal(145,12,(size,size)).astype(np.float32)
    for scale,weight in [(16,22),(64,15),(256,12)]:
        noise=gen.normal(0,1,(scale,scale)).astype(np.float32)
        base+=weight*cv2.resize(noise,(size,size),interpolation=cv2.INTER_CUBIC)
    im=np.clip(base,35,220).astype(np.uint8)
    if kind=='floor':
        # Multiscale aggregate chips and branching cracks, never encoded patterns.
        for _ in range(55000):
            x,y=gen.integers(0,size,2);r=int(gen.integers(2,9))
            angles=np.sort(gen.uniform(0,2*np.pi,5)); radii=gen.uniform(4,15,5)
            chip=np.column_stack([x+radii*np.cos(angles),y+radii*np.sin(angles)]).astype(np.int32)
            cv2.fillPoly(im,[chip],int(gen.integers(10,245)))
        for _ in range(55):
            q=gen.integers(0,size,2).astype(float); pts=[q.copy()]
            heading=gen.uniform(0,6.28)
            for j in range(18):
                heading+=gen.normal(0,.3);q=q+gen.uniform(8,40)*np.array([np.cos(heading),np.sin(heading)]);pts.append(q.copy())
            cv2.polylines(im,[np.array(pts,np.int32)],False,55,2,cv2.LINE_AA)
    else:
        # Wood grain / worn paint / masonry seams, plus ordinary readable labels.
        for _ in range(350):
            x,y=gen.integers(0,size,2);span=int(gen.integers(5,max(6,size//3)))
            cv2.line(im,(int(x),int(y)),(int(x+span),int(y+gen.integers(-5,6))),int(gen.integers(40,220)),int(gen.integers(1,4)))
        if kind=='wall':
            for row,y in enumerate(range(0,size,100)):
                cv2.line(im,(0,y),(size,y),60,4)
                for x in range((row%2)*90,size,180):cv2.line(im,(x,y),(x,min(size,y+100)),70,3)
        else:
            for y in range(0,size,80):cv2.line(im,(0,y),(size,y),65,3)
        for _ in range(180):
            x,y=gen.integers(0,size,2); angles=np.sort(gen.uniform(0,2*np.pi,6)); radii=gen.uniform(3,18,6)
            patch=np.column_stack([x+radii*np.cos(angles),y+radii*np.sin(angles)]).astype(np.int32)
            cv2.fillPoly(im,[patch],int(gen.integers(25,235)))
        title=('RECEIVING','WORKSHOP','STORES','DISPATCH')[seed%4] if kind=='wall' else f'STOCK {seed-1000:02d}'
        cv2.putText(im,title,(size//15,size//3),cv2.FONT_HERSHEY_SIMPLEX,max(.45,size/1100),235,max(1,size//350),cv2.LINE_AA)
    # Achromatic surfaces cannot enter the saturated orange cone-detector band.
    im=np.clip((im.astype(np.float32)-128)*1.6+128,0,255).astype(np.uint8)
    cv2.imwrite(str(texture_dir/(name+'.png')),im)
    return name
# Portable package-relative URIs resolved through the launch's middle_earth path.
def apply_texture(model,name):
    mat=model.find('link/visual/material')
    mat.find('ambient').text='1 1 1 1';mat.find('diffuse').text='1 1 1 1'
    metal=E.SubElement(E.SubElement(mat,'pbr'),'metal')
    E.SubElement(metal,'albedo_map').text='model://feature_warehouse_materials/textures/'+name+'.png'
    E.SubElement(metal,'roughness').text='.9';E.SubElement(metal,'metalness').text='0'
texture('concrete',900,4096,'floor')
for model in w.findall('model'):
    name=model.get('name')
    if name=='floor':apply_texture(model,'concrete')
    elif name.startswith('wall_'):
        seed=800+int(name.split('_')[-1]);texture(name,seed,2048,'wall');apply_texture(model,name)
    elif name.startswith('cabinet_'):
        k=int(name.split('_')[-1]);asset=f'storage_{k:02d}';texture(asset,1000+k,512,'storage');apply_texture(model,asset)
    elif name.startswith('carton_'):
        k=int(name.split('_')[1]);apply_texture(model,f'storage_{k:02d}')
# A textured ceiling fills the former white sky; no new collision geometry.
box('ceiling',0,0,2.81,36,30,.02,(1,1,1),collision=False)
apply_texture(w.findall('model')[-1],'concrete')
E.SubElement(w.findall('model')[-1].find('link/visual'),'cast_shadows').text='false'

E.indent(root); out=ROOT/'worlds/feature_warehouse.world';E.ElementTree(root).write(out,encoding='unicode',xml_declaration=True)
meta={'world':'warehouse_irregular','length_m':length,'gate_width_m':2.2,'gates':len(gates),'spawn_model_xy_yaw':[float(spawn[0]),float(spawn[1]),yaw],'centerline_xy':p[::5].tolist(),'feature_cluster_centers':objects,'minimum_cluster_center_distance_m':min(tree.query(objects)[0])}
out.with_suffix('.track.json').write_text(json.dumps(meta,indent=1)+'\n')
fig,ax=plt.subplots(figsize=(12,10));ax.set_facecolor('#e6e7e4')
ax.plot(p[:,0],p[:,1],color='white',lw=22,zorder=1)
ax.plot(p[:,0],p[:,1],color='#43556b',lw=1.3,ls='--',label='Irregular loop')
for sign in (-1,1):q=gates+sign*1.1*norm;ax.scatter(q[:,0],q[:,1],s=9,c='#df872c',zorder=3)
a=np.array(objects);ax.scatter(a[:,0],a[:,1],s=130,marker='s',c='#487b82',label='Distinct 3-D storage clusters')
ax.scatter(*spawn,s=160,c='#b7374e',marker='*',label='Spawn')
ax.set(xlim=(-18,18),ylim=(-15,15),aspect='equal',xlabel='metres',ylabel='metres',title=f'Feature warehouse • no tags • {length:.1f} m asymmetric loop\n2.2 m cone corridor, low-level detail and varied depth landmarks')
ax.legend(loc='lower left');fig.tight_layout();fig.savefig(ROOT/'worlds/feature_warehouse.png',dpi=130)
print(out,meta['length_m'],len(gates),len(objects),meta['minimum_cluster_center_distance_m'])
