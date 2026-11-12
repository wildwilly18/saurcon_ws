import csv, math, sys, os
import numpy as np, cv2
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
S=os.path.dirname(os.path.abspath(__file__)); OUT=S+'/out'
INK='#0b0b0b'; INK2='#52514e'; SURF='#fcfcfb'; BLUE='#2a78d6'; ORANGE='#eb6834'; GRID='#e4e3df'
plt.rcParams.update({'figure.facecolor':SURF,'axes.facecolor':SURF,'axes.edgecolor':GRID,'axes.labelcolor':INK2,
 'xtick.color':INK2,'ytick.color':INK2,'text.color':INK,'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.8,
 'axes.spines.top':False,'axes.spines.right':False,'font.size':10,'axes.titlesize':11,'axes.titleweight':'bold','legend.frameon':False})
MARKERS=[(0,0,0),(1,3.5,0),(2,7,0),(3,9,2),(4,7,4),(5,3.5,4),(6,0,4),(7,-3.5,4),(8,-7,4),(9,-10.5,4),(10,-12.5,2),(11,-10.5,0),(12,-7,0),(13,-3.5,0)]
def load(d):
    r={'gt':[],'nav':[],'aruco':[],'frame':[]}
    for row in csv.reader(open(d+'/log.csv')):
        if row[1] in r: r[row[1]].append([float(v) for v in [row[0]]+row[2:] if v!=''])
    r={k:np.array(v) for k,v in r.items()}
    gt=r['gt']; sp=np.hypot(np.diff(gt[:,1]),np.diff(gt[:,2]))/np.maximum(np.diff(gt[:,0]),1e-3)
    t0=gt[np.argmax(sp>0.15),0]
    for k in r: r[k][:,0]-=t0
    r['gt_speed']=np.column_stack([gt[1:,0]-t0, np.convolve(sp,np.ones(5)/5,'same')])
    r['dir']=d
    return r
def wrap(a): return np.arctan2(np.sin(a),np.cos(a))
def errs(r,t1=47.0):
    nav=r['nav']; gt=r['gt']; m=(nav[:,0]>=-1)&(nav[:,0]<=t1); t=nav[m,0]
    gx=np.interp(t,gt[:,0],gt[:,1]); gy=np.interp(t,gt[:,0],gt[:,2]); gyaw=np.interp(t,gt[:,0],np.unwrap(gt[:,3]))
    return t, np.hypot(nav[m,1]-gx,nav[m,2]-gy), np.degrees(wrap(nav[m,3]-gyaw))
runs=[('Original code',load(S+'/run_orig')),('Fixed code',load(S+'/run_fixed'))]
T1=47.0
stats={}
for name,r in runs:
    t,pe,he=errs(r); stats[name]=(np.sqrt(np.mean(pe**2)),pe.max(),np.sqrt(np.mean(he**2)),np.abs(he).max(),pe[-1])
    print('%-14s position error RMS %.2f m, max %.2f m, end %.2f m | heading error RMS %.1f deg, max %.1f deg'%(name,*stats[name][:2],stats[name][4],*stats[name][2:4]))
    a=r['aruco']; print('   aruco fixes during lap:',int(((a[:,0]>=0)&(a[:,0]<=T1)).sum()), ' nav msgs:',int(((r['nav'][:,0]>=0)&(r['nav'][:,0]<=T1)).sum()))

# ---- Figure 1: top-down trajectories ----
fig,axs=plt.subplots(2,1,figsize=(11,9.2),sharex=True)
for ax,(name,r) in zip(axs,runs):
    g=r['gt']; n=r['nav']; a=r['aruco']
    mg=(g[:,0]>=-1)&(g[:,0]<=T1); mn=(n[:,0]>=-1)&(n[:,0]<=T1); ma=(a[:,0]>=-1)&(a[:,0]<=T1)
    ax.plot(g[mg,1],g[mg,2],color=INK2,lw=2,label='Ground truth (simulator)',zorder=2)
    ax.scatter(a[ma,1],a[ma,2],s=9,color=ORANGE,label='ArUco fixes (filter input)',zorder=3,linewidths=0)
    ax.plot(n[mn,1],n[mn,2],color=BLUE,lw=2,label='Filter estimate',zorder=4)
    for i,x,y in MARKERS:
        ax.plot(x,y,marker='s',ms=5,color=INK,zorder=5,ls='none'); ax.annotate(str(i),(x,y),textcoords='offset points',xytext=(5,5),fontsize=8,color=INK2)
    s=stats[name]; ax.set_title('%s — position error RMS %.2f m, max %.2f m'%(name,s[0],s[1]),loc='left')
    ax.set_aspect('equal'); ax.set_xlim(-15,11.5); ax.set_ylim(-3.2,7.2); ax.set_ylabel('y (m)')
axs[0].legend(loc='upper center',ncol=3,bbox_to_anchor=(0.5,1.0),fontsize=9)
axs[1].set_xlabel('x (m)   ·   black squares are the ArUco markers, numbered by ID')
fig.suptitle('One lap of the racetrack: where the filter thinks the car is vs. where it really is',x=0.01,ha='left',fontsize=13,fontweight='bold')
fig.tight_layout(rect=(0,0,1,0.97)); fig.savefig(OUT+'/trajectory.png',dpi=130); plt.close(fig)

# ---- Figure 2: error vs time (small multiples; one axis each) ----
fig,axs=plt.subplots(2,2,figsize=(11,6.2),sharex=True,sharey='row')
for j,(name,r) in enumerate(runs):
    t,pe,he=errs(r)
    axs[0,j].plot(t,pe,color=BLUE,lw=2); axs[1,j].plot(t,he,color=BLUE,lw=2)
    axs[0,j].set_title(name,loc='left'); axs[1,j].set_xlabel('time since the car starts moving (s)')
axs[0,0].set_ylabel('position error (m)'); axs[1,0].set_ylabel('heading error (deg)')
fig.suptitle('Filter error against ground truth during the lap',x=0.01,ha='left',fontsize=13,fontweight='bold')
fig.tight_layout(rect=(0,0,1,0.96)); fig.savefig(OUT+'/error.png',dpi=130); plt.close(fig)

# ---- Figure 3: filter states vs truth ----
fig,axs=plt.subplots(4,2,figsize=(11,9.5),sharex=True,sharey='row')
for j,(name,r) in enumerate(runs):
    g=r['gt']; n=r['nav']; mg=(g[:,0]>=-1)&(g[:,0]<=T1); mn=(n[:,0]>=-1)&(n[:,0]<=T1); sp=r['gt_speed']; ms=(sp[:,0]>=-1)&(sp[:,0]<=T1)
    for i,(col,lab) in enumerate([(1,'x (m)'),(2,'y (m)'),(3,'heading (deg, unwrapped)')]):
        gv=g[mg,col]; nv=n[mn,col]
        if col==3:
            gv=np.degrees(np.unwrap(gv)); nv=np.degrees(np.interp(n[mn,0],g[mg,0],np.unwrap(g[mg,col]))+wrap(nv-np.interp(n[mn,0],g[mg,0],np.unwrap(g[mg,col]))))
        axs[i,j].plot(g[mg,0],gv,color=INK2,lw=2,label='Ground truth'); axs[i,j].plot(n[mn,0],nv,color=BLUE,lw=2,label='Filter estimate')
        axs[i,0].set_ylabel(lab)
    axs[3,j].plot(sp[ms,0],sp[ms,1],color=INK2,lw=2); axs[3,j].plot(n[mn,0],n[mn,4],color=BLUE,lw=2); axs[3,0].set_ylabel('speed (m/s)')
    axs[0,j].set_title(name,loc='left'); axs[3,j].set_xlabel('time since the car starts moving (s)')
axs[0,1].legend(loc='upper right',fontsize=9)
fig.suptitle('Kalman filter state output vs. ground truth',x=0.01,ha='left',fontsize=13,fontweight='bold')
fig.tight_layout(rect=(0,0,1,0.97)); fig.savefig(OUT+'/states.png',dpi=130); plt.close(fig)

# ---- Video: camera + live map, fixed on top, original below ----
W,H=640,400; SC=24.0; X0=-14.2; Y1=7.6
def px(x,y): return (int(round((x-X0)*SC)), int(round((Y1-y)*SC))+50)
def bgr(h): h=h.lstrip('#'); return (int(h[4:6],16),int(h[2:4],16),int(h[0:2],16))
def panel(name,r,t):
    f=r['frame']; i=int(np.searchsorted(f[:,0],t)); i=min(max(i,0),len(f)-1)
    cam=cv2.imread('%s/frames/%06d.jpg'%(r['dir'],int(f[i,1])))
    mp=np.full((H,W,3),bgr(SURF),np.uint8)
    g=r['gt']; n=r['nav']; a=r['aruco']
    def poly(arr,col,th):
        m=(arr[:,0]>=-1)&(arr[:,0]<=t)
        if m.sum()>1: cv2.polylines(mp,[np.array([px(x,y) for x,y in arr[m,1:3][::3]],np.int32)],False,bgr(col),th,cv2.LINE_AA)
    poly(g,INK2,2)
    for x,y in a[(a[:,0]>=-1)&(a[:,0]<=t),1:3]:
        p=px(x,y)
        if 0<=p[0]<W and 0<=p[1]<H: cv2.circle(mp,p,2,bgr(ORANGE),-1,cv2.LINE_AA)
    poly(n,BLUE,2)
    for _,x,y in MARKERS: p=px(x,y); cv2.rectangle(mp,(p[0]-3,p[1]-3),(p[0]+3,p[1]+3),bgr(INK),-1)
    gi=min(int(np.searchsorted(g[:,0],t)),len(g)-1); ni=min(int(np.searchsorted(n[:,0],t)),len(n)-1)
    cv2.circle(mp,px(g[gi,1],g[gi,2]),6,bgr(INK2),-1,cv2.LINE_AA); cv2.circle(mp,px(n[ni,1],n[ni,2]),6,bgr(BLUE),2,cv2.LINE_AA)
    err=math.hypot(g[gi,1]-n[ni,1],g[gi,2]-n[ni,2]) if n[ni,0]<=t+0.5 and n[0,0]<=t else float('nan')
    cv2.putText(mp,name,(12,24),cv2.FONT_HERSHEY_SIMPLEX,0.62,bgr(INK),2,cv2.LINE_AA)
    cv2.putText(mp,'t = %5.1f s    position error = %.2f m'%(t,err),(12,46),cv2.FONT_HERSHEY_SIMPLEX,0.5,bgr(INK2),1,cv2.LINE_AA)
    y=H-14
    for lab,col,x in (('ground truth',INK2,12),('filter estimate',BLUE,150),('ArUco fixes',ORANGE,310),('markers',INK,440)):
        cv2.circle(mp,(x+5,y-4),5,bgr(col),-1,cv2.LINE_AA); cv2.putText(mp,lab,(x+16,y),cv2.FONT_HERSHEY_SIMPLEX,0.45,bgr(INK2),1,cv2.LINE_AA)
    cv2.putText(cam,name+' - onboard camera',(10,22),cv2.FONT_HERSHEY_SIMPLEX,0.55,(255,255,255),2,cv2.LINE_AA)
    return np.hstack([cam,mp])
FPS=15; ts=np.arange(-2.0,T1+9.0,1.0/FPS)
path=OUT+'/lap_comparison.mp4'
vw=None
for cc in ('avc1','mp4v'):
    vw=cv2.VideoWriter(path,cv2.VideoWriter_fourcc(*cc),FPS,(2*W,2*H))
    if vw.isOpened(): print('codec',cc); break
for t in ts:
    vw.write(np.vstack([panel('Fixed code',runs[1][1],t),panel('Original code',runs[0][1],t)]))
vw.release(); print('video',path,os.path.getsize(path)//1024,'kB',len(ts),'frames')
cv2.imwrite(OUT+'/video_frame.png',np.vstack([panel('Fixed code',runs[1][1],30.0),panel('Original code',runs[0][1],30.0)]))
