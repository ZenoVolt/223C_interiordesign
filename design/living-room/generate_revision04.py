"""Variation 4 from the saved revision-03 A scene, preserving all parent files.

Blender --background --python design/living-room/generate_revision04.py
Optional script flags: -- --no-render or --draft.
"""
import bpy, copy, hashlib, importlib.util, json, math, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
PARENT = HERE / 'iterations' / '03-wall-bounded-american-walnut'
OUT = HERE / 'iterations' / '04-west-tv-three-walnut-cabinets'
OUT.mkdir(parents=True, exist_ok=True)
BASE = HERE.parents[1] / 'model' / '223C_Existing_Shell_v02.blend'
protected = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE, *PARENT.glob('*.blend'))}
data = json.loads((PARENT / 'layouts.json').read_text(encoding='utf-8'))
v = copy.deepcopy(data['variants']['A-with-tv'])

spec = importlib.util.spec_from_file_location('primitives', HERE / 'generate_designs.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
bpy.ops.wm.open_mainfile(filepath=str(PARENT / 'A-with-tv.blend'))
g.scene = scene = bpy.context.scene
g.F = bpy.data.collections['13 | Loose furniture — family room iteration 03']
g.F.name = '13 | Loose furniture — family room iteration 04'
g.OUT = OUT
g.ITEMS = []
g.M = {'oak': bpy.data.materials['American walnut — new furniture'],
       'cream': bpy.data.materials['American walnut — new furniture'],
       'dark': bpy.data.materials['dark']}

# Turn the living arrangement toward west. NAS stays at its existing west port zone.
# Cabinet fronts face local -Y; seats face local +X, so rotations differ.
living_width = v['rooms']['living'][2]
for it in v['items']:
    if it['room'] != 'living' or it['name'] == 'RETAINED R6 NAS':
        continue
    root = bpy.data.objects[it['name']]
    root.location.x = living_width - root.location.x
    it['centre'][0] = living_width - it['centre'][0]
    it['polygon'] = [[living_width-x, y] for x, y in it['polygon']]
    it['angle'] = -it['angle'] if it['purpose'] == 'storage' else 180-it['angle']
    root.rotation_euler.z = math.radians(it['angle'])
    if it['purpose'] == 'storage':
        it['note'] = 'American walnut, freestanding; now backs onto west wall.'
    if it['purpose'] == 'screen':
        it['note'] = '65-inch proxy on freestanding media cupboard at west wall; no wall mounting.'

# Unparented rug and loose props also follow the living rearrangement.
for o in g.F.objects:
    if o.type == 'MESH' and not o.parent:
        o.location.x = living_width-o.location.x
for i, o in enumerate(sorted((o for o in g.F.objects if o.name.startswith('Book on cupboard')), key=lambda o:o.name)):
    o.location = (.30, 7.44, .92+i*.035)
a,b,c,d = v['play_rect']
v['play_rect'] = [living_width-c, b, living_width-a, d]

# Replace the girls' two proposed metal units. Preserve their contents in new units.
for root in [o for o in list(g.F.objects) if o.type == 'EMPTY' and o.name.startswith('REUSE girls cupboard')]:
    for child in list(root.children):
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(root, do_unlink=True)
v['items'] = [it for it in v['items'] if not it['name'].startswith('REUSE girls cupboard')]
y = 6.68
for i, w in enumerate((.8, .8, .6), 1):
    root = g.cabinet(f'NEW girls walnut cabinet {i}', 'girls', 8.38, y+w/2, w, .4, 2, angle=90)
    root['assumption'] = 'Width owner-confirmed; 400 D x 2000 H provisional; substitutes for full metal cupboard contents.'
    it = g.ITEMS[-1]
    it['colour'] = '#926b4b'
    it['note'] = root['assumption']
    # Include modelled handles in the full 400 mm depth allowance.
    meshes = [o for o in root.children if o.type == 'MESH']
    lo = min(o.location.y+vertex.co.y for o in meshes for vertex in o.data.vertices)
    hi = max(o.location.y+vertex.co.y for o in meshes for vertex in o.data.vertices)
    factor = .4/(hi-lo)
    for o in meshes:
        o.location.y = (o.location.y-lo)*factor-.2
        o.scale.y *= factor
    # Shelf visualisation only, not a verified interior or load specification.
    for z in (.48, .94, 1.40):
        g.box(f'Girls cabinet {i} provisional shelf', (0,0,z), (w-.048,.33,.024), g.M['oak'], .004, root)
    y += w
v['items'].extend(g.ITEMS)
for it in v['items']:
    if it['purpose'] == 'trundle_open':
        it['state'] = 'night-only; saved Blender opens in day mode'
v['checks'].update({'girls_cabinet_widths_mm':[800,800,600], 'girls_cabinet_total_run_mm':2200,
                    'girls_cabinet_fitting_tolerance_mm':0,
                    'girls_cabinet_full_door_depth_allowance_mm':400})
v['storage'].update({'existing_cupboards_physically_reused':1,
    'existing_full_cupboard_content_groups_retained':3,
    'girls_metal_cupboards_replaced':2,
    'girls_new_walnut_cabinets':3,
    'girls_new_inner_envelope_before_shelves_l':round(sum((w-.048)*.33*1.87*1000 for w in (.8,.8,.6))),
    'status':'Girls metal units replaced by three walnut units; all contents retained by allocation, actual capacity unresolved. Full hinged-door operation requires trundle stored.'})
v['storage'].pop('existing_cupboards', None)
data.update({'revision':4, 'parent':'03-wall-bounded-american-walnut/A-with-tv',
    'baseline_sha256':protected[BASE], 'variants':{'A-with-tv':v},
    'feasibility_status':'Conditional: 2200 mm cabinet run has zero spare fitting tolerance; full girls cabinet door access requires trundle stored; actual content/product/site fit unresolved.',
    'assumptions':[
        'Owner direction: TV on living west wall; girls wood cabinets 800 + 800 + 600 mm.',
        'American walnut carried forward. Girls cabinet depth 400 mm and height 2000 mm are provisional.',
        'Cabinets replace the prior girls metal pair; contents retained by allocation, metal carcasses have no in-home destination in this variant. No physical disposal authorized.',
        'Girls west-wall 2200 mm segment still interpreted as y=6.68..8.88 m, exact usable endpoints not site-confirmed. No gap or fitting tolerance within nominal segment.',
        'Pull-out bed access at foot: 910 mm. Side gap 270 mm is not a route. New hinged fronts also need trundle stored for full opening.',
        'Study layout, two freestanding 2000 mm Packout stacks and fixed south sliding wardrobe carried forward.',
        'TV stays on freestanding media cupboard; no wall, wiring, lighting or built-in changes.',
        'Actual TV/power points on west wall not mapped. NAS stays at prior west-wall port zone; exact port/cable positions unresolved.',
        'Furniture and storage interiors are dimensioned proxies, not selected products; no actual content-fit or cost approval.']})

# Keep comparison cameras, with a matching camera on the opposite side for west storage.
entry = bpy.data.objects['DESIGN living from entry']
storage_cam = bpy.data.objects['DESIGN living storage wall']
storage_cam.location = (living_width-.5, 5.2, 1.6)
storage_cam.rotation_euler = (Vector((living_width-4.7,6.15,1.1))-storage_cam.location).to_track_quat('-Z','Y').to_euler()
reverse = bpy.data.objects['DESIGN living towards seating']
reverse.location = (living_width-4.48,8.32,1.65)
reverse.rotation_euler = (Vector((living_width-1.9,5.95,.85))-reverse.location).to_track_quat('-Z','Y').to_euler()
seat_cam = g.camera('DESIGN seated sofa towards west TV', (3.98,6.45,1.12), (.24,7.44,1.38), 30)
girls_cam = bpy.data.objects['DESIGN girls wardrobe and west cupboards']
scene['design_version'] = 'variation04 west TV / girls 800 + 800 + 600 walnut cabinets'
scene['feasibility_status'] = data['feasibility_status']
scene['new_girls_cabinet_dimensions'] = '800/800/600 W owner direction; 400 D x 2000 H mm provisional'
scene.camera = entry
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.resolution_percentage = 60 if '--draft' in sys.argv else 100
scene.cycles.samples = 16 if '--draft' in sys.argv else 40
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A-with-tv.blend'))
(OUT/'layouts.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
if '--no-render' not in sys.argv:
    for cam,name in [(entry,'A-with-tv-living'),(storage_cam,'A-with-tv-living-storage'),
                     (reverse,'A-with-tv-living-reverse'),(seat_cam,'A-with-tv-seated-view'),
                     (bpy.data.objects['DESIGN girls day'],'shared-girls-day'),
                     (girls_cam,'shared-girls-storage')]:
        g.render(cam,name)
    trundle = bpy.data.objects['PULL-OUT lower mattress']
    trundle.location.x -= .95
    g.render(bpy.data.objects['DESIGN girls day'],'shared-girls-night')
    g.render(girls_cam,'shared-girls-storage-night')
    trundle.location.x += .95
    g.render(bpy.data.objects['DESIGN study freestanding stacks'],'shared-study')
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p,digest in protected.items())
print('VARIATION04_COMPLETE',OUT,flush=True)
