"""Owner product modules: 350 D / 2350 H, actual 630 corner, 360 north setback."""
import bpy,copy,hashlib,importlib.util,json,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;PARENT=HERE/'iterations'/'06-east-tv-reference-cabinets'
OUT=HERE/'iterations'/'07-product-modules-360-setback';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=PARENT/'V6-east-tv.blend';parent_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
data=json.loads((PARENT/'layouts.json').read_text(encoding='utf-8'));v=copy.deepcopy(next(iter(data['variants'].values())))
spec=importlib.util.spec_from_file_location('primitives',HERE/'generate_designs.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));g.scene=scene=bpy.context.scene
g.F=bpy.data.collections['13 | Loose furniture — family room iteration 06'];g.F.name='13 | Loose furniture — family room iteration 07';g.OUT=OUT;g.ITEMS=[]
wood=bpy.data.materials['American walnut — new furniture']
def remove(name):
    p=bpy.data.objects.get(name)
    if p:
        for o in list(p.children):bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.objects.remove(p,do_unlink=True)
for name in ('WEST STORAGE W6','BLIND CORNER / NO STORAGE CREDIT','CORNER JOIN FILLER'):remove(name)
v['items']=[i for i in v['items'] if i['name'] not in ('WEST STORAGE W6','BLIND CORNER / NO STORAGE CREDIT','CORNER JOIN FILLER')]
def rectangle(it,centre,dims,angle):
    it['centre']=list(centre);it['dims']=list(dims);it['angle']=angle;dx,dy=dims[:2];a=math.radians(angle)
    it['polygon']=[[centre[0]+x*math.cos(a)-y*math.sin(a),centre[1]+x*math.sin(a)+y*math.cos(a)] for x,y in [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,dy/2),(-dx/2,dy/2)]]

for it in v['items']:
    name=it['name'];root=bpy.data.objects.get(name)
    if name.startswith('WEST STORAGE'):
        index=int(name[-1]);cy=4.126667+.4+(index-1)*.8
        root.location=(.208333,cy,0);root.scale=(.8/.7,.35/.5,2.35/2.4)
        root['dimensions_mm']=[800,350,2350];rectangle(it,(.208333,cy),(.8,.35,2.35),90)
        it['note']='Owner-confirmed available 800 W x 350 D x 2350 H; reference front appearance, actual products/interiors/hardware not identified.'
    elif name=='RETURN STORAGE L1':
        root.location=(1.073333,3.661667,0);root.scale=(.8/.9,.35/.5,2.35/2.4)
        root['dimensions_mm']=[800,350,2350];rectangle(it,(1.073333,3.661667),(.8,.35,2.35),180)
        it['note']='800 W x 350 D x 2350 H return, 10 mm after corner footprint; ends 60 mm before backing wall endpoint.'
    elif name.startswith('NEW girls walnut'):
        root.scale.z=2.35/2.4;root['dimensions_mm']=[round(it['dims'][0]*1000),400,2350];it['dims'][2]=2.35
        it['note']=it['note'].replace('2400 H','2350 H')+' Height 2350 owner-confirmed; 400 D still provisional.'

# Actual owner-supplied 630 x 630 corner replaces the uncounted blind corner.
corner=g.group('L CORNER 630 x 630 OPEN','living',(.348333,3.801667),(.63,.63,2.35),colour='#926b4b',purpose='storage',note='630 x 630 footprint and 2350 H confirmed by owner/photo. L shelf contour / 350 mm legs and staggered end panels illustrative, not product drawings.')
g.box('Corner west back',(-.306,0,1.175),(.018,.63,2.35),wood,.004,corner)
g.box('Corner south back',(0,-.306,1.175),(.63,.018,2.35),wood,.004,corner)
poly=[(-.315,-.315),(.315,-.315),(.315,.035),(.035,.035),(.035,.315),(-.315,.315)]
def l_shelf(z):
    # Exact bounding reservation; internal L contour remains provisional.
    verts=[(x,y,z+dz) for dz in (-.009,.009) for x,y in poly];n=len(poly)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new('L shelf mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new('Corner L shelf',mesh);g.F.objects.link(o);o.parent=corner;o.data.materials.append(wood)
    bevel=o.modifiers.new('Shelf rounded edge','BEVEL');bevel.width=.003;bevel.segments=2
for i in range(8):l_shelf(.009+i*(2.332/7))
for i in range(7):
    z=.018+(i+.5)*(2.314/7)
    if i%2==0:g.box('Corner alternating north panel',(-.14,.306,z),(.35,.018,2.314/7-.018),wood,.004,corner)
    else:g.box('Corner alternating east panel',(.306,-.14,z),(.018,.35,2.314/7-.018),wood,.004,corner)
v['items'].extend(g.ITEMS)
v['checks'].update({'living_main_storage_widths_mm':[800]*5,'living_return_width_mm':800,'living_tall_storage_height_mm':2350,
    'living_straight_depth_mm':350,'living_north_setback_mm':360,'north_beam_plan_gap_mm':200,
    'corner_footprint_mm':[630,630],'corner_height_mm':2350,'south_gap_mm':40,'corner_to_main_gap_mm':10,
    'l_return_wall_end_gap_mm':60,'sofa_back_to_west_cabinet_front_mm':807})
v['storage'].update({'new_living_main_modules':5,'new_living_return_modules':1,'new_living_open_corner_modules':1,
    'living_storage_height_mm':2350,'girls_new_height_mm':2350,
    'status':'Product widths/depth/height applied; corner now real open unit, not blind void. All retained contents allocated; actual usable interior/content fit unresolved.'})
v['storage'].pop('blind_corner_capacity_credit_l',None)
data.update({'revision':7,'parent':'06-east-tv-reference-cabinets/V6-east-tv','parent_sha256':parent_hash,
    'variants':{'V7-product-modules':v},'feasibility_status':'Conditional on product/site/content and girls night-access checks. Five 800 mm modules + 630 corner meet owner 360 mm north setback; rear sofa gap about 807 mm.'})
data['latest_owner_decisions'].extend(['Living straight units available in 800/900 W, 350 D, 2350 H; corner 630 x 630 x 2350 H.','Girls cabinet height also 2350 mm.','Living north setback must be 360 mm.'])
data['assumptions']=[s for s in data['assumptions'] if not any(t in s for t in ('six 700','2400','Blind corner','blind corner','657','307','200 mm strip','200 mm short','Girls nominal'))]
data['assumptions'].extend(['Living wall chain in mm: 40 south gap + 630 corner + 10 join + 5x800 cabinets + 360 north setback = 5040.',
    'A 900+4x800 west run would exceed the available length by 100 mm with these gaps; five 800 units used.',
    'Return: 630 corner + 10 join + 800 cabinet, with 33 mm west offset and 60 mm at east wall end. No wall overhang.',
    'Corner full 630x630 envelope reserved. Image-based L shelf contour, leg depth and alternating partitions are illustrative; actual connector and shelf drawing unverified.',
    'Living straight dimensions 800 W x 350 D x 2350 H owner confirmed. Girls 800/800/600 W x 2350 H; 400 mm depth remains provisional.',
    'Behind sofa about 807 mm to closed straight cabinet fronts; 800 mm pair doors need 400 mm leaves, leaving about 407 mm when open. Comfort/sequential access remains unresolved.',
    '77-inch visible TV and 3180 mm seated-eye distance retained exactly. TV console remains a separately assumed 2000 W x 450 D carcass x 550 H proxy.',
    'Girls exact 2200 mm run has zero spare fitting tolerance; door/drawer access with trundle open remains restricted. No server.'])
scene['design_version']='Version 7 / owner product modules / 360 mm north setback / east 77-inch TV / no server'
scene['feasibility_status']=data['feasibility_status'];scene['new_girls_cabinet_dimensions']='800/800/600 W x 2350 H; 400 D provisional'
scene.camera=bpy.data.objects['DESIGN living from entry'];bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'V7-product-modules.blend'))
(OUT/'layouts.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
for cam,name in [('DESIGN V6 east TV wall','V7-east-tv-wall'),('DESIGN V6 seated eye 3180 mm','V7-seated-view'),
    ('DESIGN living storage wall','V7-west-storage'),('DESIGN L corner from living','V7-l-corner'),
    ('DESIGN V6 girls full cabinet run','V7-girls-cabinets')]:g.render(bpy.data.objects[cam],name)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==parent_hash
print('REVISION07_COMPLETE',OUT,flush=True)
