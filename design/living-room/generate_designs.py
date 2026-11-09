"""Create measured furniture variants from the saved shell; never rebuild the baseline.
Run with Blender --background --python this_file.py. Optional args: -- --draft.
"""
import bpy, json, math, sys, hashlib
from pathlib import Path
from mathutils import Vector

if __name__=='__main__' and '--historical-iteration-01' not in sys.argv:
    raise RuntimeError('Iteration 01 is superseded: 2000 mm Packout stacks and girls built-in wardrobe invalidate these layouts. Use corrected revision 02 inputs. Historical reproduction only: pass --historical-iteration-01.')

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'iterations' / '01-family-room-triplets'
OUT.mkdir(parents=True, exist_ok=True)
BASE = ROOT / 'model' / '223C_Existing_Shell_v02.blend'
DRAFT = '--draft' in sys.argv
MANIFEST = {'baseline_sha256': hashlib.sha256(BASE.read_bytes()).hexdigest(), 'units':'metres', 'variants':{},
 'assumptions': ['Furniture is dimensioned proxy geometry, not selected products.',
 'Girls low pull-out bed: 2050 long, 950 wide closed, 1900 wide open; actual model not selected.',
 'Two Packout stacks each use a provisional 600 W x 600 D x 1050 H mm envelope.',
 'Study permitted east/hinge wall segment is interpreted as y=6.68..8.88 m; confirm exact endpoints.',
 'Girls existing cupboards use the south wall instead of the 2200 mm west wall, preserving the open-bed aisle.',
 'Render lights are presentation lighting; existing installed fixtures were not surveyed or redesigned.',
 'Walls/tiles are reference-based approximations; tile format, lighting and paint sheen remain unmeasured.']}

def mat(name, colour, rough=.5, metallic=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*colour,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*colour,1)
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metallic
    return m

def move(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    F.objects.link(obj)

def box(name, xyz, dims, material, bevel=.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz);o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    move(o);o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Furniture edge radius','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent
    return o

def cylinder(name, xyz, radius, depth, material, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=xyz)
    o=bpy.context.object;o.name=name;move(o);o.data.materials.append(material)
    b=o.modifiers.new('Rounded edge','BEVEL');b.width=.008;b.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
    if parent:o.parent=parent
    return o

def group(name, room, centre, dims, angle=0, colour='#bea788', purpose='furniture', note=''):
    p=bpy.data.objects.new(name,None);F.objects.link(p);p.location=(*centre,0);p.rotation_euler.z=math.radians(angle)
    p['room']=room;p['dimensions_mm']=list(round(v*1000) for v in dims);p['assumption']=note
    dx,dy=dims[:2];a=math.radians(angle)
    pts=[(centre[0]+x*math.cos(a)-y*math.sin(a),centre[1]+x*math.sin(a)+y*math.cos(a)) for x,y in [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,dy/2),(-dx/2,dy/2)]]
    ITEMS.append({'name':name,'room':room,'centre':list(centre),'dims':list(dims),'angle':angle,'polygon':pts,'colour':colour,'purpose':purpose,'note':note})
    return p

def cabinet(name,room,x,y,w,d,h,steel=False,angle=0,utility=False):
    p=group(name,room,(x,y),(w,d,h),angle,'#b9c0bf' if steel else '#d4c19f','storage')
    body=M['steel'] if steel else M['oak'];door=M['steel'] if steel else M['cream']
    box(name+' back',(0,d/2-.012,h/2),(w,.024,h),body,parent=p)
    for xx in (-w/2+.012,w/2-.012):box(name+' side',(xx,0,h/2),(.024,d,h),body,parent=p)
    for z in (.06,h-.015):box(name+' base/top',(0,0,z),(w,d,.03),body,parent=p)
    if utility:
        box(name+' equipment divider',(0,0,.59),(.024,d,1.06),body,parent=p)
        box(name+' equipment shelf',(0,0,1.14),(w,d,.03),body,parent=p)
        low=1.16;dh=h-low-.04
    else:low=.09;dh=h-.13
    for i in range(2):
        xx=(-.25 if i==0 else .25)*w
        box(name+' door '+str(i),(xx,-d/2+.009,low+dh/2),(w/2-.012,.025,dh),door,.006,p)
        hx=xx+(w/4-.045)*(1 if i==0 else -1)
        box(name+' handle',(hx,-d/2-.018,low+dh*.55),(.012,.028,.16),M['dark'],.005,p)
    if steel:
        for xx in (-w*.27,w*.27):
            for z in (.18,.22,.26):box(name+' vent',(xx,-d/2-.006,z),(.22,.006,.006),M['dark'],.002,p)
    return p

def sofa(centre, angle=0):
    p=group('SOFA 2500 x 1000','living',centre,(1,2.5,.86),angle,'#c9bca5',note='Three seat proxy; faces local +X')
    box('Sofa upholstered base',(0,0,.28),(.94,2.44,.31),M['fabric'],.075,p)
    box('Sofa back',(-.38,0,.62),(.23,2.44,.55),M['fabric'],.07,p)
    for yy in (-1.15,1.15):box('Sofa arm',(.03,yy,.49),(.94,.20,.5),M['fabric'],.055,p)
    for yy in (-.74,0,.74):
        box('Seat cushion',(.08,yy,.47),(.69,.71,.16),M['linen'],.055,p)
        b=box('Back cushion',(-.25,yy,.68),(.19,.7,.36),M['linen'],.065,p);b.rotation_euler.y=-.12
    for yy,col in [(-.86,M['sage']),(.88,M['clay'])]:
        q=box('Loose scatter cushion',(-.07,yy,.72),(.17,.36,.33),col,.055,p);q.rotation_euler.x=.13
    for xx in (-.31,.31):
        for yy in (-1.04,1.04):cylinder('Sofa oak foot',(xx,yy,.10),.035,.2,M['oak'],p)

def recliner(centre, angle, stool):
    p=group('RETAINED RECLINER proxy','living',centre,(.88,.88,1.05),angle,'#b88b60',note='Exact Stressless model unknown')
    cylinder('Stressless wood base',(0,0,.10),.34,.055,M['walnut'],p)
    box('Recliner support',(-.13,0,.3),(.18,.20,.38),M['walnut'],.03,p)
    box('Leather seat',(.05,0,.48),(.68,.65,.19),M['leather'],.075,p)
    q=box('Leather reclining back',(-.27,0,.77),(.18,.67,.65),M['leather'],.08,p);q.rotation_euler.y=-.22
    box('Leather head cushion',(-.32,0,1.01),(.18,.54,.22),M['leather'],.06,p)
    for yy in (-.38,.38):
        box('Bentwood arm',(-.02,yy,.45),(.55,.06,.08),M['walnut'],.025,p)
        box('Leather arm pad',(.02,yy,.64),(.56,.15,.12),M['leather'],.05,p)
    s=group('RETAINED FOOTSTOOL proxy','living',stool,(.62,.52,.43),angle,'#b88b60')
    cylinder('Ottoman wooden base',(0,0,.1),.23,.06,M['walnut'],s)
    box('Ottoman stem',(0,0,.25),(.11,.15,.3),M['walnut'],.025,s)
    box('Ottoman leather cushion',(0,0,.39),(.62,.52,.14),M['leather'],.06,s)

def bed():
    p=group('LOW PULL-OUT BED 2050 x 950','girls',(10.275,8.085),(.95,2.05,.55),colour='#d5c29e')
    box('Low bed frame',(0,0,.18),(.95,2.05,.25),M['oak'],.035,p)
    box('Main mattress',(0,0,.37),(.9,2,.17),M['white'],.055,p)
    box('Terracotta duvet',(0,-.19,.47),(.9,1.5,.12),M['clay'],.055,p)
    box('Main pillow',(0,.75,.49),(.64,.36,.12),M['linen'],.055,p)
    box('Low headboard',(0,1.0,.31),(.95,.06,.48),M['oak'],.02,p)
    # Small continuous low edge is a geometry proxy, not a specified child guard rail.
    box('Bed outer edge',(.45,.18,.4),(.045,1.35,.2),M['oak'],.018,p)
    t=group('PULL-OUT lower mattress','girls',(9.325,8.085),(.95,2.05,.27),colour='#a1b5a3',purpose='trundle_open',note='Shown in night view; 950 mm extension')
    for xx in (-.33,.33):
        for yy in (-.8,.8):cylinder('Pull-out wheel',(xx,yy,.045),.04,.045,M['dark'],t)
    box('Pull-out tray',(0,0,.09),(.95,2.05,.08),M['oak'],.025,t)
    box('Lower mattress',(0,0,.19),(.9,2,.14),M['white'],.045,t)
    box('Sage lower duvet',(0,-.2,.28),(.9,1.5,.1),M['sage'],.05,t)
    box('Lower pillow',(0,.75,.3),(.65,.36,.11),M['linen'],.05,t)
    return t

def props():
    # Daily toys make the family use visible without disguising the measured play footprint.
    x,y=PLAY[0]+.4,PLAY[1]+.4
    for i in range(6):box('Loose play block',(x+.16*(i%3),y+.16*(i//3),.07),(.12,.12,.14),[M['clay'],M['sage'],M['oak']][i%3],.014)
    for i in range(3):box('Book on cupboard',(4.77,6.1,.82+i*.035),(.27,.35,.03),[M['sage'],M['clay'],M['linen']][i],.003)

def setup_materials():
    global M
    M={k:mat(k,c,r,metal) for k,c,r,metal in [
     ('oak',(.50,.34,.17),.43,0),('walnut',(.19,.095,.038),.4,0),('cream',(.77,.74,.66),.5,0),
     ('fabric',(.47,.43,.35),.85,0),('linen',(.69,.63,.52),.85,0),('sage',(.27,.38,.31),.8,0),
     ('clay',(.50,.23,.14),.8,0),('leather',(.43,.25,.12),.45,0),('white',(.86,.84,.78),.8,0),
     ('dark',(.025,.03,.028),.5,0),('steel',(.48,.52,.53),.38,.72),('red',(.45,.018,.012),.45,0),
     ('screen',(.018,.025,.028),.2,.15)]}
    # Subtle timber texture; finishes are proxy materials, no downloaded textures.
    for key in ('oak','walnut'):
        m=M[key];n=m.node_tree.nodes;lk=m.node_tree.links;bs=n.get('Principled BSDF')
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=2
        coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2,2,35)
        lk.new(coord.outputs['Generated'],mapping.inputs[0]);lk.new(mapping.outputs[0],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');base=M[key].diffuse_color[:3]
        ramp.color_ramp.elements[0].color=tuple(v*.78 for v in base)+(1,);ramp.color_ramp.elements[1].color=tuple(v*1.1 for v in base)+(1,)
        lk.new(tex.outputs['Fac'],ramp.inputs[0]);lk.new(ramp.outputs[0],bs.inputs['Base Color'])
    wall=bpy.data.materials.get('Neutral warm wall finish — placeholder')
    if wall:
        wall.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.79,.81,.77,1)
    floor=bpy.data.materials.get('Neutral floor — placeholder')
    if floor:
        n=floor.node_tree.nodes;lk=floor.node_tree.links;bs=n.get('Principled BSDF')
        bs.inputs['Roughness'].default_value=.23
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=.9;tex.inputs['Detail'].default_value=4;tex.inputs['Roughness'].default_value=.65
        coord=n.new('ShaderNodeTexCoord');lk.new(coord.outputs['Object'],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.58;ramp.color_ramp.elements[0].color=(.84,.84,.81,1)
        ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(.61,.63,.62,1)
        lk.new(tex.outputs['Fac'],ramp.inputs[0]);lk.new(ramp.outputs[0],bs.inputs['Base Color'])

def camera(name,loc,target,lens=24):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.035
    return o

def light(name,loc,target,power,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.visible_glossy=False
    o.visible_transmission=False
    o.visible_camera=False

def render(cam,name):
    scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)

def build(variant):
    global scene,F,ITEMS,PLAY
    bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene;ITEMS=[]
    F=bpy.data.collections.get('13 | Loose furniture — empty for next iteration');F.name='13 | Loose furniture — family room iteration 01'
    setup_materials()
    for c in bpy.data.collections:
        if c.name.startswith(('10 |','11 |','12 |')):c.hide_render=True
    for o in list(bpy.data.objects):
        if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
    light('Presentation daylight living',(2.2,8.35,2.3),(2.2,5.5,.5),250,2.8)
    light('Presentation living fill',(2.8,4.6,2.48),(2.7,6.7,.4),170,3.2)
    light('Presentation study daylight',(6.6,8.9,2.3),(7.2,7.3,1),130,1.8)
    light('Presentation girls daylight',(9.7,8.9,2.3),(9.6,7.4,.5),150,1.8)
    light('Presentation girls fill',(9.6,5.9,2.45),(9.5,7.5,.5),100,1.8)
    scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45
    # Shared storage and sleeping arrangement.
    for i in range(2):cabinet('REUSE girls cupboard '+str(i+1),'girls',9.68+i*.9,5.79,.9,.4,2,steel=True,angle=180)
    trundle=bed()
    cabinet('REUSE study cupboard','study',7.823333,7.13,.9,.4,2,steel=True,angle=-90)
    cabinet('NEW study equipment + archive','study',7.673333,8.23,1.3,.7,2.2,angle=-90,utility=True)
    # Packout stacks are clearly provisional envelopes, each within the new lower utility bays.
    for i,yy in enumerate((7.905,8.555)):
        p=group('PACKOUT stack '+str(i+1)+' PROXY','study',(7.673333,yy),(.6,.6,1.05),colour='#94372d',purpose='equipment',note='Unmeasured assumed envelope; verify actual stack sizes')
        for j in range(3):
            box('Packout red case',(0,0,.19+j*.31),(.56,.58,.27),M['red'],.025,p)
            box('Packout black lid',(0,0,.34+j*.31),(.6,.6,.06),M['dark'],.014,p)
            box('Packout handle',(-.3,0,.2+j*.31),(.035,.23,.06),M['dark'],.008,p)
    # Shared new closed toy cupboard: proxy internal envelope ~650 litres before detailed fit.
    cabinet('NEW toy cupboard 2400 x 500','living',4.79,6.95,2.4,.5,.8,angle=-90)
    nas=group('RETAINED R6 NAS','living',(.2365,4.48),(.233,.543,.465),colour='#434849')
    box('R6 body',(0,0,.2325),(.233,.543,.465),M['dark'],.012,nas)
    box('R6 front',(0,.274,.24),(.225,.012,.43),M['screen'],.005,nas)
    for j in range(5):box('R6 front vent',(-.116,0,.11+j*.06),(.007,.38,.009),M['steel'],.002,nas)
    if variant=='A-with-tv':
        sofa((.70,6.35));recliner((2.45,7.8),-22,(3.25,7.48));PLAY=(1.5,5.25,3.8,6.95)
        tv=group('TV 65-inch PROXY','living',(4.84,6.95),(.12,1.44,1.66),colour='#465758',purpose='screen',note='65-inch proxy, not a selected screen')
        box('TV thin panel',(0,0,1.28),(.055,1.44,.81),M['dark'],.012,tv)
        box('TV screen',(-.03,0,1.28),(.006,1.405,.776),M['screen'],.004,tv)
        for yy in (-.43,.43):box('TV stand',(-.03,yy,.84),(.24,.04,.055),M['dark'],.005,tv)
    else:
        sofa((2.2,5.4),90);recliner((.85,7.8),-44,(1.5,7.17));PLAY=(2.05,6.15,4.2,7.85)
    x0,y0,x1,y1=PLAY
    box('Loose washable play rug',((x0+x1)/2,(y0+y1)/2,.012),(x1-x0,y1-y0,.018),M['linen'],.035)
    props()
    # One small movable side table; no central coffee table in the floor-play zone.
    tx,ty=(1.16,7.91) if variant=='A-with-tv' else (.49,6.85)
    p=group('SMALL SIDE TABLE','living',(tx,ty),(.38,.38,.48),colour='#aa8a5d')
    cylinder('Side table top',(0,0,.46),.19,.035,M['oak'],p);cylinder('Side table stem',(0,0,.25),.035,.45,M['oak'],p);cylinder('Side table base',(0,0,.035),.14,.035,M['oak'],p)
    # Save exact original architecture extents for native measured plan authoring.
    walls=[]
    for c in bpy.data.collections:
        if c.name.startswith(('02 |','03 |')):
            for o in c.objects:
                if o.type=='MESH':
                    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
                    walls.append({'name':o.name,'rect':[min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts)]})
    MANIFEST['variants'][variant]={'items':ITEMS,'walls':walls,'play_rect':PLAY,
      'rooms':{'living':[0,3.446667,5.073333,8.486667],'study':[5.353333,5.55,8.023333,9.16],'girls':[8.133333,5.55,11.073333,9.16]},
      'checks':{'study_wall_run_mm':2200,'study_run_start_y':6.68,'study_run_end_y':8.88,
       'girls_south_cupboard_run_mm':1800,'girls_south_wall_nominal_mm':1866.667,
       'girls_open_bed_west_aisle_mm':716.667,'girls_cupboard_to_bed_foot_mm':1070,
       'study_door_leaf_to_storage_start_mm':226.7,'girls_day_aisle_mm':1666.667},
      'storage':{'existing_cupboards':3,'samla_contents_boxes':21,'toy_nominal_l':450,'study_box_nominal_l':495,
       'new_living_inner_envelope_l':round(2.30*.43*.66*1000),
       'study_upper_inner_envelope_l':round(1.22*.62*.98*1000),
       'status':'Proxy envelopes only; shelf layout, loads, actual contents, hardware and Packout fit remain unverified.'}}
    scene.render.engine='CYCLES';scene.cycles.samples=16 if DRAFT else 40;scene.cycles.use_denoising=True
    scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=60 if DRAFT else 100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.view_settings.view_transform='AgX'
    cams={
     'living':camera('DESIGN living from entry',(2.2,3.75,1.62),(2.5,6.85,1.0),23),
     'living_reverse':camera('DESIGN living towards seating',(4.48,8.32,1.65),(1.9,5.95,.85),24),
     'girls':camera('DESIGN girls day',(8.48,5.88,1.55),(9.85,7.9,.85),21),
     'girls_storage':camera('DESIGN girls towards reused cupboards',(8.47,8.9,1.55),(10.0,6.0,1.05),22),
     'study':camera('DESIGN study permitted wall',(5.55,7.78,1.35),(7.85,7.78,1.1),20)}
    # Trundle stored beneath main bed in daytime; night view is a separate state.
    trundle.location.x+=.95
    for it in ITEMS:
        if it['purpose']=='trundle_open':it['state']='night-only'
    scene['design_version']=variant;scene['notes']='See REVIEW.md and layouts.json. Architecture baseline retained. Furniture and finishes are proxies.'
    scene.camera=cams['living'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(variant+'.blend')))
    only=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--view=')),None)
    if only:
        render(cams[only],'shared-'+only)
        return
    render(cams['living'],variant+'-living')
    render(cams['living_reverse'],variant+'-living-reverse')
    if variant=='A-with-tv' and '--living-only' not in sys.argv:
        render(cams['girls'],'shared-girls-day')
        render(cams['girls_storage'],'shared-girls-storage')
        trundle.location.x-=.95;render(cams['girls'],'shared-girls-night');trundle.location.x+=.95
        render(cams['study'],'shared-study')
    bpy.context.view_layer.update()

if __name__=='__main__':
    selected=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--variant=')),None)
    if selected and (OUT/'layouts.json').exists():
        MANIFEST['variants']=json.loads((OUT/'layouts.json').read_text(encoding='utf-8'))['variants']
    for variant in ([selected] if selected else ('A-with-tv','B-without-tv')):build(variant)
    assert hashlib.sha256(BASE.read_bytes()).hexdigest()==MANIFEST['baseline_sha256'],'Baseline changed'
    (OUT/'layouts.json').write_text(json.dumps(MANIFEST,indent=2),encoding='utf-8')
    print('DESIGN_VARIANTS_COMPLETE',str(OUT),flush=True)
