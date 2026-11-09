"""Independent geometry measurements on the saved .blend, via wall raycasts."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
cfg=json.loads((root/'model_settings.json').read_text(encoding='utf-8'))
blend_path=root/cfg['blend_filename']
bpy.ops.wm.open_mainfile(filepath=str(blend_path))
dg=bpy.context.evaluated_depsgraph_get()
walls=[o for name in ('02 | Concrete walls — existing','03 | Interior walls — existing') for o in bpy.data.collections[name].objects if o.type=='MESH']
trees=[(o,BVHTree.FromObject(o,dg)) for o in walls]

def cast(origin,direction):
    closest=None
    for o,tree in trees:
        inv=o.matrix_world.inverted()
        local_origin=inv@origin
        local_dir=(inv.to_3x3()@direction).normalized()
        hit,normal,index,distance=tree.ray_cast(local_origin,local_dir,50)
        if hit is not None:
            world=o.matrix_world@hit
            distance=(world-origin).length
            if closest is None or distance<closest[0]:closest=(distance,o.name,tuple(world))
    if closest is None:raise RuntimeError('No wall hit from '+str(origin)+' along '+str(direction))
    return closest

# Positions select clear parts of rooms, away from openings and swung leaves.
cases=[
 ('Living width',450,480,'X',5070),
 ('Living depth above maid room',185,500,'Y',5040),
 ('Study upper width',1070,330,'X',2670),
 ('Study depth',1000,330,'Y',3610),
 ('Girls upper width',1490,330,'X',2670),
 ('Girls depth',1530,330,'Y',3610),
 ('Master upper width',1965,330,'X',2850),
 ('Master depth',1965,490,'Y',4220),
 ('Maid width',185,1200,'X',1240),
 ('Maid depth',185,1100,'Y',2285),
 ('Kitchen south width',923,1370,'X',4470),
 ('Bathroom 1 width',1450,973,'X',1800),
 ('Bathroom 2 width',1784,973,'X',2215),
 ('Bathroom 1 depth',1550,973,'Y',1710),
 ('Bathroom 2 depth',1900,973,'Y',1710)
]
results=[]
for name,px,py,axis,target in cases:
    origin=Vector(((px-76)/150,(1450-py)/150,.3))
    direction=Vector((1,0,0) if axis=='X' else (0,1,0))
    a,b=cast(origin,direction),cast(origin,-direction)
    length=(a[0]+b[0])*1000
    results.append({'measurement':name,'actual_mm':round(length,3),'plan_mm':target,'error_mm':round(length-target,3),'pass':abs(length-target)<=5.01,'hit_walls':[a[1],b[1]]})

corrections=[]
def correction(name,passed,detail):
    corrections.append({'check':name,'pass':bool(passed),'detail':detail})

east_x=(1490-76)/150
for py in (1130,1280,1430):
    wall_hits=[]
    for z in (.99,1.01,2.21):
        origin=Vector(((1400-76)/150,(1450-py)/150,z))
        try:hit=cast(origin,Vector((1,0,0)))
        except RuntimeError:hit=None
        wall_hits.append(hit)
    correction('Service east opening at source Y '+str(py),
               wall_hits[0] is not None and abs(wall_hits[0][2][0]-east_x)<.001 and wall_hits[1] is None and wall_hits[2] is not None,
               'Wall at 990 mm; clear opening at 1010 mm; wall above 2200 mm head.')
south=cast(Vector(((1400-76)/150,(1450-1280)/150,1.5)),Vector((0,-1,0)))
correction('Service south wall is solid',abs(south[2][1])<.001,south[1])
service=bpy.data.objects['Service yard EAST three-panel slider | window assembly']
panes=[o for o in service.children if 'sliding glass' in o.name]
correction('Service window contains three sliding panes',len(panes)==3,len(panes))

hinges={name:bpy.data.objects[name+' | hinge (rotate Z)'] for name in ('Maid room door','Study door','Girls bedroom door','Master bedroom door')}
maid=hinges['Maid room door'];maid_leaf=bpy.data.objects['Maid room door | leaf']
correction('Maid door swings outward east of its wall',maid_leaf.matrix_world.translation.x>maid.location.x+.2,tuple(maid_leaf.matrix_world.translation))
study=hinges['Study door'];girls=hinges['Girls bedroom door']
correction('Study hinge at unchanged doorway east jamb',abs(study.location.x-(1261-76)/150)<1e-5,tuple(study.location))
correction('Girls hinge at unchanged doorway west jamb',abs(girls.location.x-(1314.25-76)/150)<1e-5,tuple(girls.location))
master=hinges['Master bedroom door']
master_source_px=master.location.x*150+76
correction('Master upper hinge centred on 145 mm segment',abs(master_source_px-1530.375)<.01 and abs(master.location.y-(1450-632.5)/150)<1e-5,{'source_x_px':master_source_px,'source_y_px':1450-master.location.y*150})
correction('Old master west doorway removed',not any(o.name.startswith('Master west short return') for o in walls),'No previously inferred west-wall doorway retained.')

summary={
    'file':str(blend_path),
    'method':'Independent BVH raycasts of evaluated wall geometry in the saved file; excludes door leaves, windows, labels and hidden cutters.',
    'tolerance_mm':5,
    'all_pass':all(r['pass'] for r in results) and all(c['pass'] for c in corrections),
    'measurements':results,
    'owner_correction_checks':corrections,
    'scene_units':bpy.context.scene.unit_settings.system,
    'ceiling_datum_mm':bpy.context.scene['ceiling_datum_mm'],
    'loose_furniture_collection_empty':len(bpy.data.collections['13 | Loose furniture — empty for next iteration'].objects)==0,
    'packed_reference_count':sum(1 for im in bpy.data.images if im.packed_file),
    'camera_count':sum(1 for o in bpy.data.objects if o.type=='CAMERA')
}
(root/'geometry_audit.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
assert summary['all_pass'], 'A measured room dimension differs from the plan by more than 5 mm'
assert summary['ceiling_datum_mm']==2580
assert summary['packed_reference_count']==2
print('SAVED_MODEL_GEOMETRY_VERIFIED')
