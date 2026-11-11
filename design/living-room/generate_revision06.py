"""East 77-inch TV / 3180 mm assumed seated-eye distance; reference cabinetry retained."""
import bpy,copy,hashlib,importlib.util,json,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;PARENT=HERE/'iterations'/'05-full-west-storage-l-return'
OUT=HERE/'iterations'/'06-east-tv-reference-cabinets';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=PARENT/'V5-reference-cabinets.blend';parent_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
data=json.loads((PARENT/'layouts-reference.json').read_text(encoding='utf-8'));v=copy.deepcopy(next(iter(data['variants'].values())))
spec=importlib.util.spec_from_file_location('primitives',HERE/'generate_designs.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));g.scene=scene=bpy.context.scene
g.F=bpy.data.collections['13 | Loose furniture — family room iteration 05'];g.F.name='13 | Loose furniture — family room iteration 06';g.OUT=OUT;g.ITEMS=[]
wood=bpy.data.materials['American walnut — new furniture'];brass=bpy.data.materials['Reference hardware — satin brass'];dark=bpy.data.materials['dark'];screen=bpy.data.materials['screen']
def place(name,xy,angle):
    root=bpy.data.objects[name];root.location.x,root.location.y=xy;root.rotation_euler.z=math.radians(angle)
    it=next(i for i in v['items'] if i['name']==name);it['centre']=list(xy);it['angle']=angle
    dx,dy=it['dims'][:2];a=math.radians(angle)
    it['polygon']=[[xy[0]+x*math.cos(a)-y*math.sin(a),xy[1]+x*math.sin(a)+y*math.cos(a)] for x,y in [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,dy/2),(-dx/2,dy/2)]]

screen_x=4.970;view_distance=3.180;eye=(screen_x-view_distance,6.95,1.12)
place('SOFA 2500 x 1000',(eye[0]-.10,6.95),0)
place('RETAINED RECLINER proxy',(3.0,4.95),48)
place('RETAINED FOOTSTOOL proxy',(3.58,5.58),48)
place('SMALL SIDE TABLE',(2.65,8.22),0)
v['play_rect']=[2.40,6.25,4.25,8.0]
a,b,c,d=v['play_rect'];rug=bpy.data.objects['Loose washable play rug'];rug.location=((a+c)/2,(b+d)/2,.012);rug.dimensions=(c-a,d-b,.018)
for i,o in enumerate(sorted((o for o in g.F.objects if o.name.startswith('Loose play block')),key=lambda o:o.name)):
    o.location=(a+.35+.16*(i%3),b+.35+.16*(i//3),.07)

# Low loose console fits entirely inside east backing wall y=5.55..8.486667.
root=g.group('EAST TV CONSOLE 2000 x 450 x 550','living',(4.808333,6.95),(2,.45,.55),angle=-90,colour='#926b4b',purpose='storage',note='Provisional 2000 W x 450 D x 550 H freestanding walnut console, solid drawer fronts echo cabinet bases.')
g.box('Console back',(0,.213,.275),(2,.024,.55),wood,.005,root)
for x in (-.988,.988):g.box('Console side',(x,0,.275),(.024,.45,.55),wood,.005,root)
for z in (.06,.535):g.box('Console base/top',(0,0,z),(2,.45,.03),wood,.005,root)
for i in range(3):
    x=(i-1)*2/3
    g.box('Console walnut drawer '+str(i),(x,-.207,.30),(2/3-.018,.024,.43),wood,.006,root)
    g.box('Console brass pull '+str(i),(x,-.235,.30),(.10,.018,.012),brass,.004,root)

# 77-inch 16:9 display. Screen front plane exactly x=4.970 m.
diagonal=.0254*77;width=diagonal*16/math.sqrt(337);height=diagonal*9/math.sqrt(337)
tv=g.group('TV 77-inch 16-by-9 PROXY','living',(5.003,6.95),(.278,width+.022,.651+height),colour='#465758',purpose='screen',note='77-inch visible 16:9 area; display front x=4.970, freestanding on console. Foot envelope extends west of panel; product unselected.')
zc=.64+height/2
g.box('77 TV thin panel',(0,0,zc),(.055,width+.022,height+.022),dark,.009,tv)
g.box('77 TV display face',(-.030,0,zc),(.006,width,height),screen,.003,tv)
for y in (-.57,.57):
    g.box('77 TV foot',(-.123,y,.572),(.25,.045,.035),dark,.005,tv)
    g.box('77 TV support',(-.015,y,.610),(.035,.025,.075),dark,.004,tv)
v['items'].extend(g.ITEMS)
# Proxy envelope for TV only covers its actual support/panel extent; screen is intentionally on console.
for it in v['items']:
    if it['name']=='TV 77-inch 16-by-9 PROXY':
        it['polygon']=[[4.755,6.95-(width+.022)/2],[5.033,6.95-(width+.022)/2],[5.033,6.95+(width+.022)/2],[4.755,6.95+(width+.022)/2]]
v['viewing']={'tv_diagonal_inches':77,'aspect_ratio':[16,9],'screen_width_mm':round(width*1000,2),'screen_height_mm':round(height*1000,2),
    'screen_front_x_m':screen_x,'screen_centre_y_m':6.95,'screen_centre_z_m':zc,'seated_eye_m':list(eye),
    'horizontal_eye_to_screen_mm':3180,'seated_eye_offset_from_sofa_proxy_centre_mm':100,
    'scope':'Owner-assumed distance, geometrically set from seated eye to screen face, not sofa back or console. Actual sofa/posture/product dimensions need checking.'}
v['checks'].update({'sofa_back_to_west_cabinet_front_mm':round((eye[0]-.10-.5-.533333)*1000),'play_area_m2':round((c-a)*(d-b),3),'tv_console_east_wall_y_bounds':[5.95,7.95]})
data.update({'revision':6,'parent':'05-full-west-storage-l-return/V5-reference-cabinets',
    'parent_sha256':parent_hash,'variants':{'V6-east-tv':v},
    'feasibility_status':'Conditional: 3180 mm assumed eye-to-screen set in model; about 657 mm behind sofa for west-storage access; actual product/site/contents and girls night access unresolved.'})
data['latest_owner_decisions'].append('Add 77-inch TV and console to east living wall; assume 3180 mm viewing distance.')
data['assumptions']=[s for s in data['assumptions'] if not s.startswith('Owner version 5:')]
data['assumptions'].extend(['Owner now reintroduces TV on east wall; overrides V5 no-TV direction. Server remains removed.',
    '3180 mm is horizontal seated-eye to screen-front distance. Proxy eye 100 mm forward of sofa centre at 1120 mm height; actual sofa/posture not measured.',
    'West full-height reference cabinetry and girls mixed-reference cabinets retained; console is a new provisional loose unit.',
    'Rear sofa-to-west-front gap about 657 mm; 350 mm doors leave about 307 mm when open. Access is sequential; household comfort and opening use not approved.',
    'Floor-play rectangle now 1850 x 1750 mm. Recliner moved south, actual recline envelope and entry/guest routes remain product-dependent.',
    'East TV power/AV points and streaming equipment not mapped; no new fixed electrical work assumed.'])
scene['design_version']='Version 6 / 77-inch east TV / 3180 mm viewing / owner-reference cabinets / no server'
scene['feasibility_status']=data['feasibility_status'];scene['tv_viewing_distance_mm']=3180
eye_cam=g.camera('DESIGN V6 seated eye 3180 mm',eye,(screen_x,6.95,zc),28)
tv_cam=g.camera('DESIGN V6 east TV wall',(.75,4.8,1.60),(4.80,6.95,1.10),24)
girls_cam=g.camera('DESIGN V6 girls full cabinet run',(10.60,7.78,1.30),(8.38,7.78,1.22),19)
scene.camera=bpy.data.objects['DESIGN living from entry'];bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'V6-east-tv.blend'))
(OUT/'layouts.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
for cam,name in [(scene.camera,'V6-living-entry'),(tv_cam,'V6-east-tv-wall'),(eye_cam,'V6-seated-view'),
    (bpy.data.objects['DESIGN living storage wall'],'V6-west-storage-access'),(girls_cam,'V6-girls-reference-cabinets')]:g.render(cam,name)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==parent_hash
print('REVISION06_COMPLETE',OUT,flush=True)
