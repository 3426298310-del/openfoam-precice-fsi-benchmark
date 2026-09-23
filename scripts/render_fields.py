#!/usr/bin/env python3
"""Read actual OpenFOAM moving mesh fields with VTK; render without a GUI."""
from pathlib import Path
import argparse,json
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.animation import FuncAnimation,PillowWriter
p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--animate',action='store_true');a=p.parse_args()
r=a.run.resolve();root=Path(__file__).resolve().parents[1];out=root/'results'/r.name;out.mkdir(parents=True,exist_ok=True)
case=r/'fluid/fluid.foam';case.touch()
reader=vtk.vtkOpenFOAMReader();reader.SetFileName(str(case));reader.SetCreateCellToPoint(0);reader.UpdateInformation();reader.EnableAllCellArrays()
times=vtk_to_numpy(reader.GetTimeValues())
# Some OpenFOAM adapter versions create time folders containing no volume fields.
times=np.array([t for t in times if t>0 and (case.parent/f'{t:g}'/'U').exists()])
if not len(times):raise SystemExit('No saved nonzero-time fields found')
def internal(data):
 if isinstance(data,vtk.vtkUnstructuredGrid): return data
 if isinstance(data,vtk.vtkMultiBlockDataSet):
  for i in range(data.GetNumberOfBlocks()):
   found=internal(data.GetBlock(i))
   if found is not None:return found
 return None
plane=vtk.vtkPlane();plane.SetOrigin(0,0,0);plane.SetNormal(0,0,1)
def get_frame(t):
 reader.UpdateTimeStep(float(t));grid=internal(reader.GetOutput());assert grid is not None
 gradient=vtk.vtkGradientFilter();gradient.SetInputData(grid);gradient.SetInputScalars(vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS,'U');gradient.ComputeVorticityOn();gradient.SetVorticityArrayName('vorticity');gradient.Update()
 cut=vtk.vtkCutter();cut.SetCutFunction(plane);cut.SetInputData(gradient.GetOutput());cut.Update();mesh=cut.GetOutput()
 coords=vtk_to_numpy(mesh.GetPoints().GetData());polys=[]
 for i in range(mesh.GetNumberOfCells()):
  cell=mesh.GetCell(i);polys.append(coords[[cell.GetPointId(j) for j in range(cell.GetNumberOfPoints())],:2])
 cd=mesh.GetCellData();u=vtk_to_numpy(cd.GetArray('U'));pressure=vtk_to_numpy(cd.GetArray('p'))*1000;omega=vtk_to_numpy(cd.GetArray('vorticity'))[:,2]
 return polys,[np.linalg.norm(u,axis=1),pressure,omega]
polys,fields=get_frame(times[-1]);meta=json.loads((r/'run.json').read_text());variant=meta.get('benchmark','fsi3').upper()
names=['velocity','pressure','vorticity'];labels=['Speed [m/s]','Pressure [Pa]','Vorticity z [1/s]'];cmaps=['viridis','coolwarm','RdBu_r']
for i,(name,label,cmap) in enumerate(zip(names,labels,cmaps)):
 fig,ax=plt.subplots(figsize=(12,4),layout='constrained');v=fields[i]
 limits=(float(v.min()),float(v.max())) if i!=2 else (-float(np.abs(v).max()),float(np.abs(v).max()))
 pc=PolyCollection(polys,array=v,cmap=cmap,edgecolors='none',clim=limits);ax.add_collection(pc);ax.set(xlim=(0,1.25),ylim=(0,.41),xlabel='x [m]',ylabel='y [m]',title=f'Turek-Hron {variant} | t = {times[-1]:g} s | {r.name}');ax.set_aspect('equal');ax.set_facecolor('#38404b');fig.colorbar(pc,ax=ax,label=label,shrink=.8);fig.savefig(out/f'{name}.png',dpi=170);plt.close(fig)
if a.animate:
 selected=times[::max(1,len(times)//80)]
 if selected[-1]!=times[-1]:selected=np.append(selected,times[-1])
 fig,ax=plt.subplots(figsize=(10,3.4),layout='constrained');p0,f0=get_frame(selected[0]);vmax=max(float(fields[0].max()),.01)
 pc=PolyCollection(p0,array=f0[0],cmap='viridis',edgecolors='none',clim=(0,vmax));ax.add_collection(pc);ax.set(xlim=(0,1.25),ylim=(0,.41),xlabel='x [m]',ylabel='y [m]');ax.set_aspect('equal');ax.set_facecolor('#38404b');title=ax.set_title('');fig.colorbar(pc,ax=ax,label='Speed [m/s]',shrink=.8)
 def update(i):
  poly,f=get_frame(selected[i]);pc.set_verts(poly);pc.set_array(f[0]);title.set_text(f'{variant} | t = {selected[i]:.2f} s | actual simulation');return pc,title
 ani=FuncAnimation(fig,update,frames=len(selected),interval=120,blit=False);ani.save(out/'velocity-animation.gif',writer=PillowWriter(fps=8),dpi=100);plt.close(fig)
(out/'field-render.json').write_text(json.dumps({'last_time_s':float(times[-1]),'saved_times':times.tolist(),'pressure_conversion':'p_Pa = 1000 * OpenFOAM kinematic p','section':'z=0, actual moving mesh','deformation_scale':1},indent=2)+'\n')
print(out)
