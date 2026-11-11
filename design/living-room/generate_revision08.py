"""V8: 3x900 east storage, centred west TV/2.59m console/KEF Q11 Meta pair."""
import bpy,copy,hashlib,importlib.util,json,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;PARENT=HERE/'iterations'/'07-product-modules-360-setback'
OUT=HERE/'iterations'/'08-west-av-east-storage';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=PARENT/'V7-product-modules.blend';parent_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
data=json.loads((PARENT/'layouts.json').read_text(encoding='utf-8'));v=copy.deepcopy(next(iter(data['variants'].values())))
spec=importlib.util.spec_from_file_location('primitives',HERE/'generate_designs.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));g.scene=scene=bpy.context.scene
g.F=bpy.data.collections['13 | Loose furniture — family room iteration 07'];g.F.name='13 | Loose furniture — family room iteration 08';g.OUT=OUT;g.ITEMS=[]
wood=bpy.data.materials['American walnut — new furniture'];dark=bpy.data.materials['dark']
cone=g.mat('Q11 driver graphite — proxy',(.045,.047,.043),.38,.30)
rim=g.mat('Q11 Uni-Q aluminium — proxy',(.28,.24,.15),.34,.6)

def rectangle(it,centre,dims,angle):
    it.update({'centre':list(centre),'dims':list(dims),'angle':angle});dx,dy=dims[:2];a=math.radians(angle)
    it['polygon']=[[centre[0]+x*math.cos(a)-y*math.sin(a),centre[1]+x*math.sin(a)+y*math.cos(a)] for x,y in [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,dy/2),(-dx/2,dy/2)]]
def place(name,centre,angle,new_name=None,dims=None):
    root=bpy.data.objects[name];root.location.x,root.location.y=centre;root.rotation_euler.z=math.radians(angle)
    it=next(i for i in v['items'] if i['name']==name)
    rectangle(it,centre,dims or it['dims'],angle)
    if new_name:root.name=new_name;it['name']=new_name
    root['dimensions_mm']=[round(x*1000) for x in it['dims']]
    return root,it
def remove(name):
    root=bpy.data.objects[name]
    for o in list(root.children):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.objects.remove(root,do_unlink=True)
    v['items'][:]=[i for i in v['items'] if i['name']!=name]
for name in ('WEST STORAGE W4','WEST STORAGE W5','RETURN STORAGE L1','L CORNER 630 x 630 OPEN'):remove(name)

# South bias is needed: the north beam makes a centred 2700 mm tall run collide.
for i in range(3):
    root,it=place(f'WEST STORAGE W{i+1}',(4.865,6.04+i*.9),-90,f'EAST STORAGE E{i+1}',(.9,.35,2.35))
    root.scale.x*=.9/.8
    it['note']='900 W x 350 D x 2350 H, owner product range; quantity three is current layout hypothesis. y=5.59..8.29 clears north beam.'

# All west AV components share the midpoint of the full 5040 mm wall.
cy=(3.446667+8.486667)/2
width_outer=next(i for i in v['items'] if i['purpose']=='screen')['dims'][1]
console_width=width_outer*1.5
console,it=place('EAST TV CONSOLE 2000 x 450 x 550',(.265,cy),90,'WEST TV CONSOLE ratio 3-to-2',(console_width,.469,.55))
console.scale.x=console_width/2
# Actual console includes 19 mm pull projection beyond its 450 mm carcass.
it['polygon']=[[.04,cy-console_width/2],[.509,cy-console_width/2],[.509,cy+console_width/2],[.04,cy+console_width/2]]
it['note']='Physical TV outer width is 2/3 console width; approx 2590 W. 450 D carcass +19 pull, 550 H provisional; freestanding walnut.'
tv,it=place('TV 77-inch 16-by-9 PROXY',(.070333,cy),180)
it['polygon']=[[.042833,cy-width_outer/2],[.318333,cy-width_outer/2],[.318333,cy+width_outer/2],[.042833,cy+width_outer/2]]
it['note']='77-inch visible 16:9 display; physical bezel-inclusive width sets 2/3 console ratio. Now on west, no wall mounting.'
screen_x=.103333;eye=(screen_x+3.18,cy,1.12)
place('SOFA 2500 x 1000',(eye[0]+.10,cy),180)
place('RETAINED RECLINER proxy',(2.10,7.78),-145)
place('RETAINED FOOTSTOOL proxy',(1.39,7.28),-145)
place('SMALL SIDE TABLE',(3.45,7.65),0)
v['play_rect']=[1.05,4.78,2.65,6.65]
a,b,c,d=v['play_rect'];rug=bpy.data.objects['Loose washable play rug'];rug.location=((a+c)/2,(b+d)/2,.012);rug.dimensions=(c-a,d-b,.018)
for i,o in enumerate(sorted((o for o in g.F.objects if o.name.startswith('Loose play block')),key=lambda o:o.name)):
    o.location=(a+.3+.16*(i%3),b+.3+.16*(i//3),.07)

def speaker(name,y,angle):
    # Verified manufacturer terminal/plinth envelope, not invented body-only footprint.
    p=g.group(name,'living',(.515,y),(.380,.317,1.112),angle,colour='#6e543b',purpose='speaker',note='KEF Q11 Meta: 1112 H x 317 W x 380 D including terminals/plinth. Body styling and driver positions illustrative; walnut provisional.')
    g.box(name+' plinth',(0,0,.038),(.380,.317,.026),dark,.008,p)
    for x in (-.145,.145):
        for yy in (-.125,.125):g.cylinder(name+' rubber foot',(x,yy,.014),.012,.028,dark,p)
    g.box(name+' walnut body',(.0075,0,.5815),(.335,.210,1.061),wood,.006,p)
    g.box(name+' front baffle',(.175,0,.5815),(.007,.207,1.047),dark,.004,p)
    g.box(name+' rear terminals',(-.180,0,.20),(.020,.075,.11),dark,.003,p)
    for j,z in enumerate((.910,.695,.475,.255)):
        rad=.052 if j==0 else .0825
        o=g.cylinder(name+' driver rim '+str(j),(.182,0,z),rad,.008,rim if j==0 else dark,p);o.rotation_euler.y=math.pi/2
        o=g.cylinder(name+' diaphragm '+str(j),(.185,0,z),rad*.88,.004,cone,p);o.rotation_euler.y=math.pi/2
        o=g.cylinder(name+' driver centre '+str(j),(.187,0,z),.0095 if j==0 else .025,.004,rim if j==0 else dark,p);o.rotation_euler.y=math.pi/2
    return p
speaker('KEF Q11 Meta SOUTH',cy-1.60,10)
speaker('KEF Q11 Meta NORTH',cy+1.60,-10)
v['items'].extend(g.ITEMS)
v['viewing'].update({'screen_front_x_m':screen_x,'screen_centre_y_m':cy,'seated_eye_m':list(eye),
    'physical_tv_outer_width_mm':width_outer*1000,'console_width_mm':console_width*1000,
    'physical_tv_to_console_width_ratio':2/3,'horizontal_eye_to_screen_mm':3180})
v['audio']={'speaker':'KEF Q11 Meta','source':'https://international.kef.com/products/q11-meta',
    'manual':'https://images.salsify.com/image/upload/s--oYdpVA3V--/ebnntv3ljqcad5t2iefe.pdf',
    'checked_date_sg':'2026-11-10','manufacturer_hwd_with_terminal_plinth_mm':[1112,317,380],
    'west_wall_midpoint_y_m':cy,'speaker_centres_y_m':[cy-1.6,cy+1.6],'speaker_centre_separation_mm':3200,
    'toe_in_deg':10,'placement_status':'Provisional starting positions; approx 300 mm bounding-envelope rear clearance. No measured room acoustic result.'}
v['checks']={'east_storage_widths_mm':[900,900,900],'east_storage_depth_mm':350,'east_storage_height_mm':2350,
    'east_storage_y_bounds':[5.59,8.29],'east_storage_to_north_beam_mm':36.667,
    'sofa_back_to_east_storage_front_mm':807,'door_leaf_assumed_mm':450,'remaining_gap_with_leaf_open_mm':357,
    'west_wall_centre_y_m':cy,'play_area_m2':round((c-a)*(d-b),3)}
v['storage'].update({'new_living_main_modules':3,'new_living_return_modules':0,'new_living_open_corner_modules':0,
    'living_tall_straight_frontage_mm':2700,'status':'Capacity reopened: 2700 mm tall east storage replaces 4800 mm straight storage plus corner. 21 box contents remain required; actual fit/overflow unresolved. Console is additional low storage, not automatic replacement capacity.'})
data.update({'revision':8,'parent':'07-product-modules-360-setback/V7-product-modules','parent_sha256':parent_hash,
    'variants':{'V8-west-av':v},'feasibility_status':'Conditional. West AV centred, 77-inch / 3180 eye distance and 2/3 physical TV-to-console ratio set. East 3x900 hypothesis fits model; capacity/acoustics/product/site/bed-state access unresolved.'})
data['latest_owner_decisions']=['New version: east living wall storage, approximately 3 x 900 mm.',
    'West wall: large console, TV 2/3 console width, 77-inch TV and KEF Q11 Meta speaker pair, centred on wall.',
    'Retain 3180 mm viewing distance; no server and girls/study retained.']
data['assumptions']=[
    'TV 2/3 console size interpreted as bezel-inclusive physical width, not diagonal or area. TV proxy 1726.63 W gives 2589.94 mm console. Actual product bezel/console details unresolved.',
    'West AV axis is midpoint y=5.966667 of full existing 5040 mm west wall, not shortened by prior corner furniture. Speaker centres ±1600 mm, 10 degree toe-in provisional.',
    'East 3x900 x350 D x2350 H is a proposal, not accepted capacity. Run starts y5.59 and ends8.29 so all high cabinets clear low north beam by ~37 mm in plan.',
    'Prior 360 mm west cabinet north setback is not transferred to east storage. All west AV components leave over 700 mm to north/south wall endpoints; tall east units clear the north beam.',
    'New storage is 2700 straight frontage versus previous 4800 plus open corner; no purge, overflow destination or capacity pass assumed. Repacking 21 box contents allowed.',
    'Girls 800/800/600 x2350 H unchanged, 400 depth provisional, exact 2200 wall zero fitting tolerance and night access restrictions remain. Study and fixed wardrobe unchanged.',
    'Retained recliner/footstool and sofa are proxies, including eye offset100 mm and eye height1120. Actual recline/window access, guest setup and household clearance comfort unresolved.',
    'Speaker envelope from KEF official specs, finish/walnut material and driver positions approximate. Toe-in and rear room allowance are planning choices, not an acoustic approval.',
    'Amplifier/streaming hardware, cable routing, west AV electrical outlets and room tuning unverified. No wiring, built-in, ceiling or wall alteration assumed.'
]
scene['design_version']='Version 8 / east 3x900 storage / centred west 77 TV + KEF Q11 Meta / 3180 viewing'
scene['feasibility_status']=data['feasibility_status']
eye_cam=g.camera('DESIGN V8 seated eye 3180 mm',eye,(screen_x,cy,v['viewing']['screen_centre_z_m']),28)
av_cam=g.camera('DESIGN V8 west centred AV',(3.92,cy,1.60),(.23,cy,1.05),23)
storage_cam=g.camera('DESIGN V8 east storage',(2.0,8.00,1.6),(4.85,6.94,1.25),23)
scene.camera=bpy.data.objects['DESIGN living from entry'];bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'V8-west-av-east-storage.blend'))
(OUT/'layouts.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
if '--no-render' not in __import__('sys').argv:
    for cam,name in [(scene.camera,'V8-entry'),(av_cam,'V8-west-av'),(eye_cam,'V8-seated-view'),(storage_cam,'V8-east-storage')]:g.render(cam,name)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==parent_hash
print('REVISION08_COMPLETE',OUT,flush=True)
