"""Add walnut-framed vertical reeded glass to version 5, preserving solid-door file."""
import bpy, hashlib, importlib.util, json, math
from pathlib import Path
from mathutils import Vector

HERE=Path(__file__).resolve().parent
OUT=HERE/'iterations'/'05-full-west-storage-l-return'
SOURCE=OUT/'V5-no-tv.blend'
before=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('primitives',HERE/'generate_designs.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
g.scene=scene=bpy.context.scene
g.F=bpy.data.collections['13 | Loose furniture — family room iteration 05'];g.OUT=OUT
walnut=bpy.data.materials['American walnut — new furniture']
glass=g.mat('Vertical reeded glass — illustrative 12 mm pitch',(.78,.84,.79),.20)
bs=glass.node_tree.nodes.get('Principled BSDF')
bs.inputs['Transmission Weight'].default_value=1
bs.inputs['IOR'].default_value=1.46
bs.inputs['Coat Weight'].default_value=.08
glass['assumption']='Illustrative clear/reeded transmission with 12 mm pitch; sample, thickness, tempering and hardware not selected.'
linen=g.mat('Illustrative closed linen boxes',(.42,.40,.32),.85)
bookmats=[g.mat('Illustrative book '+str(i),c,.8) for i,c in enumerate([(.10,.15,.13),(.28,.13,.08),(.43,.39,.28)])]

def reeded_panel(name,x0,x1,y0,y1,z0,z1,parent):
    # Actual rounded vertical flutes, with a flat rear surface. Stays in old leaf envelope.
    nx=max(24,math.ceil((x1-x0)/.002));verts=[]
    for i in range(nx+1):
        x=x0+(x1-x0)*i/nx
        front=y0+.004-.002*math.cos(2*math.pi*(x-x0)/.012)
        back=min(y1-.002,y0+.013)
        verts.extend([(x,front,z0),(x,front,z1),(x,back,z0),(x,back,z1)])
    faces=[]
    for i in range(nx):
        a=4*i;b=4*(i+1)
        faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                      (a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
    faces.extend([(0,2,3,1),(4*nx,4*nx+1,4*nx+3,4*nx+2)])
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);g.F.objects.link(o);o.parent=parent;o.data.materials.append(glass)
    for polygon in mesh.polygons:polygon.use_smooth=polygon.index<4*nx and polygon.index%4==0
    o['style']='vertical reeded glass, illustrative'
    return o

roots=[o for o in g.F.objects if o.type=='EMPTY' and o.name.startswith(('WEST STORAGE','RETURN STORAGE','NEW girls walnut'))]
count=0
for root in roots:
    doors=[o for o in list(root.children) if ' door ' in o.name or 'upper door ' in o.name]
    for door in doors:
        pts=[door.matrix_basis@v.co for v in door.data.vertices]
        x0,y0,z0=[min(v[i] for v in pts) for i in range(3)]
        x1,y1,z1=[max(v[i] for v in pts) for i in range(3)]
        name=door.name;w=x1-x0;h=z1-z0;th=y1-y0
        bpy.data.objects.remove(door,do_unlink=True)
        stile=.05;rail=.04
        for xx in (x0+stile/2,x1-stile/2):
            g.box(name+' walnut stile',(xx,(y0+y1)/2,(z0+z1)/2),(stile,th,h),walnut,.004,root)
        for zz in (z0+rail/2,z1-rail/2):
            g.box(name+' walnut rail',((x0+x1)/2,(y0+y1)/2,zz),(w-2*stile,th,rail),walnut,.004,root)
        reeded_panel(name+' REEDED GLASS',x0+stile,x1-stile,y0,y1,z0+rail,z1-rail,root)
        count+=1
    # Contents here are visual cues for transparency, not a claimed packing solution.
    if root.name.startswith('WEST STORAGE'):
        index=int(root.name[-1])
        if index==1:levels=(1.25,1.77,2.2)
        else:levels=(.26,.69,1.15,1.61,2.07)
        for j,z in enumerate(levels):
            for xx in (-.16,.16):
                if index in (2,3,4):g.box('ILLUSTRATIVE bin '+root.name,(xx,-.015,z),(.27,.32,.28),linen,.012,root)
                else:
                    for k in range(3):g.box('ILLUSTRATIVE books '+root.name,(xx-.07+k*.055,-.015,z),(.045,.24,.24+.025*(k%2)),bookmats[(j+k)%3],.002,root)
    elif root.name.startswith('NEW girls walnut'):
        width=root['dimensions_mm'][0]/1000
        for z in (.28,.82,1.36,1.90):
            for xx in (-width*.23,width*.23):g.box('ILLUSTRATIVE girls bin',(xx,-.01,z),(width*.4,.27,.26),linen,.012,root)
    else:
        for z in (.26,.69,1.15,1.61,2.07):
            for xx in (-.22,.22):g.box('ILLUSTRATIVE return bin',(xx,-.01,z),(.36,.32,.28),linen,.012,root)
scene['door_style']='Walnut frames with vertical reeded-glass panels in living + girls new cabinets. Solid version retained.'
scene['contents_visualisation']='Illustrative bins/books only; actual retained-content fit not established.'
scene.cycles.samples=64;scene.cycles.max_bounces=12;scene.cycles.transmission_bounces=10
scene.camera=bpy.data.objects['DESIGN living from entry']
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'V5-reeded-glass.blend'))
data=json.loads((OUT/'layouts.json').read_text(encoding='utf-8'))
data['front_style']='American walnut frames / vertical reeded-glass panels'
data['solid_door_parent_sha256']=before
data['illustrative_contents_only']=True
(OUT/'layouts-reeded.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
for cam,name in [('DESIGN living storage wall','V5-reeded-west-storage'),
                 ('DESIGN L corner from living','V5-reeded-l-return'),
                 ('DESIGN living from entry','V5-reeded-living-entry'),
                 ('DESIGN girls wardrobe and west cupboards','girls-reeded-storage')]:
    g.render(bpy.data.objects[cam],name)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==before
report={'new_cabinets':len(roots),'reeded_glass_leaves':count,'solid_version_preserved':True,
    'footprints_and_heights':'Unchanged from audited version 5; glazing stays within prior leaf bounds.',
    'unresolved':'Glass sample/privacy, suitable safety glazing and hinge/frame construction are product decisions; actual contents/loads unverified.'}
(OUT/'reeded-glass-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('REEDED_GLASS_COMPLETE',report,flush=True)
