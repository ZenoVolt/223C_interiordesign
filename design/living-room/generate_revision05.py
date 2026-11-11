"""Version 5: full west storage, 2400 mm high; L-return and no TV.

Run in Blender background. Preserves shell and versions 3/4. Optional --no-render.
"""
import bpy, copy, hashlib, importlib.util, json, math, sys
from pathlib import Path
from mathutils import Vector

HERE=Path(__file__).resolve().parent
PARENT=HERE/'iterations'/'04-west-tv-three-walnut-cabinets'
OUT=HERE/'iterations'/'05-full-west-storage-l-return'
OUT.mkdir(parents=True,exist_ok=True)
BASE=HERE.parents[1]/'model'/'223C_Existing_Shell_v02.blend'
protected={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE,*PARENT.glob('*.blend'))}
data=json.loads((PARENT/'layouts.json').read_text(encoding='utf-8'))
v=copy.deepcopy(data['variants']['A-with-tv'])
spec=importlib.util.spec_from_file_location('primitives',HERE/'generate_designs.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
bpy.ops.wm.open_mainfile(filepath=str(PARENT/'A-with-tv.blend'))
g.scene=scene=bpy.context.scene
g.F=bpy.data.collections['13 | Loose furniture — family room iteration 04']
g.F.name='13 | Loose furniture — family room iteration 05'
g.OUT=OUT;g.ITEMS=[]
g.M={'oak':bpy.data.materials['American walnut — new furniture'],
     'cream':bpy.data.materials['American walnut — new furniture'],
     'dark':bpy.data.materials['dark']}

# Remove the screen and short media/archive units; retain their contents allocation.
removed=[it['name'] for it in v['items'] if it['purpose']=='screen' or (it['room']=='living' and it['purpose']=='storage')]
for name in removed:
    root=bpy.data.objects[name]
    for child in list(root.children):bpy.data.objects.remove(child,do_unlink=True)
    bpy.data.objects.remove(root,do_unlink=True)
v['items']=[it for it in v['items'] if it['name'] not in removed]
for o in [o for o in list(g.F.objects) if o.name.startswith('Book on cupboard')]:
    bpy.data.objects.remove(o,do_unlink=True)

# New height direction applies to all new wood storage; preserve widths/depths.
for it in v['items']:
    if not it['name'].startswith('NEW girls walnut'):continue
    root=bpy.data.objects[it['name']]
    for o in root.children:
        o.location.z*=1.2;o.scale.z*=1.2
    root['dimensions_mm']=[round(it['dims'][0]*1000),400,2400]
    it['dims'][2]=2.4
    root['assumption']='Widths and 2400 H owner direction; 400 D provisional; actual site and contents fit unresolved.'
    it['note']=root['assumption']

def normalize_depth(root,depth):
    meshes=[o for o in root.children if o.type=='MESH']
    lo=min(o.location.y+v.co.y for o in meshes for v in o.data.vertices)
    hi=max(o.location.y+v.co.y for o in meshes for v in o.data.vertices)
    factor=depth/(hi-lo)
    for o in meshes:o.location.y=(o.location.y-lo)*factor-depth/2;o.scale.y*=factor

# Six independent 700 mm modules along west, not a built-in carcass.
# Reserve 200 mm north strip: B01 projects 160 mm and is only 2255 mm high.
start=4.086667
for i in range(6):
    root=g.cabinet(f'WEST STORAGE W{i+1}', 'living', .283333, start+.35+i*.7, .7,.5,2.4,angle=90)
    root['assumption']='Freestanding walnut 700 W x 500 D x 2400 H proxy; product interior/load/restraint details unverified.'
    if i==0:
        # Open NAS bay preserves access/ventilation; closed storage above.
        for o in list(root.children):
            if ' door ' in o.name or ' handle' in o.name:bpy.data.objects.remove(o,do_unlink=True)
        for j in range(2):
            x=(-.25 if j==0 else .25)*.7
            g.box('W1 upper door '+str(j),(x,-.241,1.51),(.338,.025,1.66),g.M['oak'],.006,root)
            hx=x+(.175-.045)*(1 if j==0 else -1)
            g.box('W1 upper handle',(hx,-.268,1.40),(.012,.028,.16),g.M['dark'],.005,root)
        g.box('W1 equipment bay shelf',(0,0,.65),(.652,.43,.03),g.M['oak'],.006,root)
    normalize_depth(root,.5)
    for z in ((1.1,1.6,2.1) if i==0 else (.48,.94,1.4,1.86)):
        g.box(f'W{i+1} provisional shelf',(0,0,z),(.652,.43,.024),g.M['oak'],.004,root)
    g.ITEMS[-1]['note']=root['assumption']
    g.ITEMS[-1]['colour']='#926b4b'

# Wrap only 900 mm onto the maid-room north wall, ending 50 mm before its east end.
root=g.cabinet('RETURN STORAGE L1','living',1.033333,3.736667,.9,.5,2.4,angle=180)
normalize_depth(root,.5)
for z in (.48,.94,1.4,1.86):g.box('L1 provisional shelf',(0,0,z),(.852,.43,.024),g.M['oak'],.004,root)
g.ITEMS[-1]['colour']='#926b4b'
g.ITEMS[-1]['note']='900 W x 500 D x 2400 H loose return; terminates 50 mm before wall end. Blind corner excluded from capacity.'

# Explicit blind corner: no shelves, doors, contents or counted storage volume.
corner=g.group('BLIND CORNER / NO STORAGE CREDIT','living',(.283333,3.786667),(.5,.6,2.4),colour='#d8c4ac',purpose='corner_void',note='Deliberately uncounted void behind perpendicular modules; removable top cover, no assumed contents access.')
g.box('Removable blind-corner top', (0,0,2.385),(.5,.6,.03),g.M['oak'],.004,corner)
filler=g.group('CORNER JOIN FILLER','living',(.558333,4.036667),(.05,.1,2.4),colour='#926b4b',purpose='filler')
g.box('Corner join infill',(0,0,1.2),(.05,.1,2.4),g.M['oak'],.004,filler)
v['items'].extend(g.ITEMS)

# Retain R6 orientation: its 543 mm depth already runs along the west wall.
nas=bpy.data.objects['RETAINED R6 NAS']
nas.location=(.283333,4.436667,.1);nas.rotation_euler.z=0
for it in v['items']:
    if it['name']=='RETAINED R6 NAS':
        it['centre']=[.283333,4.436667];it['angle']=0;it['purpose']='equipment_in_bay'
        it['polygon']=[[.166833,4.165167],[.399833,4.165167],[.399833,4.708167],[.166833,4.708167]]
        it['note']='R6 original orientation: 543 mm along wall, 233 mm projecting into room; body elevated 100 mm in open W1 bay. Cable/airflow and restraint details unresolved.'

# Face-to-face seating for a TV-free family room; keep useful floor play clear.
chair=bpy.data.objects['RETAINED RECLINER proxy'];chair.location.x=1.95;chair.rotation_euler.z=math.radians(-28)
stool=bpy.data.objects['RETAINED FOOTSTOOL proxy'];stool.location.x=2.72;stool.location.y=7.43;stool.rotation_euler.z=math.radians(-28)
for it in v['items']:
    if it['name'] not in ('RETAINED RECLINER proxy','RETAINED FOOTSTOOL proxy'):continue
    root=chair if 'RECLINER' in it['name'] else stool
    it['centre']=[root.location.x,root.location.y];it['angle']=-28
    dx,dy=it['dims'][:2];ang=math.radians(-28)
    it['polygon']=[[root.location.x+x*math.cos(ang)-y*math.sin(ang),root.location.y+x*math.sin(ang)+y*math.cos(ang)] for x,y in [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,dy/2),(-dx/2,dy/2)]]

v['checks'].update({'living_main_storage_widths_mm':[700]*6,'living_return_width_mm':900,
    'living_tall_storage_height_mm':2400,'living_north_setback_mm':200,'north_beam_projection_mm':160,
    'north_beam_underside_mm':2255,'north_beam_plan_gap_mm':40,'l_return_wall_end_gap_mm':50})
v['storage'].update({'new_living_main_modules':6,'new_living_return_modules':1,
    'living_storage_height_mm':2400,'blind_corner_capacity_credit_l':0,
    'girls_new_height_mm':2400,
    'status':'Three full cupboard content groups and 21 box contents remain allocated; new west run holds toys/study archive with upper reserve. Blind corner excluded. Actual interior/content fit unresolved.'})
for key in ('new_living_toy_inner_envelope_l','new_living_archive_inner_envelope_l','girls_new_inner_envelope_before_shelves_l'):
    v['storage'].pop(key,None)
data.update({'revision':5,'parent':'04-west-tv-three-walnut-cabinets/A-with-tv',
    'baseline_sha256':protected[BASE],'variants':{'V5-no-tv':v},
    'feasibility_status':'Conditional on site/product/storage checks. Full west storage stops 200 mm short of north wall to clear low beam; blind L-corner excluded; girls night cabinet restriction persists.',
    'assumptions':[
        'Owner version 5: full living west-side storage, remove TV, consider L-wall, cabinets 2400 mm tall.',
        '2400 mm height applied to living and new girls wood cabinets; girls widths 800/800/600 and provisional 400 mm depth retained.',
        'L-wall interpreted as west wall turning east onto maid-room north wall; no wall alteration.',
        'Main west run six 700 W x 500 D x 2400 H loose modules; 900 W return. Module widths/depths provisional.',
        'North wall beam underside 2255 mm in source model (drop assumed); its 160 mm projection prevents 2400 mm tall cabinets extending literally to north wall. Reserve 200 mm strip, leaving 40 mm plan separation.',
        'Blind corner deliberately inaccessible and uncounted; avoid claiming hidden usable capacity. Return stops 50 mm before wall end, clear of maid door zone.',
        'R6 in open lower W1 bay, original orientation with 543 mm along wall / 233 mm projecting into room. Exact port positions, cable service and ventilation remain to verify.',
        'Freestanding modular proposal within loose-furniture scope. No built-in, power, lighting or wall changes authorized; tall-unit support/restraint remains product/site-specific.',
        'Girls nominal 2200 mm run has zero spare fitting tolerance; full hinged-door opening still needs trundle stored.',
        'All retained contents allocated; actual shelf capacity and load not established. No product sourcing or budget total.']})

scene['design_version']='version05 full west storage / L return / no TV'
scene['feasibility_status']=data['feasibility_status']
scene['new_girls_cabinet_dimensions']='800/800/600 W x 2400 H owner direction; 400 D provisional'
entry=bpy.data.objects['DESIGN living from entry']
wallcam=bpy.data.objects['DESIGN living storage wall']
wallcam.location=(4.65,5.30,1.60)
wallcam.rotation_euler=(Vector((.3,6.1,1.22))-wallcam.location).to_track_quat('-Z','Y').to_euler()
lcam=g.camera('DESIGN L corner from entry',(2.85,2.85,1.62),(.4,4.3,1.2),25)
cornercam=g.camera('DESIGN L corner from living',(2.85,5.7,1.65),(.65,3.9,1.15),25)
scene.camera=entry;scene.cycles.samples=40
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'V5-no-tv.blend'))
(OUT/'layouts.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
if '--no-render' not in sys.argv:
    for cam,name in [(entry,'V5-living-entry'),(wallcam,'V5-west-storage'),
        (bpy.data.objects['DESIGN living towards seating'],'V5-living-seating'),
        (lcam,'V5-l-return-entry'),(cornercam,'V5-l-return-living'),
        (bpy.data.objects['DESIGN girls wardrobe and west cupboards'],'girls-storage'),
        (bpy.data.objects['DESIGN girls day'],'girls-day')]:g.render(cam,name)
    trundle=bpy.data.objects['PULL-OUT lower mattress'];trundle.location.x-=.95
    g.render(bpy.data.objects['DESIGN girls day'],'girls-night');trundle.location.x+=.95
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in protected.items())
print('VERSION05_COMPLETE',OUT,flush=True)
