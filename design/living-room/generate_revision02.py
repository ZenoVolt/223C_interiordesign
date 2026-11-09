"""Corrected room triplets: fixed sliding wardrobe and full-height freestanding Packout."""
import bpy,importlib.util,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('furniture_primitives',HERE/'generate_designs.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
OUT=HERE/'iterations'/'02-wardrobe-and-full-height-packout';OUT.mkdir(parents=True,exist_ok=True)
g.OUT=OUT;g.DRAFT='--draft' in sys.argv
old=json.loads((HERE/'iterations'/'01-family-room-triplets'/'layouts.json').read_text(encoding='utf-8'))
DATA={'revision':2,'valid_for_current_brief':True,'feasibility_status':'conditional on day/night cupboard access trade-off and final product/site checks',
 'baseline_sha256':hashlib.sha256(g.BASE.read_bytes()).hexdigest(),'units':'metres','variants':{},
 'assumptions':['Both Packout stacks reserve 600 W x 450 D x 2000 H mm including planning allowance; not enclosed.',
 'Packout composition per owner: two 4-drawer 48-22-8444, one multi-depth 3-drawer 48-22-8447, two cabinets 48-22-8445.',
 'Module proportions are illustrative within the owner-confirmed 2000 mm overall height; do not infer actual interlock/base dimensions.',
 'Fixed wardrobe south wall: 600 mm depth and sliding doors confirmed. Full nominal 1867 mm wall reserved; visible cabinet and switch gap approximated.',
 'Girls 2200 mm west-wall segment interpreted as y=6.68..8.88 m; exact endpoints remain to confirm.',
 'Night mode accesses mattresses from the foot; 270 mm beside lower mattress is not a walking route. Metal cupboard doors need trundle closed for full use.',
 'Bed and recliner remain dimensioned proxies. Fixed finish colours and render lights are illustrative.']}

def fixed_wardrobe():
    # Reserve entire south-wall bay; do not use the unmeasured switch strip as furniture space.
    x0,x1=9.206667,11.073333
    p=g.group('FIXED SLIDING WARDROBE','girls',((x0+x1)/2,5.85),(x1-x0,.6,2.25),colour='#d1d0c6',purpose='fixed',note='600 mm depth and sliding doors confirmed; width/height/switch strip approximated')
    width=x1-x0-.15;centre=.075
    g.box('Existing wardrobe carcass',(centre,-.035,1.125),(width,.53,2.25),g.M['cream'],.006,p)
    for i in range(2):
        xx=centre+(-.25 if i==0 else .25)*width
        g.box('Existing sliding door',(xx,.241+i*.018,1.13),(width/2+.025,.025,2.19),g.M['white'],.005,p)
        g.box('Existing sliding handle',(xx+(.16 if i==0 else -.16),.269+i*.018,1.14),(.015,.022,.26),g.M['dark'],.004,p)
    c=bpy.data.collections.new('14 | Existing built-in wardrobe — retained');g.scene.collection.children.link(c)
    for o in [p]+list(p.children):
        for col in list(o.users_collection):col.objects.unlink(o)
        c.objects.link(o)

def packout_stack(name,cy):
    p=g.group(name,'study',(7.798333,cy),(.6,.45,2),angle=-90,colour='#963d32',purpose='equipment',note='Freestanding, 2000 H owner-confirmed; 600 x 450 footprint allowance based on Milwaukee dimensions')
    heights=[.361,.361,.361,.381,.381];scale=2/sum(heights);z=0
    for i,h0 in enumerate(heights):
        h=h0*scale;w=.565 if i<3 else .508;dep=.36 if i<3 else .34
        g.box(name+' module '+str(i+1),(0,0,z+h/2),(w,dep,h-.012),g.M['red'],.018,p)
        g.box(name+' top rim '+str(i+1),(0,0,z+h-.018),(w,dep,.035),g.M['dark'],.008,p)
        if i<3:
            count=4 if i<2 else 3
            for j in range(count):
                zz=z+.04+(j+.5)*(h-.075)/count
                g.box(name+' drawer face',(0,-dep/2-.008,zz),(w-.075,.018,(h-.075)/count-.012),g.M['red'],.006,p)
                g.box(name+' drawer handle',(0,-dep/2-.027,zz),(.27,.035,.024),g.M['dark'],.005,p)
            for xx in (-w/2+.025,w/2-.025):g.box(name+' reinforcing bar',(xx,-dep/2-.018,z+h/2),(.022,.022,h-.04),g.M['steel'],.004,p)
        else:
            g.box(name+' cabinet front',(0,-dep/2-.008,z+h/2),(w-.05,.02,h-.055),g.M['red'],.006,p)
            g.box(name+' cabinet handle',(0,-dep/2-.027,z+.08),(.26,.035,.025),g.M['dark'],.005,p)
        z+=h

def build(variant):
    bpy.ops.wm.open_mainfile(filepath=str(g.BASE));g.scene=bpy.context.scene;s=g.scene;g.ITEMS=[]
    g.F=bpy.data.collections.get('13 | Loose furniture — empty for next iteration');g.F.name='13 | Loose furniture — family room iteration 02'
    g.setup_materials()
    for c in bpy.data.collections:
        if c.name.startswith(('10 |','11 |','12 |')):c.hide_render=True
    for o in list(bpy.data.objects):
        if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
    for args in [('Living daylight',(2.2,8.35,2.3),(2.2,5.5,.5),250,2.8),('Living fill',(2.8,4.6,2.48),(2.7,6.7,.4),170,3.2),
        ('Study daylight',(6.6,8.9,2.3),(7.2,7.3,1),130,1.8),('Girls daylight',(9.7,8.9,2.3),(9.6,7.4,.5),150,1.8),
        ('Girls fill',(9.6,5.9,2.45),(9.5,7.5,.5),100,1.8)]:g.light(*args)
    s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45
    fixed_wardrobe()
    for i in range(2):g.cabinet('REUSE girls cupboard '+str(i+1),'girls',8.38,7.13+i*.9,.9,.4,2,steel=True,angle=90)
    trundle=g.bed()
    g.cabinet('REUSE study cupboard','study',7.823333,7.13,.9,.4,2,steel=True,angle=-90)
    packout_stack('PACKOUT stack 1 / 2000 H',7.93);packout_stack('PACKOUT stack 2 / 2000 H',8.58)
    g.cabinet('NEW toy cupboard 2400 x 500','living',4.79,6.95,2.4,.5,.8,angle=-90)
    g.cabinet('NEW archive cupboard 800 x 500','living',4.79,5.25,.8,.5,2.1,angle=-90)
    # Nominal depth represents the complete proxy, including handles, not just its carcass.
    for p in list(g.F.objects):
        if p.type!='EMPTY' or not p.name.startswith(('REUSE','NEW toy','NEW archive')):continue
        children=[o for o in p.children if o.type=='MESH']
        lo=min(o.location.y+v.co.y for o in children for v in o.data.vertices)
        hi=max(o.location.y+v.co.y for o in children for v in o.data.vertices)
        depth=p['dimensions_mm'][1]/1000;factor=depth/(hi-lo)
        for o in children:o.location.y=(o.location.y-lo)*factor-depth/2;o.scale.y*=factor
    nas=g.group('RETAINED R6 NAS','living',(.2365,4.48),(.233,.543,.465),colour='#434849')
    g.box('R6 body',(0,0,.2325),(.233,.543,.465),g.M['dark'],.012,nas)
    g.box('R6 front',(0,.274,.24),(.225,.012,.43),g.M['screen'],.005,nas)
    if variant=='A-with-tv':
        g.sofa((.70,6.35));g.recliner((2.45,7.8),-22,(3.25,7.48));g.PLAY=(1.5,5.25,3.8,6.95)
        p=g.group('TV 65-inch PROXY','living',(4.84,6.95),(.12,1.44,1.66),colour='#465758',purpose='screen')
        g.box('TV thin panel',(0,0,1.28),(.055,1.44,.81),g.M['dark'],.012,p)
        g.box('TV screen',(-.03,0,1.28),(.006,1.405,.776),g.M['screen'],.004,p)
        for yy in (-.43,.43):g.box('TV stand',(-.03,yy,.84),(.24,.04,.055),g.M['dark'],.005,p)
    else:
        g.sofa((2.2,5.4),90);g.recliner((.85,7.8),-44,(1.5,7.17));g.PLAY=(2.05,6.15,4.2,7.85)
    a,b,c,d=g.PLAY;g.box('Loose washable play rug',((a+c)/2,(b+d)/2,.012),(c-a,d-b,.018),g.M['linen'],.035);g.props()
    tx,ty=(1.16,7.91) if variant=='A-with-tv' else (.49,6.85)
    p=g.group('SMALL SIDE TABLE','living',(tx,ty),(.38,.38,.48),colour='#aa8a5d')
    g.cylinder('Side table top',(0,0,.46),.19,.035,g.M['oak'],p);g.cylinder('Side table stem',(0,0,.25),.035,.45,g.M['oak'],p);g.cylinder('Side table base',(0,0,.035),.14,.035,g.M['oak'],p)
    reference=old['variants'][variant]
    DATA['variants'][variant]={'items':g.ITEMS,'walls':reference['walls'],'rooms':reference['rooms'],'play_rect':g.PLAY,
     'study_allowed_segment':[6.68,8.88],
     'checks':{'girls_night_side_gap_mm':270,'girls_day_cupboard_to_bed_gap_mm':1220,'girls_wardrobe_to_bed_foot_mm':910,
      'study_cupboard_plus_stack_allowances_mm':2100,'study_spacing_allowance_mm':100},
     'storage':{'existing_cupboards':3,'samla_contents_boxes':21,'toy_nominal_l':450,'study_box_nominal_l':495,
       'new_living_toy_inner_envelope_l':653,'new_living_archive_inner_envelope_l':588,
       'status':'Content allocation retained; actual shelf/contents capacity unresolved. Metal cupboard doors not fully usable with trundle open.'}}
    cams={
     'living':g.camera('DESIGN living from entry',(2.2,3.75,1.62),(2.5,6.85,1),23),
     'living_reverse':g.camera('DESIGN living towards seating',(4.48,8.32,1.65),(1.9,5.95,.85),24),
     'living_storage':g.camera('DESIGN living storage wall',(.5,5.2,1.6),(4.7,6.15,1.1),23),
     'girls':g.camera('DESIGN girls day',(8.68,6.35,1.6),(9.8,8.1,.9),22),
     'girls_storage':g.camera('DESIGN girls wardrobe and west cupboards',(10.6,8.9,1.6),(8.9,6.5,1),21),
     'study':g.camera('DESIGN study freestanding stacks',(5.55,7.78,1.35),(7.85,7.78,1.05),20)}
    s.render.engine='CYCLES';s.cycles.samples=16 if g.DRAFT else 40;s.cycles.use_denoising=True
    s.render.resolution_x=1280;s.render.resolution_y=960;s.render.resolution_percentage=60 if g.DRAFT else 100
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.view_settings.view_transform='AgX'
    trundle.location.x+=.95
    s['design_version']='revision02 '+variant;s['feasibility_status']=DATA['feasibility_status']
    s.camera=cams['living'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(variant+'.blend')))
    if '--storage-only' in sys.argv:
        g.render(cams['living_storage'],variant+'-living-storage')
        return
    for view in ('living','living_reverse','living_storage'):g.render(cams[view],variant+'-'+view.replace('_','-'))
    if variant=='A-with-tv':
        g.render(cams['girls'],'shared-girls-day');g.render(cams['girls_storage'],'shared-girls-storage')
        trundle.location.x-=.95;g.render(cams['girls'],'shared-girls-night');trundle.location.x+=.95
        g.render(cams['study'],'shared-study')

for variant in ('A-with-tv','B-without-tv'):build(variant)
assert hashlib.sha256(g.BASE.read_bytes()).hexdigest()==DATA['baseline_sha256']
(OUT/'layouts.json').write_text(json.dumps(DATA,indent=2),encoding='utf-8')
print('REVISION02_COMPLETE',OUT,flush=True)
