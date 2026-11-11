"""Independently compare saved variant architecture with saved source shell."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
REV4='--revision04' in sys.argv
REV3='--revision03' in sys.argv or REV4
REV2='--revision02' in sys.argv or REV3
OUT=Path(__file__).resolve().parent/'iterations'/('04-west-tv-three-walnut-cabinets' if REV4 else ('03-wall-bounded-american-walnut' if REV3 else ('02-wardrobe-and-full-height-packout' if REV2 else '01-family-room-triplets')))
if json.loads((OUT/'layouts.json').read_text(encoding='utf-8')).get('valid_for_current_brief') is False:
    raise SystemExit('Iteration 01 is superseded. Its historical unchanged-shell audit must not be presented as current room feasibility.')
def snapshot():
    result={}
    for c in bpy.data.collections:
        if c.name.startswith(('01 |','02 |','03 |','04 |','05 |','06 |','07 |')):
            for o in c.objects:
                if o.type=='MESH':
                    coords=[tuple(round(v,6) for v in (o.matrix_world@x.co)) for x in o.data.vertices]
                    result[o.name]=hashlib.sha256(repr(coords).encode()).hexdigest()
    return result
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model'/'223C_Existing_Shell_v02.blend'))
baseline=snapshot();checks=[]
for name in json.loads((OUT/'layouts.json').read_text(encoding='utf-8'))['variants']:
    bpy.ops.wm.open_mainfile(filepath=str(OUT/(name+'.blend')))
    actual=snapshot()
    differences=[k for k in set(baseline)|set(actual) if baseline.get(k)!=actual.get(k)]
    checks.append({'variant':name,'architecture_geometry_unchanged':not differences,'architecture_meshes':len(actual),'differences':differences})
    # Study storage is independently checked from actual transformed saved mesh vertices.
    furniture=bpy.data.collections.get('13 | Loose furniture — family room iteration 04' if REV4 else ('13 | Loose furniture — family room iteration 03' if REV3 else ('13 | Loose furniture — family room iteration 02' if REV2 else '13 | Loose furniture — family room iteration 01')))
    parts=[o for o in furniture.objects if o.type=='MESH' and o.parent and (o.parent.name=='REUSE study cupboard' or (REV2 and o.parent.name.startswith('PACKOUT stack')) or (not REV2 and o.parent.name=='NEW study equipment + archive'))]
    pts=[o.matrix_world@v.co for o in parts for v in o.data.vertices]
    low=min(v.y for v in pts);high=max(v.y for v in pts)
    checks[-1]['saved_study_wall_run_mm']=round((high-low)*1000,3)
    checks[-1]['study_within_2200']=high-low<=2.20001
    if REV2:
        roots=[o for o in furniture.objects if o.type=='EMPTY' and o.name.startswith('PACKOUT stack')]
        heights=[]
        for root in roots:
            p=[o.matrix_world@v.co for o in root.children if o.type=='MESH' for v in o.data.vertices]
            heights.append(round(max(v.z for v in p)*1000))
        checks[-1]['packout_render_heights_mm']=heights
        checks[-1]['packout_full_height']=len(heights)==2 and all(abs(h-2000)<=2 for h in heights)
        checks[-1]['packout_modules_per_stack']=[sum(' module ' in o.name for o in r.children) for r in roots]
        checks[-1]['packout_drawer_faces_per_stack']=[sum('drawer face' in o.name for o in r.children) for r in roots]
        checks[-1]['packout_cabinet_fronts_per_stack']=[sum('cabinet front' in o.name for o in r.children) for r in roots]
        checks[-1]['packout_composition_checked']=all(n==5 for n in checks[-1]['packout_modules_per_stack']) and all(n==11 for n in checks[-1]['packout_drawer_faces_per_stack']) and all(n==2 for n in checks[-1]['packout_cabinet_fronts_per_stack'])
        ward=bpy.data.objects.get('FIXED SLIDING WARDROBE')
        checks[-1]['fixed_wardrobe_retained']=ward is not None and list(ward['dimensions_mm'])[:2]==[1867,600]
    if REV3:
        cupboard_parts=[o for o in furniture.objects if o.type=='MESH' and o.parent and o.parent.name.startswith(('NEW toy','NEW archive'))]
        p=[o.matrix_world@v.co for o in cupboard_parts for v in o.data.vertices]
        bounds=[min(v.y for v in p),max(v.y for v in p)]
        checks[-1]['actual_living_cupboard_y_bounds']=bounds
        checks[-1]['living_cupboards_within_wall']=bounds[0]>=5.55 and bounds[1]<=8.486667
        doors=[o for o in cupboard_parts if ' door ' in o.name]
        checks[-1]['new_cupboard_fronts_american_walnut']=bool(doors) and all(any('American walnut' in m.name for m in o.data.materials) for o in doors)
    if REV4:
        roots=sorted((o for o in furniture.objects if o.type=='EMPTY' and o.name.startswith('NEW girls walnut cabinet')),key=lambda o:o.name)
        sizes=[];all_pts=[];fronts=[]
        for root in roots:
            pts=[o.matrix_world@vertex.co for o in root.children if o.type=='MESH' for vertex in o.data.vertices]
            all_pts.extend(pts)
            sizes.append([round((max(v.y for v in pts)-min(v.y for v in pts))*1000),round((max(v.x for v in pts)-min(v.x for v in pts))*1000)])
            fronts.extend(o for o in root.children if ' door ' in o.name)
        checks[-1]['girls_actual_saved_width_depth_mm']=sizes
        checks[-1]['girls_three_cabinet_dimensions_match']=sizes==[[800,400],[800,400],[600,400]]
        checks[-1]['girls_actual_y_bounds']=[min(v.y for v in all_pts),max(v.y for v in all_pts)]
        checks[-1]['girls_nominal_2200_segment_respected']=min(v.y for v in all_pts)>=6.68-1e-5 and max(v.y for v in all_pts)<=8.88+1e-5
        checks[-1]['girls_new_fronts_american_walnut']=len(fronts)==6 and all(any('American walnut' in m.name for m in o.data.materials) for o in fronts)
        tv=bpy.data.objects['TV 65-inch PROXY']
        tvpts=[o.matrix_world@vertex.co for o in tv.children if o.type=='MESH' for vertex in o.data.vertices]
        checks[-1]['saved_tv_at_west_wall']=max(v.x for v in tvpts)<.55
        checks[-1]['girls_full_door_access_with_trundle_open']=False
        checks[-1]['scope_note']='Saved geometry check only; exact site 2200 mm segment, interior capacity and night cupboard access unresolved.'
report={'all_pass':all(c['architecture_geometry_unchanged'] and c['study_within_2200'] and (not REV2 or (c['packout_full_height'] and c['fixed_wardrobe_retained'] and c['packout_composition_checked'])) for c in checks),'checks':checks}
if REV3:report['all_pass']=report['all_pass'] and all(c['living_cupboards_within_wall'] and c['new_cupboard_fronts_american_walnut'] for c in checks)
if REV4:report['all_pass']=report['all_pass'] and all(c['girls_three_cabinet_dimensions_match'] and c['girls_nominal_2200_segment_respected'] and c['girls_new_fronts_american_walnut'] and c['saved_tv_at_west_wall'] for c in checks)
(OUT/'saved_file_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2));assert report['all_pass']
