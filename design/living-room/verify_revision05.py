"""Independent saved-file geometry / operational audit for version 5, in Blender."""
import bpy, hashlib, json, math, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REV6='--revision06' in sys.argv
OUT=HERE/'iterations'/('06-east-tv-reference-cabinets' if REV6 else '05-full-west-storage-l-return')
BASE=HERE.parents[1]/'model'/'223C_Existing_Shell_v02.blend'
REF='--reference' in sys.argv or REV6
data=json.loads((OUT/('layouts-reference.json' if REF and not REV6 else 'layouts.json')).read_text(encoding='utf-8'))
v=next(iter(data['variants'].values()));checks=[]
def check(name,ok,detail):checks.append({'name':name,'pass':bool(ok),'detail':detail})
def snapshot():
    return {o.name:hashlib.sha256(repr([tuple(round(x,6) for x in o.matrix_world@v.co) for v in o.data.vertices]).encode()).hexdigest()
        for c in bpy.data.collections if c.name.startswith(('01 |','02 |','03 |','04 |','05 |','06 |','07 |')) for o in c.objects if o.type=='MESH'}
def bounds(objects):
    pts=[o.matrix_world@p.co for o in objects if o.type=='MESH' for p in o.data.vertices]
    return [min(p[i] for p in pts) for i in range(3)]+[max(p[i] for p in pts) for i in range(3)]
def intersect(a,b):return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-5 for i in range(3))
def overlap(a,b):
    for p in (a,b):
        for i in range(len(p)):
            u,w=p[i],p[(i+1)%len(p)];axis=(-(w[1]-u[1]),w[0]-u[0])
            aa=[x*axis[0]+y*axis[1] for x,y in a];bb=[x*axis[0]+y*axis[1] for x,y in b]
            if max(aa)<=min(bb)+1e-5 or max(bb)<=min(aa)+1e-5:return False
    return True

bpy.ops.wm.open_mainfile(filepath=str(BASE));baseline=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(OUT/('V6-east-tv.blend' if REV6 else ('V5-reference-cabinets.blend' if REF else 'V5-no-tv.blend'))))
check('Architecture unchanged',snapshot()==baseline,{'meshes':len(baseline)})
check('Baseline bytes unchanged',hashlib.sha256(BASE.read_bytes()).hexdigest()==data['baseline_sha256'],data['baseline_sha256'])
if not REV6:check('TV completely removed',not any('TV ' in o.name for o in bpy.data.objects) and not any(i['purpose']=='screen' for i in v['items']),'No screen or stand object remains')
f=bpy.data.collections['13 | Loose furniture — family room iteration 06' if REV6 else '13 | Loose furniture — family room iteration 05']
roots=[o for o in f.objects if o.type=='EMPTY' and o.name.startswith(('WEST STORAGE','RETURN STORAGE','NEW girls walnut'))]
bb={o.name:bounds(o.children) for o in roots}
check('All ten new storage cabinets exactly 2400 high',len(roots)==10 and all(abs(b[5]-2.4)<1e-5 for b in bb.values()),{n:round(b[5]*1000,2) for n,b in bb.items()})
main=sorted((o for o in roots if o.name.startswith('WEST STORAGE')),key=lambda o:o.name)
check('Six 700 mm west modules',len(main)==6 and all(abs(bb[o.name][4]-bb[o.name][1]-.7)<1e-5 for o in main),'4200 mm main cabinet frontage')
check('Girls widths remain 800 / 800 / 600',sorted(round((bb[o.name][4]-bb[o.name][1])*1000) for o in roots if o.name.startswith('NEW girls'))==[600,800,800],'All now 2400 H; 400 D remains provisional')
check('All new fronts American walnut',all(any('American walnut' in m.name for m in o.data.materials) for r in roots for o in r.children if ' door ' in o.name or 'upper door ' in o.name),'Procedural illustration carried forward')
arch=[o for c in bpy.data.collections if c.name.startswith(('02 |','03 |','06 |','07 |')) for o in c.objects if o.type=='MESH']
hits=[]
for name,b in bb.items():
    for o in arch:
        if intersect(b,bounds([o])):hits.append([name,o.name])
check('New cabinet meshes clear walls, beams and false ceiling',not hits,hits)
beam=bpy.data.objects['B01 | Living north window beam']
beam_b=bounds([beam]);north=max(bb[o.name][4] for o in main)
check('2400 high north end clears low beam',north<beam_b[1]-1e-5,{'cabinet_end_y':north,'beam_start_y':beam_b[1],'gap_mm':round((beam_b[1]-north)*1000),'beam_underside_mm':round(beam_b[2]*1000)})
ret=bb['RETURN STORAGE L1']
check('Return ends before L wall endpoint',ret[3]<1.533333,{'return_x_end':ret[3],'wall_end_x':1.533333,'end_gap_mm':round((1.533333-ret[3])*1000)})

# R6 is intentionally inside W1, with vertical separation from storage above.
if REF:
    check('Server removed from living model and allocation',bpy.data.objects.get('RETAINED R6 NAS') is None and not any('R6' in i['name'] for i in v['items']),'Owner instruction overrides prior living retention; no destination elsewhere assumed')
    panes=[o for r in roots for o in r.children if 'REEDED GLASS' in o.name]
    check('Reference glass layouts: 28 living + 8 girls panels',len(panes)==36 and sum('Living' in o.name for o in panes)==28,'Seven living units each main/upper pair; two 800 girls units each main/upper pair; 600 unit open')
    check('600 girls reference uses four drawers',sum(o.name.startswith('Girls 600 drawer') for o in bpy.data.objects)==4,'Open shelves above; two 800 units have niches and lower closed doors')
else:
    nas=bpy.data.objects['RETAINED R6 NAS'];n=bounds(nas.children);w=bb['WEST STORAGE W1']
    check('NAS body inside open W1 bay',n[0]>=w[0]+.024 and n[3]<=w[3]-.024 and n[1]>=w[1]+.024 and n[4]<=w[4]-.024 and n[5]<=.635,
        {'body_bounds':n,'note':'Body containment only; cable bend, airflow and service not approved'})
check('Three retained cupboard content groups and 21 box contents allocated',v['storage']['existing_full_cupboard_content_groups_retained']==3 and v['storage']['samla_contents_boxes']==21,'New living west/return storage holds toys/archive; girls units hold prior metal-pair contents; study metal retained')
check('Blind corner excluded from usable capacity',v['storage']['blind_corner_capacity_credit_l']==0,'No shelves or contents credited')
check('Fixed south wardrobe retained',bpy.data.objects.get('FIXED SLIDING WARDROBE') is not None,'Sliding / 600 D retained')
pack=[o for o in f.objects if o.type=='EMPTY' and o.name.startswith('PACKOUT stack')]
check('Two 2000 high Packout stacks retained',len(pack)==2 and all(abs(bounds(r.children)[5]-2)<.002 for r in pack),'Study arrangement unchanged')

its=v['items'];collisions=[]
for j,it in enumerate(its):
    for other in its[j+1:]:
        if it['room']!=other['room']:continue
        if it['purpose']=='screen' or other['purpose']=='screen':continue
        if {it['name'],other['name']}=={'RETAINED R6 NAS','WEST STORAGE W1'}:continue
        if overlap(it['polygon'],other['polygon']):collisions.append([it['name'],other['name']])
check('No unintended proxy footprint overlaps in night mode',not collisions,collisions)
a,b,c,d=v['play_rect'];play=[(a,b),(c,b),(c,d),(a,d)]
check('Marked floor-play zone free with cabinets closed',not any(overlap(play,it['polygon']) for it in its if it['room']=='living'),{'area_m2':round((c-a)*(d-b),2)})
foot=[(8.85,6.15),(10.75,6.15),(10.75,7.06),(8.85,7.06)]
check('Girls 910 mm bed-foot band remains free',not any(overlap(foot,it['polygon']) for it in its if it['room']=='girls'),'270 mm side gap is not a walking route')
for room,hx,hy,radius,start,end in [('girls',8.255,5.5,.9517,0,88),('study',7.9,5.5,.9533,92,180),('living',1.44,2.685,.71,-92,0)]:
    sector=[(hx,hy)]+[(hx+radius*math.cos(math.radians(t)),hy+radius*math.sin(math.radians(t))) for t in range(start,end+1)]
    hit=[it['name'] for it in its if it['room']==room and overlap(sector,it['polygon'])]
    check(room+' modelled door swing clear',not hit,hit)
# Main west doors: 350 mm leaves. Each sector is checked against other furniture.
door_hits=[]
for it in its:
    if it['name'].startswith('WEST STORAGE'):
        front=max(p[0] for p in it['polygon']);y0=min(p[1] for p in it['polygon']);y1=max(p[1] for p in it['polygon'])
        for hinge,start,end in [(y0,0,90),(y1,-90,0)]:
            sector=[(front,hinge)]+[(front+.35*math.cos(math.radians(t)),hinge+.35*math.sin(math.radians(t))) for t in range(start,end+1)]
            door_hits.extend([it['name'],j['name']] for j in its if j['room']=='living' and j is not it and j['purpose']!='equipment_in_bay' and overlap(sector,j['polygon']))
check('West 350 mm hinged-leaf sectors clear other furniture',not door_hits,door_hits)
report={'all_pass':all(c['pass'] for c in checks),'checks':checks,
    'overall_feasibility':'Conditional; passed model geometry does not establish site, contents or product feasibility.',
    'full_girls_cabinet_access_with_trundle_open':False,
    'unresolved':['Site verification of north beam underside/projection and installed ceiling; 2400 H has 180 mm to unfinished ceiling only',
        'Actual cabinet products, level/fitting tolerances, tall-unit support/restraint details within scope',
        'Girls 2200 mm usable segment has zero spare fitting tolerance; confirm depth and retained content capacity',
        'Girls full hinged opening requires trundle stored; restriction still awaiting acceptance',
        'NAS cable/airflow/service access and exact existing west port positions',
        'No storage capacity credited to blind corner; corner join/adjacent door hardware to verify',
        'Actual recliner full recline/footstool envelopes and family/guest circulation preferences',
        'Actual contents/shelf loads, product costs and replaced metal carcass destination']}
if REF:
    report['unresolved']=[s for s in report['unresolved'] if 'NAS' not in s]
    report['unresolved'].extend(['Reference glass/frames/hinges/knobs are visual proxies; actual product and suitable glazing selection unresolved','Girls 600 drawer travel and 800 hinged doors require bed-state access verification; night side gap remains 270 mm'])
if REV6:
    face=bounds([bpy.data.objects['77 TV display face']]);eye=bpy.data.objects['DESIGN V6 seated eye 3180 mm'].location
    diagonal=math.hypot(face[4]-face[1],face[5]-face[2])/.0254
    check('Actual visible screen diagonal is 77 inches',abs(diagonal-77)<.001,{'diagonal_inches':diagonal,'visible_width_mm':(face[4]-face[1])*1000,'visible_height_mm':(face[5]-face[2])*1000})
    check('Saved camera eye is 3180 mm from screen front',abs(face[0]-eye.x-3.18)<1e-5 and abs((face[1]+face[4])/2-eye.y)<1e-5,{'horizontal_distance_mm':(face[0]-eye.x)*1000,'seated_eye':list(eye),'screen_front_x':face[0]})
    console=bounds(bpy.data.objects['EAST TV CONSOLE 2000 x 450 x 550'].children)
    tv=bounds(bpy.data.objects['TV 77-inch 16-by-9 PROXY'].children)
    check('East console inside backing-wall endpoints',console[1]>=5.55 and console[4]<=8.486667 and console[3]<5.073333,{'actual_console_bounds':console})
    check('TV and feet remain inside console top footprint',tv[0]>=console[0] and tv[3]<=console[3] and tv[1]>=console[1] and tv[4]<=console[4],{'actual_tv_bounds':tv})
    hits=[o.name for o in arch if intersect(console,bounds([o])) or intersect(tv,bounds([o]))]
    check('TV and console actual meshes clear walls and beams',not hits,hits)
    sofa=next(i for i in its if i['name'].startswith('SOFA'))
    gap=min(p[0] for p in sofa['polygon'])-max(bb[o.name][3] for o in main)
    check('Rear sofa storage gap recomputed',abs(gap-.656667)<.001,{'rear_gap_mm':gap*1000,'remaining_when_350_mm_leaf_open_mm':(gap-.35)*1000,'status':'Geometry only; sequential use and household comfort unresolved'})
    report['all_pass']=all(c['pass'] for c in checks)
    report['unresolved'].extend(['3180 mm assumes modelled seated eye 100 mm ahead of sofa centre; actual sofa/posture/TV feet need confirmation','657 mm behind sofa / 307 mm with 350 mm door open: storage access is tight, comfort not approved','Actual reclined envelope, guest placement and east TV power/AV positions unresolved'])
(OUT/('fit_checks.json' if REV6 else ('fit_checks-reference.json' if REF else 'fit_checks.json'))).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2));assert report['all_pass']
