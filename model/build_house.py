"""Build an editable metric shell from the owner's two annotated raster plans.

Run: blender --background --python model/build_house.py
Inputs are beside this script; all generated artifacts stay in model/.
No add-ons, downloads, external materials or UI operations are required.
"""
import bpy
import json
import math
import os
from pathlib import Path
from mathutils import Vector, Quaternion
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'model_settings.json').read_text(encoding='utf-8'))
H = CFG['ceiling_height_mm'] / 1000
DROP = CFG['bathroom_floor_drop_mm'] / 1000
DH = CFG['door_height_mm'] / 1000
BS = CFG['bathroom_window_sill_mm'] / 1000
BT = CFG['bathroom_window_top_mm'] / 1000
SCALE = CFG['source_scale_px_per_m']
OX, OY = CFG['source_origin_px']
REPORT = {'project': CFG['project'], 'units': 'metres', 'checks': [], 'openings': [], 'beams': [], 'rooms': []}

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection':
        bpy.data.collections.remove(c)
default = bpy.data.collections.get('Collection')
if default:
    bpy.data.collections.remove(default)

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'MILLIMETERS'
scene.unit_settings.scale_length = 1
scene['project'] = CFG['project']
scene['ceiling_datum_mm'] = CFG['ceiling_height_mm']
scene['source'] = 'Floor Plan.png + owner-supplied Beam Plan.png'
scene['status'] = 'Existing shell, first iteration; see MODEL NOTES text block for assumptions.'

def coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or scene.collection).children.link(c)
    return c

C = {
    'floor': coll('01 | Floors and bathroom drops'),
    'concrete': coll('02 | Concrete walls — existing'),
    'partition': coll('03 | Interior walls — existing'),
    'windows': coll('04 | Windows — elevation provisional'),
    'doors': coll('05 | Hinged doors and kitchen slider'),
    'beams': coll('06 | Beams — ceiling drops'),
    'false': coll('07 | False ceiling — confirmed 150 mm drop'),
    'sanitary': coll('08 | Fixed sanitary location proxies'),
    'ledge': coll('09 | AC ledge — dimensions provisional'),
    'ceiling': coll('10 | Unfinished ceiling slab — toggle on'),
    'labels': coll('11 | Room labels — presentation only'),
    'reference': coll('12 | Packed reference plans — toggle on'),
    'furniture': coll('13 | Loose furniture — empty for next iteration'),
    'cutters': coll('99 | Internal junction cutters — hidden'),
    'studio': coll('90 | Cameras and lighting')
}

def material(name, rgba, roughness=.65, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = rgba
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = rgba
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return m

MAT = {
    'wall': material('Neutral warm wall finish — placeholder', CFG['wall_finish']),
    'beam': material('Structural beams — soft neutral', (.70,.72,.70,1)),
    'floor': material('Neutral floor — placeholder', CFG['floor_finish'], .74),
    'bath': material('Wet area floor — placeholder', (.40,.46,.46,1), .78),
    'frame': material('Window and slider frames — charcoal', (.085,.105,.11,1), .35, .45),
    'door': material('Existing door finish — placeholder', (.48,.35,.23,1), .55),
    'ceramic': material('Sanitary ceramic — location proxies', (.9,.92,.9,1), .22),
    'chrome': material('Hardware — satin metal', (.42,.46,.47,1), .23, .82),
    'label': material('Plan labels', (.055,.11,.12,1), .7),
    'slab': material('Unfinished structural slab', (.53,.55,.54,1)),
    'ledge': material('External AC ledge concrete', (.46,.49,.48,1))
}
glass = material('Window glass — clear blue grey', (.38,.60,.66,1), .12)
bs = glass.node_tree.nodes.get('Principled BSDF')
bs.inputs['Transmission Weight'].default_value = .8
bs.inputs['IOR'].default_value = 1.45
MAT['glass'] = glass

def xy(px, py):
    return ((px-OX)/SCALE, (OY-py)/SCALE)

def move_to(o, collection):
    for old in list(o.users_collection):
        old.objects.unlink(o)
    collection.objects.link(o)

def box(name, bounds, z0, z1, mat, collection, bevel=0):
    x0,y0,x1,y1 = bounds
    x0,x1 = sorted((x0,x1)); y0,y1 = sorted((y0,y1))
    assert x1-x0 > 1e-6 and y1-y0 > 1e-6 and z1-z0 > 1e-6, name
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    o = bpy.context.object
    o.name = name
    o.dimensions = (x1-x0,y1-y0,z1-z0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    move_to(o,collection)
    if bevel:
        m = o.modifiers.new('Small physical edge radius', 'BEVEL')
        m.width = bevel; m.segments = 2
    return o

def pbox(name, rect, z0, z1, mat, collection, **kwargs):
    x0,y0 = xy(rect[0],rect[1]); x1,y1 = xy(rect[2],rect[3])
    return box(name,(x0,y0,x1,y1),z0,z1,mat,collection,**kwargs)

def prism(name, points, z0, z1, mat, collection):
    p = [xy(*v) for v in points]
    n = len(p)
    verts = [(x,y,z0) for x,y in p] + [(x,y,z1) for x,y in p]
    faces = []
    # Triangulation works for a concave orthogonal footprint, unlike a fan.
    for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in p]]):
        ids = list(tri) if isinstance(tri[0],int) else [min(range(n), key=lambda k:(p[k][0]-v.x)**2+(p[k][1]-v.y)**2) for v in tri]
        faces.append(tuple(i+n for i in ids))
        faces.append(tuple(reversed(ids)))
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,j+n,i+n))
    mesh = bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); collection.objects.link(o); o.data.materials.append(mat)
    # Make the winding of all prism faces consistent after XY conversion.
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active=o
    o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
    o.select_set(False)
    return o

def wall(name, rect, concrete=False, openings=()):
    """Preserve a wall run, splitting its solid mesh around real openings.

    Openings are (start_px,end_px,sill_m,head_m,label) along the long axis.
    Window returns remain actual wall geometry; no opaque overlay windows.
    """
    x0,y0,x1,y1=rect
    horizontal = x1-x0 >= y1-y0
    a,b=(x0,x1) if horizontal else (y0,y1)
    collection=C['concrete' if concrete else 'partition']
    last=a
    out=[]
    def segment(lo,hi,z0,z1,suffix):
        if hi-lo < .01 or z1-z0 < .0001:return
        rr=(lo,y0,hi,y1) if horizontal else (x0,lo,x1,hi)
        o=pbox(name+' | '+suffix,rr,z0,z1,MAT['wall'],collection)
        o['existing_wall']=True; o['wall_type']='concrete' if concrete else 'internal'
        o['ceiling_height_mm']=H*1000
        out.append(o)
    for i,(lo,hi,sill,head,label) in enumerate(sorted(openings)):
        assert a-.1 <= lo < hi <= b+.1, (name,lo,hi,a,b)
        segment(last,lo,-DROP,H,f'solid {i+1}')
        if sill>0:segment(lo,hi,-DROP,sill,'below '+label)
        segment(lo,hi,head,H,'above '+label)
        REPORT['openings'].append({'wall':name,'label':label,'width_mm':round((hi-lo)/SCALE*1000,1),'sill_mm':sill*1000,'head_mm':head*1000})
        last=hi
    segment(last,b,-DROP,H,'solid end')
    return out

def window(name, start_px, end_px, py, thickness_px=16, sill=None, top=None, panels=True):
    sill=CFG['window_sill_mm']/1000 if sill is None else sill
    top=CFG['window_top_mm']/1000 if top is None else top
    x0,y=xy(start_px,py); x1,_=xy(end_px,py)
    depth=max(.055,thickness_px/SCALE*.64); f=.032
    c=C['windows']
    parent=bpy.data.objects.new(name+' | window assembly',None); c.objects.link(parent)
    parent['elevation_status']='PROVISIONAL — no sill/head measured'
    parent['width_mm']=round((end_px-start_px)/SCALE*1000,1)
    parent['sill_mm']=sill*1000; parent['head_mm']=top*1000
    def part(n,b,z0,z1,m):
        o=box(name+' | '+n,b,z0,z1,m,c); o.parent=parent;return o
    part('left jamb',(x0,y-depth/2,x0+f,y+depth/2),sill,top,MAT['frame'])
    part('right jamb',(x1-f,y-depth/2,x1,y+depth/2),sill,top,MAT['frame'])
    split=([sill,CFG['window_fixed_panel_top_mm']/1000,CFG['window_casement_top_mm']/1000,top] if panels else [sill,top])
    for z in split:part('horizontal rail',(x0,y-depth/2,x1,y+depth/2),z-f/2,z+f/2,MAT['frame'])
    n=max(1,round((x1-x0)/.6))
    for i in range(1,n):
        x=x0+(x1-x0)*i/n
        part(f'mullion {i}',(x-f/2,y-depth/2,x+f/2,y+depth/2),sill,top,MAT['frame'])
    for i in range(n):
        xx0=x0+(x1-x0)*i/n+f/2;xx1=x0+(x1-x0)*(i+1)/n-f/2
        for j in range(len(split)-1):
            o=part(f'glass {i+1}.{j+1}',(xx0,y-.006,xx1,y+.006),split[j]+f/2,split[j+1]-f/2,MAT['glass'])
            o['operation']=('fixed lower panel','side-hung casement','top-hung flap (assumed)')[j] if panels else 'bath/service operation unmeasured'
    return parent

def east_sliding_window(name, px, py0, py1, sill, top):
    x,y0=xy(px,py0);_,y1=xy(px,py1)
    a,b=sorted((y0,y1));length=b-a;f=.028;depth=.10
    parent=bpy.data.objects.new(name+' | window assembly',None);C['windows'].objects.link(parent)
    parent['location_status']='CONFIRMED — spans east wall'
    parent['elevation_status']='1000 mm sill confirmed; head provisional'
    parent['sill_mm']=sill*1000;parent['head_mm']=top*1000
    parent['width_mm']=length*1000;parent['panel_count']=3;parent['operation']='three-panel sliding window'
    def part(n,bounds,z0,z1,mat):
        o=box(name+' | '+n,bounds,z0,z1,mat,C['windows']);o.parent=parent;return o
    for y in (a,b-f):part('end jamb',(x-depth/2,y,x+depth/2,y+f),sill,top,MAT['frame'])
    for z in (sill,top-f):part('continuous sliding track',(x-depth/2,a,x+depth/2,b),z,z+f,MAT['frame'])
    overlap=.025;panel_width=(length+2*overlap)/3;step=(length-overlap)/3
    for i in range(3):
        lo=a+i*step;hi=lo+panel_width;xx=x+(i-1)*.03
        for y in (lo,hi-f):part(f'panel {i+1} stile',(xx-.012,y,xx+.012,y+f),sill+f,top-f,MAT['frame'])
        for z in (sill+f,top-2*f):part(f'panel {i+1} rail',(xx-.012,lo,xx+.012,hi),z,z+f,MAT['frame'])
        o=part(f'panel {i+1} sliding glass',(xx-.004,lo+f,xx+.004,hi-f),sill+2*f,top-2*f,MAT['glass'])
        o['operation']='slides north/south along east wall'
    return parent

def door(name, hinge_px, width_mm, closed_deg, open_deg, floor=0, swing='inwards'):
    c=C['doors']; x,y=xy(*hinge_px); w=width_mm/1000; h=CFG['door_height_mm']/1000
    p=bpy.data.objects.new(name+' | hinge (rotate Z)',None);c.objects.link(p);p.location=(x,y,floor)
    p['closed_Z_degrees']=closed_deg;p['display_Z_degrees']=open_deg;p['width_mm']=width_mm
    p['status']='height and hinge side provisional'
    p['swing']=swing
    p.empty_display_type='PLAIN_AXES';p.empty_display_size=.12
    o=box(name+' | leaf',(0,-.018,w,.018),.008,h,MAT['door'],c,bevel=.003)
    o.parent=p
    # Handle is parented to the same hinge so it follows the leaf.
    box_o=box(name+' | handle',(w-.12,-.065,w-.04,-.018),.96,.985,MAT['chrome'],c,bevel=.007)
    box_o.parent=p
    p.rotation_euler[2]=math.radians(open_deg)
    return p

def slider():
    x0,y=xy(586,1077);x1,_=xy(918,1077)
    w=x1-x0;h=CFG['door_height_mm']/1000;c=C['doors']
    p=bpy.data.objects.new('Kitchen | THREE-PANEL slider assembly',None);c.objects.link(p)
    p['confirmed_location']='LEFT of 2388 mm fixed wall, RIGHT of 930 mm return'
    p['opening_width_mm']=round(w*1000,1);p['panel_count']=3
    p['configuration']='Three panels shown closed on three tracks; opening sequence and material unmeasured.'
    for z in (.006,h):
        o=box('Kitchen slider | continuous track',(x0,y-.055,x1,y+.055),z,z+.025,MAT['frame'],c);o.parent=p
    panel_w=(w+.08)/3
    for i in range(3):
        a=x0+i*(w-.04)/3;b=a+panel_w
        yy=y+(i-1)*.032
        for xx in (a,b-.028):
            o=box(f'Kitchen slider | panel {i+1} stile',(xx,yy-.012,xx+.028,yy+.012),.03,h,MAT['frame'],c);o.parent=p
        for zz in (.03,h-.03):
            o=box(f'Kitchen slider | panel {i+1} rail',(a,yy-.012,b,yy+.012),zz,zz+.028,MAT['frame'],c);o.parent=p
        o=box(f'Kitchen slider | panel {i+1} glass',(a+.028,yy-.004,b-.028,yy+.004),.06,h-.03,MAT['glass'],c);o.parent=p

# Main footprint, including wall support. Ordinary finish deliberately stops at
# both bathroom rectangles so the 60 mm floor drop is physically present.
outline=[(58,162),(837,162),(837,80),(879,80),(879,62),(1697,62),(1697,80),(1737,80),(1737,162),(2217,162),(2217,827),(1968,827),(1968,1099),(1508,1099),(1508,1468),(562,1468),(562,1325),(76,1325),(58,1305)]
prism('Continuous base slab — supports wet-area drop',outline,-.20,-DROP-.005,MAT['slab'],C['floor'])

def inside(x,y,poly):
    hit=False
    for i in range(len(poly)):
        a,b=poly[i],poly[(i+1)%len(poly)]
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    return hit

bath_rects=[(1331,827,1601,1083),(1617,827,1950,1083)]
xs=sorted(set([x for x,y in outline]+[v for r in bath_rects for v in (r[0],r[2])]))
ys=sorted(set([y for x,y in outline]+[v for r in bath_rects for v in (r[1],r[3])]))
for j in range(len(ys)-1):
    run=None
    for i in range(len(xs)):
        ok=False
        if i<len(xs)-1:
            mx=(xs[i]+xs[i+1])/2;my=(ys[j]+ys[j+1])/2
            ok=inside(mx,my,outline) and not any(r[0]<mx<r[2] and r[1]<my<r[3] for r in bath_rects)
        if ok and run is None:run=xs[i]
        if not ok and run is not None:
            pbox(f'Floor finish | strip {j}.{i}',(run,ys[j],xs[i],ys[j+1]),-DROP-.005,0,MAT['floor'],C['floor']);run=None
drop=DROP
for i,r in enumerate(bath_rects):
    o=pbox(f'Bathroom {i+1} | lowered floor',r,-DROP-.005,-drop,MAT['bath'],C['floor'])
    o['drop_below_main_floor_mm']=drop*1000

# North facade openings use the owner's measured window widths and offsets.
ws,wt=CFG['window_sill_mm']/1000,CFG['window_top_mm']/1000
facades=[
 ('Living north', (76,162,837,177),[(154.75,502.75,'2320 mm'),(615.25,795.25,'1200 mm')]),
 ('Study north', (879,62,1279.5,76),[(945,1212,'1780 mm')]),
 ('Girls north', (1296,62,1696.5,76),[(1326,1593.75,'1785 mm')]),
 ('Master north',(1752,162,2179.5,177),[(1794.75,2064,'1795 mm')])
]
for name,r,op in facades:
    wall(name,r,True,[(a,b,ws,wt,label) for a,b,label in op])
    for a,b,label in op:window(name+' '+label,a,b,(r[1]+r[3])/2,r[3]-r[1])

# Structural wall/column runs. No walls have been removed for a presentation view.
wall('Living west concrete',(58,177,76,933),True)
wall('Study west upper concrete',(837,80,879,462),True)
wall('Girls east upper concrete',(1697,80,1737,462),True)
wall('Master east concrete',(2180,177,2217,810),True)
wall('Master south concrete',(1824,810,2180,827),True)
wall('Bathrooms west concrete',(1276,810,1331,1083),True)
wall('Bathrooms east concrete',(1950,827,1968,1083),True)
wall('Maid north concrete',(76,933,306,958),True)
wall('Maid west concrete',(58,952,92,1300.75),True)
maid_a=958+595/1000*SCALE
maid_b=maid_a+710/1000*SCALE
wall('Maid east concrete',(278,958,306,1300.75),True,[(maid_a,maid_b,0,DH,'maid hinged door — inferred')])
wall('Maid south concrete',(76,1300.75,306,1325),True)
wall('Entrance west nib concrete',(306,1195,334,1310),True)
wall('Entrance south concrete',(306,1310,562,1325),True,[(340,496,0,DH,'main entrance 1040 mm')])
wall('Kitchen west lower concrete',(562,1211,605,1450),True)
wall('Kitchen south concrete',(605,1450,1276,1468),True)
wall('Service yard east concrete',(1490,1110,1508,1450),True,[(1110,1450,CFG['service_yard_window_sill_mm']/1000,CFG['service_yard_window_top_mm']/1000,'three-panel sliding window above 1000 mm wall — confirmed')])

# Existing internal walls and room access gaps.
wall('Study west lower internal',(837,462,853.5,617.5))
wall('Study south internal',(837,617.5,1118,632.5))
wall('Study / girls dividing internal',(1279.5,76,1296,623))
wall('Study / girls central concrete nib',(1261,623,1314.25,644),True)
wall('Girls south internal',(1457,617.5,1752,632.5))
wall('Girls / master upper internal lining',(1737,177,1752,462))
wall('Girls / master lower internal',(1737,462,1752,617.5))
wall('Master entry door header',(1522.875,632.5,1537.875,810),False,[(632.5,810,0,DH,'master entry door centred on 145 mm segment — confirmed')])
wall('Study access header',(1118,617.5,1261,632.5),False,[(1118,1261,0,DH,'study door')])
wall('Girls access header',(1314.25,617.5,1457,632.5),False,[(1314.25,1457,0,DH,'girls door')])
wall('Bathroom 1 north internal',(1331,810,1601,827),False,[(1331,1484,0,DH,'bathroom 1 door')])
wall('Bathroom 2 north internal',(1617,810,1950,827),False,[(1696,1824,0,DH,'bathroom 2 door')])
wall('Bathroom dividing internal',(1601,827,1617,1099))
wall('Bathroom 1 south internal',(1331,1083,1601,1099),False,[(1511,1601,BS,BT,'bathroom 1 window 600 mm')])
wall('Bathroom 2 south internal',(1617,1083,1950,1099),False,[(1701,1822.5,BS,BT,'bathroom 2 window — inferred 810 mm')])
window('Bathroom 1 south',1511,1601,1091,16,sill=BS,top=BT,panels=False)
window('Bathroom 2 south',1701,1822.5,1091,16,sill=BS,top=BT,panels=False)
wall('Kitchen north 930 mm return',(562,1071,582,1210.5))
wall('Kitchen north 2388 mm FIXED WALL',(918,1071,1276.2,1082))
wall('Kitchen sliding-door header',(586,1071,918,1082),False,[(586,918,0,DH,'three-panel sliding door — confirmed')])
wall('Service yard north internal',(1294,1100,1490,1110))
wall('Kitchen / service yard north return',(1276,1100,1294,1204.5))
wall('Kitchen / service yard south return',(1276,1350,1294,1450))
wall('Service yard south internal',(1294,1450,1490,1468))
east_sliding_window('Service yard EAST three-panel slider',1499,1110,1450,CFG['service_yard_window_sill_mm']/1000,CFG['service_yard_window_top_mm']/1000)

study_door=door('Study door',(1261,625),953.3,180,92)
study_door['hinge_side_status']='CONFIRMED — east/right jamb; doorway unchanged'
girls_door=door('Girls bedroom door',(1314.25,625),951.7,0,88)
girls_door['hinge_side_status']='CONFIRMED — west/left jamb; doorway unchanged'
master_door=door('Master bedroom door',(1530.375,632.5),1183.333,-90,-2)
master_door['hinge_side_status']='CONFIRMED — upper hinge at centre of 145 mm segment between 365 and 1405'
master_door['width_status']='inferred full passage width; not measured'
door('Maid room door',(292,maid_a),710,-90,-2,swing='outwards — confirmed into entrance area')
door('Main entrance',(340,1317),1040,0,88)
door('Bathroom 1 door',(1331,818.5),1020,0,-87)
door('Bathroom 2 door',(1824,818.5),853.3,180,267)
slider()

def beam(name, rect, width_mm, drop_mm, status='measured label'):
    o=pbox(name,rect,H-drop_mm/1000,H,MAT['beam'],C['beams'])
    o['width_mm']=width_mm;o['drop_mm']=drop_mm;o['underside_mm']=2580-drop_mm;o['status']=status
    REPORT['beams'].append({'name':name,'width_mm':width_mm,'drop_mm':drop_mm,'underside_mm':2580-drop_mm,'status':status})
    return o

beam('B01 | Living north window beam',(76,177,837,201),160,325,'drop assumed; 160 mm width labelled')
beam('B02 | Study north window beam',(879,76,1279.5,100),160,325)
beam('B03 | Girls north window beam',(1296,76,1697,100),160,325,'height inferred from adjacent labelled beam')
beam('B04 | Master north window beam',(1752,177,2180,201),160,345)
beam('B05 | Study south beam',(853.5,592.75,1279.5,617.5),165,325)
beam('B06 | Study west small return',(853.5,462,863.25,592.75),65,325)
beam('B07 | Girls south beam',(1296,592.75,1737,617.5),165,325,'165 width labelled; drop inferred')
beam('B08 | Girls east return',(1725.75,462,1752,592.75),175,325,'width/drop inferred from sketch and wall return')
beam('B09 | Living / dining spine',(837,650,879.75,1061),285,345,'285 width labelled; drop inferred at kitchen junction')
beam('B10a | Kitchen cross beam north half',(562,1061,1276,1082),280,345,'345 north / 355 south as annotated')
beam('B10b | Kitchen cross beam south half',(562,1082,1276,1103),280,355,'345 north / 355 south as annotated')
beam('B11 | Kitchen west return',(562,1103,604,1201),280,355,'drop/width inferred from cross beam')
beam('B12 | Kitchen / wet-area spine',(1276,650,1343.5,1450),450,425)
beam('B13 | Bathroom 1 north beam',(1331,810,1601,836.25),175,245)
beam('B14 | Bathroom 2 north beam',(1617,810,1950,836.25),175,245)
beam('B15 | Bathroom divider beam',(1582.375,810,1635.625,1099),355,425)
beam('B16 | Bathroom 2 east beam',(1896.75,836.25,1950,1099),355,425,'355 width labelled; drop inferred from paired divider')

# Exact dimensions from the owner's ceiling note; position registered to plan grid.
o=pbox('FC01 | Master entry ceiling drop 1405 x 1095 x 150',
       (1541.25,645,1752,809.25),H-.15,H,MAT['wall'],C['false'])
o['confirmed_dimensions_mm']=[1405,1095,150]
o['underside_mm']=2430
o['position_status']='registered from second raster to first; approximate within linework'

# Toggleable ceiling slab does not conceal the default model overview.
o=prism('Unfinished ceiling datum | underside exactly 2580 mm',outline,H,H+.12,MAT['slab'],C['ceiling'])
o['underside_mm']=2580;o['slab_thickness_status']='120 mm visual aid only'

# External AC ledge; unknown depth is deliberately kept in settings.
ledge_depth=CFG['ac_ledge_depth_mm']/1000*SCALE
ledge_z=-CFG['ac_ledge_floor_drop_mm']/1000
pbox('AC ledge | slab',(1617,1099,1950,1100+ledge_depth),ledge_z-.10,ledge_z,MAT['ledge'],C['ledge'])
parapet_top=ledge_z+CFG['ac_ledge_parapet_height_mm']/1000
for name,r in [('south',(1617,1100+ledge_depth-15,1950,1100+ledge_depth)),('west',(1602,1100,1617,1100+ledge_depth)),('east',(1950,1100,1968,1100+ledge_depth))]:
    pbox('AC ledge | '+name+' parapet',r,ledge_z,parapet_top,MAT['ledge'],C['ledge'])

def ellipsoid(name, px, py, z, dims, mat):
    x,y=xy(px,py)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(x,y,z))
    o=bpy.context.object;o.name=name;o.scale=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat);move_to(o,C['sanitary'])
    for p in o.data.polygons:p.use_smooth=True
    o['status']='simplified fixed-fixture proxy; position from plan'
    return o

for name,px,py in [('Bathroom 1 WC',1540,908),('Bathroom 2 WC',1683,1008)]:
    ellipsoid(name+' pedestal',px,py,.14-drop,(.17,.23,.19),MAT['ceramic'])
    ellipsoid(name+' bowl',px,py,.32-drop,(.205,.29,.115),MAT['ceramic'])
    ellipsoid(name+' seat inset',px,py,.412-drop,(.12,.185,.012),MAT['frame'])
    pbox(name+' cistern',(px+35,py-37,px+52,py+37),.10-drop,.75-drop,MAT['ceramic'],C['sanitary'],bevel=.025)
for name,px,py in [('Bathroom 1 basin',1460,1045),('Bathroom 2 basin',1639,920)]:
    pbox(name+' proxy',(px-23,py-20,px+23,py+20),.73-drop,.84-drop,MAT['ceramic'],C['sanitary'],bevel=.035)
    ellipsoid(name+' inset',px,py,.842-drop,(.10,.075,.008),MAT['bath'])
for name,px,py in [('Bathroom 1 shower',1577,1049),('Bathroom 2 shower',1908,1049)]:
    pbox(name+' floor drain',(px-4,py-4,px+4,py+4),-drop+.001,-drop+.005,MAT['chrome'],C['sanitary'])
    pbox(name+' riser',(px-1,py+12,px+1,py+14),.9-drop,1.98-drop,MAT['chrome'],C['sanitary'])
    pbox(name+' head',(px-8,py+2,px+8,py+17),1.96-drop,1.985-drop,MAT['chrome'],C['sanitary'],bevel=.005)

def label(name, text, px, py, size=.16, z=.012):
    curve=bpy.data.curves.new(name,'FONT');curve.body=text;curve.size=size
    curve.align_x='CENTER';curve.align_y='CENTER';curve.extrude=0
    o=bpy.data.objects.new(name,curve);C['labels'].objects.link(o)
    x,y=xy(px,py);o.location=(x,y,z);o.data.materials.append(MAT['label'])
    return o

rooms=[
 ('LIVING',450,480,'5070 mm north span'),
 ('STUDY',1070,330,'2670 mm upper clear width'),
 ('GIRLS BEDROOM',1490,330,'2670 mm upper clear width'),
 ('MASTER BEDROOM',1965,490,'2850 x 4220 mm'),
 ('DINING / PASSAGE',1060,824,'open circulation beside bathrooms'),
 ('MAID ROOM',185,1200,'1240 x 2285 mm'),
 ('KITCHEN',923,1300,'4470 mm south wall'),
 ('SERVICE YARD',1402,1280,'inferred room identity'),
 ('BATH 1',1450,973,'1800 x 1710 mm; floor drop assumed 60'),
 ('BATH 2',1784,915,'2215 x 1710 mm; floor drop assumed 60')]
for name,x,y,desc in rooms:
    label(name,name,x,y,size=.135 if 'BATH' in name or name=='SERVICE YARD' else .17,z=-drop+.012 if 'BATH' in name else .012)
    REPORT['rooms'].append({'name':name,'dimension_reference':desc})
label('Kitchen fixed wall annotation','2388 mm FIXED WALL',1092,1123,.095)
label('Kitchen slider annotation','3-PANEL SLIDER',750,1130,.10)
label('Entrance annotation','ENTRY',449,1256,.11)
label('Master entry annotation','MASTER ENTRY',1640,735,.105)
label('AC ledge label','AC LEDGE',1780,1164,.11,z=ledge_z+.01)

# Packed image empties retain original plans inside the .blend file.
def reference(name,path,offset=(0,0,0)):
    img=bpy.data.images.load(str(path),check_existing=True);img.pack()
    o=bpy.data.objects.new(name,None);C['reference'].objects.link(o)
    o.empty_display_type='IMAGE';o.data=img
    width=img.size[0]/SCALE;height=img.size[1]/SCALE
    o.empty_display_size=width
    o.location=((img.size[0]/2-OX)/SCALE+offset[0],(OY-img.size[1]/2)/SCALE+offset[1],offset[2])
    o.color=(1,1,1,.38);o.empty_image_depth='BACK';o.show_in_front=False
    o['registration']='150 px/m, floor image origin at (76,1450); beam image shifted +17,+10 px'
    return o
reference('Floor Plan | original, packed',ROOT.parent/'Floor Plan.png',(0,0,-.015))
reference('Beam Plan | original, packed',ROOT/'reference'/'Beam Plan.png',(17/SCALE,-10/SCALE,H+.02))

notes='223C EXISTING SHELL — MODEL NOTES\n\nCONFIRMED\n'+'\n'.join('- '+s for s in CFG['notes']['confirmed'])+'\n\nPROVISIONAL / TO CHECK\n'+'\n'.join('- '+s for s in CFG['notes']['provisional'])
notes+='\n\nHOW TO USE\n- Metric scene; Blender displays millimetres. 1 Blender unit = 1 metre.\n- Ceiling slab and packed references start hidden. Toggle collections 10 and 12.\n- Collection 13 is reserved for loose furniture.\n- Door leaves follow their hinge empties. Rotate hinge Z to swing a leaf.\n- Beams stay separate from all walls. Collection 06 can be hidden for furniture planning.\n- All finishes and sanitary shapes are placeholders.\n- Rebuild from model_settings.json + build_house.py.\n- Cameras: Overview, Top plan, Ceiling structure, Kitchen eye level, Living eye level.\n'
bpy.data.texts.new('READ ME — confirmed facts and assumptions').write(notes)
bpy.data.texts.new('model_settings.json').write(json.dumps(CFG,indent=2,ensure_ascii=False))

def camera(name,location,target,ortho=None):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);C['studio'].objects.link(o)
    o.location=location;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    data.clip_start=.05;data.clip_end=200
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    else:data.lens=23
    return o

cams={
 'overview':camera('CAM 01 | Overall architectural shell',(20,-16,23),(7,4.8,.5),19.0),
 'plan':camera('CAM 02 | Top plan — dimensions in model',(7.0,4.8,28),(7.0,4.8,0),15.4),
 'structure':camera('CAM 03 | Ceiling structure overview',(20,-16,24),(7,4.8,1.6),19.0),
 'kitchen':camera('CAM 04 | Kitchen eye level',(4.2,1.1,1.55),(7.4,3.2,1.4)),
 'living':camera('CAM 05 | Living eye level',(1.0,4.0,1.55),(4.6,7.8,1.4)),
 'service':camera('CAM 06 | Service yard east window',(12.8,-3.0,5.8),(8.7,1.25,1.05),5.6)
}

def area(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);C['studio'].objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

area('Large overhead softbox',(6,4,15),2200,10,(7,4,0))
area('West daylight',(-4,5,8),1400,8,(6,5,0))
area('East fill',(18,10,11),1800,9,(8,5,0))
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.78,.83,.87,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.55

scene.render.engine='CYCLES';scene.cycles.samples=CFG['render_samples']
scene.cycles.use_denoising=True
scene.render.resolution_x,scene.render.resolution_y=CFG['render_resolution']
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.image_settings.color_mode='RGBA'
scene.camera=cams['overview']

for key in ('ceiling','reference','cutters'):
    C[key].hide_render=True;C[key].hide_viewport=True
C['labels'].hide_render=True;C['labels'].hide_viewport=True

# Start in a useful material-coloured, full-home view; preserve the whole shell.
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            ar.spaces.active.shading.type='MATERIAL'
            ar.spaces.active.overlay.show_floor=False
            ar.spaces.active.region_3d.view_distance=21
            ar.spaces.active.region_3d.view_location=(7,4.7,.8)
            ar.spaces.active.region_3d.view_rotation=cams['overview'].rotation_euler.to_quaternion()
            ar.spaces.active.clip_end=200

bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active=None
bpy.context.view_layer.update()

# Validations check physical clearances, real openings, and floor heights.
def check(name,condition,detail):
    REPORT['checks'].append({'name':name,'pass':bool(condition),'detail':detail})
    if not condition:raise AssertionError(name+': '+str(detail))

check('Ceiling datum',abs(H-2.580)<1e-9,H)
wall_objects=[o for key in ('concrete','partition') for o in C[key].objects]
check('Wall geometry respects ceiling datum',all(o.location.z+o.dimensions.z/2<=H+1e-6 and o.location.z-o.dimensions.z/2>=-DROP-1e-6 for o in wall_objects), 'Walls reach wet-area subfloor and stop at unfinished ceiling. Main floor hides the wall bases.')
wall_runs=set(o.name.split(' | ')[0] for o in wall_objects)
check('Every wall run reaches ceiling datum',all(any(o.name.split(' | ')[0]==name and abs(o.location.z+o.dimensions.z/2-H)<1e-6 for o in wall_objects) for name in wall_runs),len(wall_runs))
check('Bathroom drop present',all(abs((o.location.z+o.dimensions.z/2)+drop)<1e-7 for o in C['floor'].objects if 'lowered floor' in o.name),drop)
check('Kitchen fixed wall length',any('2388 mm FIXED WALL' in o.name and abs(o.dimensions.x-2.388)<1e-6 for o in C['partition'].objects), '2388 mm wall is on the right of slider')
check('Kitchen slider on correct side',xy(918,1077)[0]<xy(1276.2,1077)[0], 'Three-panel assembly x=586..918 source pixels, wall x=918..1276.2')
check('Window elevations clear north beams',wt<=H-.345, {'window_head':wt,'lowest_north_beam_underside':H-.345})
check('Doors clear deepest beam',CFG['door_height_mm']<=2580-425,CFG['door_height_mm'])
check('False ceiling dimensions',all(abs(a-b)<1e-7 for a,b in zip(sorted(C['false'].objects[0].dimensions),sorted((1.405,1.095,.150)))),'1405 x 1095 x 150 mm')
check('Window count',len([o for o in C['windows'].objects if o.type=='EMPTY'])==8,'5 north windows + 2 bathroom windows + 1 service-yard window')
check('Packed references',all(img.packed_file is not None for img in bpy.data.images if img.name.endswith('.png')),'Both source plans packed in the .blend')
measured_dimensions={
    'Living north clear width':((837-76)/SCALE*1000,5070),
    'Living west clear depth':((933-177)/SCALE*1000,5040),
    'Study upper clear width':((1279.5-879)/SCALE*1000,2670),
    'Study clear depth':((617.5-76)/SCALE*1000,3610),
    'Girls upper clear width':((1696.5-1296)/SCALE*1000,2670),
    'Girls clear depth':((617.5-76)/SCALE*1000,3610),
    'Master clear width':((2180-1752)/SCALE*1000,2850),
    'Master clear depth':((810-177)/SCALE*1000,4220),
    'Maid clear width':((278-92)/SCALE*1000,1240),
    'Maid clear depth':((1300.75-958)/SCALE*1000,2285),
    'Kitchen south span':((1276-605)/SCALE*1000,4470),
    'Bathroom 1 clear width':((1601-1331)/SCALE*1000,1800),
    'Bathroom 2 clear width':((1950-1617)/SCALE*1000,2215),
    'Bathrooms clear depth':((1083-827)/SCALE*1000,1710)
}
REPORT['measured_dimension_comparison']={name:{'model_mm':round(actual,2),'plan_mm':target,'difference_mm':round(actual-target,2)} for name,(actual,target) in measured_dimensions.items()}
check('Primary measured dimensions within 5 mm raster tolerance',all(abs(actual-target)<=5.001 for actual,target in measured_dimensions.values()),REPORT['measured_dimension_comparison'])
REPORT['object_count']=len(bpy.data.objects)
REPORT['assumptions']=CFG['notes']['provisional']

# Keep each measured source solid editable, while resolving physical overlaps at
# junctions. Ordered differences allocate an intersection to the earlier solid;
# no wall is removed or shortened. Unlike arbitrary offsets this preserves every
# supplied dimension and the exact 2580 mm ceiling datum.
junction_objects=[o for key in ('floor','concrete','partition','beams','false','ledge') for o in C[key].objects if o.type=='MESH']
wall_ids={o.as_pointer() for key in ('concrete','partition') for o in C[key].objects}
wall_cut_modifiers=[]
def world_bounds(o):
    vv=[o.matrix_world@Vector(v) for v in o.bound_box]
    return ([min(v[k] for v in vv) for k in range(3)],[max(v[k] for v in vv) for k in range(3)])
raw_bounds=[world_bounds(o) for o in junction_objects]
junction_count=0
raw_cutters={}
def junction_cutter(index):
    if index not in raw_cutters:
        source=junction_objects[index]
        cutter=bpy.data.objects.new('Junction operand | '+source.name,source.data.copy())
        C['cutters'].objects.link(cutter)
        cutter.matrix_world=source.matrix_world.copy()
        # A 0.1 mm hidden cutter tolerance avoids ambiguous coplanar CSG faces.
        # Measured source solids are unchanged; the clearance is below raster
        # precision and lies at the intersection with the preceding solid.
        for k in range(3):cutter.scale[k]*=(source.dimensions[k]+.0002)/source.dimensions[k]
        cutter.hide_render=True
        raw_cutters[index]=cutter
    return raw_cutters[index]
for i,o in enumerate(junction_objects):
    alo,ahi=raw_bounds[i]
    for j in range(i):
        blo,bhi=raw_bounds[j]
        if all(min(ahi[k],bhi[k])-max(alo[k],blo[k])>1e-6 for k in range(3)):
            cutter=junction_cutter(j)
            mod=o.modifiers.new('Existing junction | '+cutter.name[:35],'BOOLEAN')
            mod.operation='DIFFERENCE';mod.solver='MANIFOLD';mod.object=cutter
            junction_count+=1
            if junction_objects[j].as_pointer() in wall_ids:wall_cut_modifiers.append(mod)
REPORT['junction_boolean_count']=junction_count
print('CLEANED_JUNCTIONS',junction_count,flush=True)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
negative_top_faces=[]
for o in junction_objects:
    evaluated=o.evaluated_get(dg);mesh=evaluated.to_mesh()
    for face in mesh.polygons:
        if face.normal.z < -.5 and all(abs((evaluated.matrix_world@mesh.vertices[k].co).z-H)<1e-5 for k in face.vertices):
            negative_top_faces.append(o.name)
    evaluated.to_mesh_clear()
check('Junction top surfaces have outward normals',not negative_top_faces,negative_top_faces)
REPORT['object_count']=len(bpy.data.objects)
(ROOT/'validation.json').write_text(json.dumps(REPORT,indent=2,ensure_ascii=False),encoding='utf-8')
(ROOT/'MODEL_NOTES.txt').write_text(notes,encoding='utf-8')

blend_path=ROOT/CFG['blend_filename']
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
print('MODEL_SAVED',blend_path,flush=True)

def render(name,cam,labels=False):
    scene.camera=cam;C['labels'].hide_render=not labels
    scene.render.filepath=str(ROOT/'previews'/name)
    bpy.ops.render.render(write_still=True)
    print('RENDER_SAVED',scene.render.filepath,flush=True)

render('01_architectural_shell.png',cams['overview'])
C['beams'].hide_render=True;C['false'].hide_render=True
plan_headers=[o for key in ('concrete','partition') for o in C[key].objects if ' | above ' in o.name]
for o in plan_headers:o.hide_render=True
render('02_floor_plan.png',cams['plan'],True)
for o in plan_headers:o.hide_render=False
C['beams'].hide_render=False;C['false'].hide_render=False
for key in ('concrete','partition','windows','doors','sanitary','ledge'):
    C[key].hide_render=True
for mod in wall_cut_modifiers:mod.show_render=False
render('03_ceiling_structure.png',cams['structure'])
for mod in wall_cut_modifiers:mod.show_render=True
for key in ('concrete','partition','windows','doors','sanitary','ledge'):
    C[key].hide_render=False
C['labels'].hide_render=True
render('04_service_yard_window.png',cams['service'])
scene.camera=cams['overview']
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
print('BUILD_AND_RENDERS_COMPLETE',flush=True)
