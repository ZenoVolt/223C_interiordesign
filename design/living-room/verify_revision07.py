"""Saved geometry audit: owner product dimensions, 360 setback and retained viewing."""
import bpy,json,math,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;OUT=HERE/'iterations'/'07-product-modules-360-setback'
BASE=HERE.parents[1]/'model'/'223C_Existing_Shell_v02.blend'
data=json.loads((OUT/'layouts.json').read_text(encoding='utf-8'));v=next(iter(data['variants'].values()));checks=[]
def check(name,ok,detail):checks.append({'name':name,'pass':bool(ok),'detail':detail})
def snapshot():
    return {o.name:hashlib.sha256(repr([tuple(round(x,6) for x in o.matrix_world@p.co) for p in o.data.vertices]).encode()).hexdigest() for c in bpy.data.collections if c.name.startswith(('01 |','02 |','03 |','04 |','05 |','06 |','07 |')) for o in c.objects if o.type=='MESH'}
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
bpy.ops.wm.open_mainfile(filepath=str(OUT/'V7-product-modules.blend'))
check('Architecture geometry unchanged',snapshot()==baseline,{'meshes':len(baseline)})
check('Baseline file unchanged',hashlib.sha256(BASE.read_bytes()).hexdigest()==data['baseline_sha256'],data['baseline_sha256'])
f=bpy.data.collections['13 | Loose furniture — family room iteration 07']
roots=[o for o in f.objects if o.type=='EMPTY' and o.name.startswith(('WEST STORAGE','RETURN STORAGE','NEW girls walnut','L CORNER'))]
bb={o.name:bounds(o.children) for o in roots}
main=sorted((o for o in roots if o.name.startswith('WEST STORAGE')),key=lambda o:o.name)
check('Five real-width west modules, 800 each',len(main)==5 and all(abs(bb[o.name][4]-bb[o.name][1]-.8)<1e-5 for o in main),[round((bb[o.name][4]-bb[o.name][1])*1000) for o in main])
depths={o.name:(bb[o.name][3]-bb[o.name][0] if o.name.startswith('WEST STORAGE') else bb[o.name][4]-bb[o.name][1]) for o in roots if o.name.startswith(('WEST STORAGE','RETURN STORAGE'))}
check('Living straight cabinets 350 deep',all(abs(depth-.35)<1e-5 for depth in depths.values()),{n:round(depth*1000,3) for n,depth in depths.items()})
check('All ten tall cabinets 2350 high',len(roots)==10 and all(abs(b[5]-2.35)<1e-5 for b in bb.values()),{n:round(b[5]*1000) for n,b in bb.items()})
check('Girls widths 800/800/600 retained',sorted(round((bb[o.name][4]-bb[o.name][1])*1000) for o in roots if o.name.startswith('NEW girls'))==[600,800,800],'Girls 400 mm depth remains provisional')
co=bb['L CORNER 630 x 630 OPEN']
check('Real corner reservation 630 by 630',abs(co[3]-co[0]-.63)<1e-5 and abs(co[4]-co[1]-.63)<1e-5,{'bounds':co,'note':'Interior L contour / staggered dividers remain illustrative'})
check('Invented blind void/filler removed',bpy.data.objects.get('BLIND CORNER / NO STORAGE CREDIT') is None and bpy.data.objects.get('CORNER JOIN FILLER') is None,'Actual open corner is now in the inventory')
end=max(bb[o.name][4] for o in main);start=min(bb[o.name][1] for o in main)
check('North setback exactly 360',abs(8.486667-end-.36)<1e-5,{'north_setback_mm':(8.486667-end)*1000,'main_end_y':end})
check('West chain fits measured 5040 shell depth',abs(co[1]-3.446667-.04)<1e-5 and abs(start-co[4]-.01)<1e-5 and abs(end-start-4)<1e-5,{'chain_mm':[40,630,10,4000,360],'sum_mm':5040})
ret=bb['RETURN STORAGE L1']
check('800 return within short backing wall',abs(ret[3]-ret[0]-.8)<1e-5 and ret[3]<=1.533333 and abs(ret[0]-co[3]-.01)<1e-5,{'east_end_gap_mm':(1.533333-ret[3])*1000,'join_gap_mm':(ret[0]-co[3])*1000})
arch=[o for c in bpy.data.collections if c.name.startswith(('02 |','03 |','06 |','07 |')) for o in c.objects if o.type=='MESH']
hits=[[n,o.name] for n,b in bb.items() for o in arch if intersect(b,bounds([o]))]
check('All new tall cabinet meshes clear existing walls/beams',not hits,hits)
check('Server remains removed',bpy.data.objects.get('RETAINED R6 NAS') is None and not any('R6' in it['name'] for it in v['items']),'Owner instruction carried forward')
panes=[o for r in roots for o in r.children if 'REEDED GLASS' in o.name]
check('Reference door designs retained',len(panes)==32 and sum(o.name.startswith('Girls 600 drawer') for o in bpy.data.objects)==4,'Six straight living units x four glass panels; two girls 800 units x four; 600 open/drawers; real corner open')
face=bounds([bpy.data.objects['77 TV display face']]);eye=bpy.data.objects['DESIGN V6 seated eye 3180 mm'].location
check('77-inch visible screen retained',abs(math.hypot(face[4]-face[1],face[5]-face[2])/.0254-77)<.001,{'visible_diagonal_inches':math.hypot(face[4]-face[1],face[5]-face[2])/.0254})
check('3180 mm seated-eye viewing distance retained',abs(face[0]-eye.x-3.18)<1e-5 and abs((face[1]+face[4])/2-eye.y)<1e-5,{'eye_to_screen_mm':(face[0]-eye.x)*1000})
console=bounds(bpy.data.objects['EAST TV CONSOLE 2000 x 450 x 550'].children);tv=bounds(bpy.data.objects['TV 77-inch 16-by-9 PROXY'].children)
check('TV/console clear walls and beams',not any(intersect(console,bounds([o])) or intersect(tv,bounds([o])) for o in arch),'East wall arrangement unchanged from version 6')
its=v['items'];collisions=[]
for j,it in enumerate(its):
    for other in its[j+1:]:
        if it['room']==other['room'] and it['purpose']!='screen' and other['purpose']!='screen' and overlap(it['polygon'],other['polygon']):collisions.append([it['name'],other['name']])
check('No unintended night-state furniture footprint overlaps',not collisions,collisions)
sofa=next(i for i in its if i['name'].startswith('SOFA'));gap=min(p[0] for p in sofa['polygon'])-max(bb[o.name][3] for o in main)
check('Rear sofa gap recomputed to about 807',abs(gap-.806667)<.001,{'closed_gap_mm':gap*1000,'remaining_with_400_leaf_mm':(gap-.4)*1000,'comfort':'Unresolved; sequential use'})
door_hits=[]
for it in its:
    if not it['name'].startswith('WEST STORAGE'):continue
    front=max(p[0] for p in it['polygon']);y0=min(p[1] for p in it['polygon']);y1=max(p[1] for p in it['polygon'])
    for hinge,start_ang,end_ang in ((y0,0,90),(y1,-90,0)):
        sector=[(front,hinge)]+[(front+.4*math.cos(math.radians(t)),hinge+.4*math.sin(math.radians(t))) for t in range(start_ang,end_ang+1)]
        door_hits.extend([it['name'],j['name']] for j in its if j['room']=='living' and j is not it and j['purpose']!='screen' and overlap(sector,j['polygon']))
check('West 400 mm door sectors clear other furniture',not door_hits,door_hits)
a,b,c,d=v['play_rect'];play=[(a,b),(c,b),(c,d),(a,d)]
check('1850 by 1750 floor-play footprint clear',not any(overlap(play,i['polygon']) for i in its if i['room']=='living' and i['purpose']!='screen'),{'area_m2':(c-a)*(d-b)})
check('All retained content groups and 21 boxes allocated',v['storage']['existing_full_cupboard_content_groups_retained']==3 and v['storage']['samla_contents_boxes']==21,'Actual usable capacity reopened at 350 depth; no numeric capacity approval')
check('Fixed sliding wardrobe retained',bpy.data.objects.get('FIXED SLIDING WARDROBE') is not None,'600 deep existing bay reserved')
pack=[o for o in f.objects if o.type=='EMPTY' and o.name.startswith('PACKOUT stack')]
check('Two full-height Packout stacks retained',len(pack)==2 and all(abs(bounds(r.children)[5]-2)<.002 for r in pack),'Study unchanged')
foot=[(8.85,6.15),(10.75,6.15),(10.75,7.06),(8.85,7.06)]
check('Girls 910 mm foot band free in night mode',not any(overlap(foot,i['polygon']) for i in its if i['room']=='girls'),'270 side gap is not a route; cupboard use remains restricted')
for room,hx,hy,radius,start_ang,end_ang in [('girls',8.255,5.5,.9517,0,88),('study',7.9,5.5,.9533,92,180),('living',1.44,2.685,.71,-92,0)]:
    sector=[(hx,hy)]+[(hx+radius*math.cos(math.radians(t)),hy+radius*math.sin(math.radians(t))) for t in range(start_ang,end_ang+1)]
    hit=[i['name'] for i in its if i['room']==room and i['purpose']!='screen' and overlap(sector,i['polygon'])]
    check(room+' modelled door swing clear',not hit,hit)
report={'all_pass':all(c['pass'] for c in checks),'checks':checks,'overall_feasibility':'Conditional model proposal; geometry passes do not approve site/products/content or household comfort.',
    'full_girls_cupboard_access_with_trundle_open':False,
    'unresolved':['Actual straight/corner product drawings, connector clearances and shelf contours; internal dimensions and load capacities',
        'Reduced living depth 350: repack allowed, but actual retained-content fit must be checked again',
        'Girls actual depth (400 proxy), exact usable 2200 wall/fitting tolerances and door/drawer travel with bed open',
        '807 rear sofa gap / 407 with 400 door leaf: sequential access and household comfort unverified',
        'Actual TV/console feet and sofa seated-eye/posture; recliner full operating envelope and guest routes',
        'Tall-unit support/restraint, glazing/hinges/knobs and installed beam/ceiling/site verification',
        'Product cost in SGD, delivery/installation; replaced metal carcass destination']}
(OUT/'fit_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'all_pass':report['all_pass'],'checks':len(checks),'failures':[c for c in checks if not c['pass']]},indent=2));assert report['all_pass']
