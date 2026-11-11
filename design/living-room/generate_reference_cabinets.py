"""Current V5: owner reference cabinet designs, no living server. Blender script."""
import bpy,copy,hashlib,importlib.util,json,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;OUT=HERE/'iterations'/'05-full-west-storage-l-return'
SOURCE=OUT/'V5-no-tv.blend';source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('primitives',HERE/'generate_designs.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));g.scene=scene=bpy.context.scene
g.F=bpy.data.collections['13 | Loose furniture — family room iteration 05'];g.OUT=OUT;g.ITEMS=[]
wood=bpy.data.materials['American walnut — new furniture']
brass=g.mat('Reference hardware — satin brass',(.52,.34,.12),.30,.75)
glass=g.mat('Reference vertical reeded glass — 12 mm illustrative pitch',(.78,.84,.79),.20)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=1
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.46
linen=g.mat('Illustrative storage bins',(.42,.40,.32),.85)
dark=g.mat('Pegboard charcoal',(.065,.06,.048),.8)
holes=g.mat('Pegboard hole shadows',(.008,.009,.008),.9)
bookmats=[g.mat('Reference-view book '+str(i),c,.8) for i,c in enumerate([(.10,.15,.13),(.28,.13,.08),(.43,.39,.28)])]
data=json.loads((OUT/'layouts.json').read_text(encoding='utf-8'));v=copy.deepcopy(data['variants']['V5-no-tv'])
names=[it['name'] for it in v['items'] if it['name'].startswith(('WEST STORAGE','RETURN STORAGE','NEW girls walnut'))]
for name in names+['RETAINED R6 NAS']:
    root=bpy.data.objects.get(name)
    if not root:continue
    for o in list(root.children):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.objects.remove(root,do_unlink=True)
v['items']=[it for it in v['items'] if it['name']!='RETAINED R6 NAS']

def box(name,xyz,dims,mat=wood,parent=None,bevel=.004):return g.box(name,xyz,dims,mat,bevel,parent)
def reeded(name,x0,x1,y0,z0,z1,parent):
    nx=max(24,math.ceil((x1-x0)/.002));verts=[]
    for i in range(nx+1):
        x=x0+(x1-x0)*i/nx;front=y0+.004-.002*math.cos(2*math.pi*(x-x0)/.012)
        verts.extend([(x,front,z0),(x,front,z1),(x,y0+.013,z0),(x,y0+.013,z1)])
    faces=[]
    for i in range(nx):
        a=4*i;b=a+4;faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
    faces.extend([(0,2,3,1),(4*nx,4*nx+1,4*nx+3,4*nx+2)])
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);g.F.objects.link(o);o.parent=parent;o.data.materials.append(glass)
    for p in mesh.polygons:p.use_smooth=p.index<4*nx and p.index%4==0
    o['design_role']='Reference vertical reeded-glass panel'
def knob(name,x,y,z,parent):
    stem=g.cylinder(name+' stem',(x,y-.006,z),.003,.012,brass,parent);stem.rotation_euler.x=math.pi/2
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.007,location=(x,y-.018,z))
    o=bpy.context.object;o.name=name+' brass knob';g.move(o);o.parent=parent;o.data.materials.append(brass)
def pair(parent,w,d,z0,z1,label,glazed=True,handle_z=None):
    y0=-d/2+.028;h=z1-z0
    for side in (-1,1):
        x0=-w/2+.009 if side==-1 else .009;x1=-.009 if side==-1 else w/2-.009
        if glazed:
            for x in (x0+.019,x1-.019):box(label+' walnut stile',(x,y0+.012,(z0+z1)/2),(.038,.024,h),parent=parent)
            for z in (z0+.02,z1-.02):box(label+' walnut rail',((x0+x1)/2,y0+.012,z),(x1-x0-.076,.024,.04),parent=parent)
            reeded(label+' REEDED GLASS '+str(side),x0+.038,x1-.038,y0,z0+.04,z1-.04,parent)
        else:box(label+' solid wood door '+str(side),((x0+x1)/2,y0+.012,(z0+z1)/2),(x1-x0,.024,h),parent=parent)
        knob(label,side*.027,y0,handle_z if handle_z is not None else (z0+z1)/2,parent)
        hinge_x=x0+.006 if side==-1 else x1-.006
        for z in (z0+min(.10,h*.22),z1-min(.10,h*.22)):
            g.cylinder(label+' brass hinge',(hinge_x,y0-.002,z),.004,.034,brass,parent)
def shelf(parent,w,d,z):box('Reference shelf',(0,0,z),(w-.048,d-.07,.024),parent=parent)
def carcass(it):
    w,d,h=it['dims'];p=g.group(it['name'],it['room'],it['centre'],it['dims'],it['angle'],colour='#926b4b',purpose='storage',note='Owner-reference design, dimensions/contents are proxies pending products/site checks.')
    box('Cabinet back',(0,d/2-.012,1.2),(w,.024,2.4),parent=p)
    for x in (-w/2+.012,w/2-.012):box('Cabinet side',(x,0,1.2),(.024,d,2.4),parent=p)
    for z in (.065,2.385):box('Cabinet base/top',(0,0,z),(w,d,.03),parent=p)
    box('Solid walnut plinth',(0,-d/2+.012,.04),(w,.024,.08),parent=p)
    return p,w,d
def bins(parent,w,d,levels):
    for z in levels:
        for x in (-w*.23,w*.23):box('ILLUSTRATIVE bin',(x,-.005,z),(w*.4,d-.15,.24),linen,parent,.012)
def books(parent,w,d,z):
    for i in range(max(3,int((w-.1)/.05))):
        x=-w/2+.075+i*.05
        box('ILLUSTRATIVE book',(x,-.005,z),(.038,min(.22,d-.12),.22+.015*(i%3)),bookmats[i%3],parent,.002)

for it in v['items']:
    if it['name'] not in names:continue
    p,w,d=carcass(it);name=it['name']
    if name.startswith(('WEST STORAGE','RETURN STORAGE')):
        # Reference 1: lower wood drawer, tall main glass pair, separate upper glass pair.
        y0=-d/2+.028
        box('Living solid lower drawer',(0,y0+.012,.22),(w-.024,.024,.26),parent=p)
        for x in (-w*.22,w*.22):knob('Living drawer',x,y0,.22,p)
        pair(p,w,d,.37,1.99,'Living MAIN',handle_z=1.02)
        pair(p,w,d,2.01,2.36,'Living UPPER',handle_z=2.18)
        for z in (.36,.78,1.20,1.62,2.00):shelf(p,w,d,z)
        bins(p,w,d,(.55,.97));books(p,w,d,1.40);books(p,w,d,1.82);bins(p,w,d,(2.18,))
        it['note']='Owner living reference: upper/main framed reeded doors, lower solid drawer, brass knobs/hinges. 2400 H. No NAS.'
    elif it['dims'][0]>.7:
        # Girls 800 reference: closed base, open pegboard niche, two upper glazed sections.
        pair(p,w,d,.09,.91,'Girls BASE',glazed=False,handle_z=.82)
        for z in (.935,1.45,2.04):shelf(p,w,d,z)
        pair(p,w,d,1.47,2.02,'Girls MAIN',handle_z=1.74)
        pair(p,w,d,2.06,2.36,'Girls UPPER',handle_z=2.20)
        box('Girls open-niche pegboard',(0,d/2-.045,1.19),(w-.06,.018,.47),dark,p)
        # Perforation appearance only: no appliance or electrical point is inferred.
        for ix in range(14):
            for iz in range(9):
                o=g.cylinder('Pegboard dot',(-.2925+ix*.045,d/2-.056,.995+iz*.045),.004,.002,holes,p);o.rotation_euler.x=math.pi/2
        books(p,w,d,1.08);bins(p,w,d,(1.74,2.20))
        it['note']='Owner second girls reference: 800 W, upper reeded doors, open book/toy niche with pegboard, lower wood doors; no coffee equipment. 2400 H x 400 D provisional.'
    else:
        # Girls 600 reference: four lower drawers and four open shelf/display compartments.
        y0=-d/2+.028
        for i in range(4):
            z0=.09+i*.2275
            box('Girls 600 drawer '+str(i+1),(0,y0+.012,z0+.105),(w-.024,.024,.21),parent=p)
            box('Girls 600 recessed pull',(0,y0+.001,z0+.193),(w-.08,.004,.012),dark,p,.002)
        for z in (1.02,1.44,1.79,2.09):shelf(p,w,d,z)
        books(p,w,d,1.20)
        for i in range(9):box('ILLUSTRATIVE thin book',(-.20+i*.047,-.01,1.57),(.024,.19,.18),bookmats[i%3],p,.002)
        for z in (1.94,2.24):
            for sign in (-1,1):
                o=box('Reference crossed display stand',(0,.03,z),(.43,.12,.022),parent=p);o.rotation_euler.y=sign*math.radians(23)
        it['note']='Owner first girls reference: 600 W open shelf/display unit with four lower wood drawers; 2400 H x 400 D provisional.'
    p['reference_style']=it['note']

v['storage'].update({'nas_in_living':False,'server_removed_by_owner':True,'girls_reeded_800_units':2,'girls_open_600_unit':1})
v['checks']['server_removed']=True
data.update({'variants':{'V5-reference':v},'front_style':'Owner references: living upper/main reeded + wood drawer; girls two 800 hybrid units + 600 open/drawers.',
    'parent_solid_sha256':source_hash,'latest_owner_decisions':['Living cabinet design from supplied walnut/reeded reference','Girls two 800 units from second reference and one 600 from first','Remove server from living room; no alternative destination assumed'],
    'illustrative_contents_only':True})
data['assumptions']=[s for s in data['assumptions'] if not ('R6' in s or 'NAS' in s)]
data['assumptions'].extend(['Owner removed server from living proposal, overriding prior retention in living; no other-room relocation claimed.',
    'Girls reference mapping: two 800 mm units use glass/niche/closed-base design; 600 mm unit uses open shelves/four drawers. All 2400 H; depths provisional.',
    'Reference images establish appearance only; no product model, available sizes, cost, actual glass/hardware, contents capacity or electrical appliances inferred.'])
scene['design_version']='Version 5 / owner reference cabinets / no TV or server'
scene['door_style']=data['front_style'];scene['contents_visualisation']='Illustrative books/bins, not actual packing proof.'
scene.cycles.samples=64;scene.cycles.max_bounces=12;scene.cycles.transmission_bounces=10
scene.camera=bpy.data.objects['DESIGN living from entry'];bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'V5-reference-cabinets.blend'))
(OUT/'layouts-reference.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
for cam,name in [('DESIGN living storage wall','V5-reference-west-storage'),('DESIGN L corner from living','V5-reference-l-return'),
    ('DESIGN living from entry','V5-reference-living-entry'),('DESIGN girls wardrobe and west cupboards','girls-reference-storage')]:g.render(bpy.data.objects[cam],name)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
print('REFERENCE_CABINETS_COMPLETE',OUT,flush=True)
