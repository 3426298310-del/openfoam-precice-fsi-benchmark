#!/usr/bin/env python3
"""Analyze only solver-generated data; literature data stay separate."""
import argparse, json, shutil
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args()
r=a.run.resolve();root=Path(__file__).resolve().parents[1];out=root/'results'/r.name;out.mkdir(parents=True,exist_ok=True)
meta=json.loads((r/'run.json').read_text())
wpath=r/'solid/precice-Solid-watchpoint-flaptip.log'
header=wpath.read_text().splitlines()[0].split();w=np.atleast_2d(np.loadtxt(wpath,skiprows=1))
assert np.isfinite(w).all() and np.all(np.diff(w[:,0])>0), 'Invalid watchpoint data'
t=w[:,header.index('Time')]; ux=w[:,header.index('Displacement0')];uy=w[:,header.index('Displacement1')]
np.savetxt(out/'tip-displacement.csv',np.c_[t,ux,uy],delimiter=',',header='time_s,ux_m,uy_m',comments='')
it=np.atleast_2d(np.loadtxt(r/'solid/precice-Solid-iterations.log',skiprows=1))
np.savetxt(out/'coupling-iterations.csv',it,delimiter=',',header='time_window,total_iterations,iterations,converged,qn_columns,deleted_qn_columns,dropped_qn_columns',comments='',fmt='%d')
conv=np.atleast_2d(np.loadtxt(r/'solid/precice-Solid-convergence.log',skiprows=1))
np.savetxt(out/'coupling-residuals.csv',conv,delimiter=',',header='time_window,iteration,displacement_abs_or_rel_measure,force_relative_measure',comments='')
fig,ax=plt.subplots(2,1,figsize=(10,6),sharex=True,layout='constrained')
for axis,y,label in zip(ax,[ux,uy],['Horizontal displacement [mm]','Vertical displacement [mm]']):
 axis.plot(t,1000*y,color='#126782',lw=1);axis.set_ylabel(label);axis.grid(alpha=.25)
ax[0].set_title(f'Turek-Hron {meta.get("benchmark","fsi3").upper()} | {r.name} | actual coupled simulation');ax[-1].set_xlabel('Time [s]');fig.savefig(out/'tip-displacement.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(2,1,figsize=(10,6),layout='constrained')
ax[0].plot(it[:,0]*meta['dt'],it[:,2],lw=.8,color='#126782');ax[0].set(xlabel='Time [s]',ylabel='Coupling iterations',title='Implicit coupling convergence')
ax[1].hist(it[:,2],bins=np.arange(it[:,2].min()-.5,it[:,2].max()+1.5),color='#126782');ax[1].set(xlabel='Iterations per time window',ylabel='Count')
for axis in ax:axis.grid(alpha=.2)
fig.savefig(out/'coupling-iterations.png',dpi=170);plt.close(fig)
summary={'run':meta,'last_time_s':float(t[-1]),'accepted_windows':int(it.shape[0]),'unconverged_windows':int(np.count_nonzero(it[:,3]!=1)), 'iterations_mean':float(it[:,2].mean()),'iterations_max':int(it[:,2].max()),'ux_range_m':[float(ux.min()),float(ux.max())],'uy_range_m':[float(uy.min()),float(uy.max())]}
summary['run_accepted']=bool(meta['status']=='completed' and np.isclose(t[-1],meta['end_time']) and np.all(it[:,3]==1) and len(it)==round(meta['end_time']/meta['dt']))
variant=meta.get('benchmark','fsi3')
ref=json.loads((root/'docs'/('benchmark.json' if variant=='fsi1' else 'benchmark-fsi3.json')).read_text())['reference']
summary['reference_comparison']={'status':'not_evaluated','reason':'Requires completed 20 s trajectory; early transient is not comparable with the periodic reference.'}
if summary['run_accepted'] and t[-1]>=20-1e-8 and variant=='fsi3':
 comparison={}
 for name,y in [('ux',ux),('uy',uy)]:
  last=y[t>=19.5-1e-8];mid=(last.max()+last.min())/2;amp=np.ptp(last)/2
  mask=t>=18;peaks,_=find_peaks(y[mask],prominence=max(amp*.5,1e-12));freq=float(1/np.mean(np.diff(t[mask][peaks]))) if len(peaks)>2 else None
  comparison[name]={'window_s':[19.5,20],'midrange_m':float(mid),'amplitude_m':float(amp),'frequency_Hz':freq,'frequency_window_s':[18,20], 'reference':ref[name], 'midrange_error_percent':float(100*(mid-ref[name]['midrange_m'])/abs(ref[name]['midrange_m'])),'amplitude_error_percent':float(100*(amp-ref[name]['amplitude_m'])/ref[name]['amplitude_m'])}
 summary['reference_comparison']={'status':'compared_not_grid_verified','values':comparison,'note':'Numerical agreement does not substitute mesh/time-step independence or model verification.'}
 fig,ax=plt.subplots(2,1,figsize=(10,6),sharex=True,layout='constrained')
 for axis,name,y in zip(ax,['ux','uy'],[ux,uy]):
  m=t>=19.5;axis.plot(t[m],1000*y[m],label='Computed');rr=ref[name];axis.axhline(1000*(rr['midrange_m']+rr['amplitude_m']),color='darkorange',ls='--',label='Reference extrema');axis.axhline(1000*(rr['midrange_m']-rr['amplitude_m']),color='darkorange',ls='--');axis.set_ylabel(name+' [mm]');axis.grid(alpha=.2);axis.legend()
 ax[-1].set_xlabel('Time [s]');fig.savefig(out/'reference-comparison.png',dpi=170);plt.close(fig)
if variant=='fsi1' and summary['run_accepted'] and t[-1]>=20-1e-8:
 comparison={}
 for name,y in [('ux',ux),('uy',uy)]:
  mask=t>=max(0,t[-1]-2);value=float(y[mask].mean());span=float(np.ptp(y[mask]));reference=ref[name+'_m']
  comparison[name]={'mean_last_2s_m':value,'last_2s_peak_to_peak_m':span,'reference_m':reference,'error_percent':100*(value-reference)/abs(reference)}
 forces_path=r/'fluid/postProcessing/Forces/0/force.dat'
 if forces_path.exists():
  raw=np.atleast_2d(np.loadtxt(forces_path)); last_rows={float(row[0]):row for row in raw};forces=np.array([last_rows[k] for k in sorted(last_rows)])
  np.savetxt(out/'forces-per-unit-depth.csv',np.c_[forces[:,0],forces[:,1:3]/0.01],delimiter=',',header='time_s,drag_N_per_m,lift_N_per_m',comments='')
  for name,col in [('drag',1),('lift',2)]:
   values=forces[forces[:,0]>=t[-1]-2,col]/0.01;value=float(values.mean());reference=ref[name+'_N_per_m']
   comparison[name]={'mean_last_2s_N_per_m':value,'last_2s_peak_to_peak_N_per_m':float(np.ptp(values)),'reference_N_per_m':reference,'error_percent':100*(value-reference)/abs(reference)}
 summary['reference_comparison']={'status':'compared_not_grid_verified','values':comparison,'note':'FSI1 steady reference. Time-step and spatial convergence need separate studies.'}
 fig,ax=plt.subplots(2,1,figsize=(10,6),sharex=True,layout='constrained')
 for axis,name,y in zip(ax,['ux','uy'],[ux,uy]):
  axis.plot(t,y*1000,label='Computed');axis.axhline(ref[name+'_m']*1000,color='darkorange',ls='--',label='FSI1 reference');axis.set_ylabel(name+' [mm]');axis.grid(alpha=.2);axis.legend()
 ax[-1].set_xlabel('Time [s]');fig.savefig(out/'reference-comparison.png',dpi=170);plt.close(fig)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
# Keep compact raw evidence alongside CSVs; full solver logs remain in results/runs.
for f in ['precice-Solid-watchpoint-flaptip.log','precice-Solid-iterations.log','precice-Solid-convergence.log']:
 shutil.copy(r/'solid'/f,out/f)
shutil.copy(r/'run.json',out/'run.json')
print(json.dumps(summary,indent=2))
