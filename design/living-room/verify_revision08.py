"""Independent saved-file audit of V8 geometry and explicit feasibility limits."""
import bpy,hashlib,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent;OUT=HERE/'iterations'/'08-west-av-east-storage'
PARENT=HERE/'iterations'/'07-product-modules-360-setback'/'V7-product-modules.blend'
BASE=HERE.parents[1]/'model'/'223C_Existing_Shell_v02.blend'
data=json.loads((OUT/'layouts.json').read_text(encoding='utf-8'));v=next(iter(data['variants'].values()));checks=[]
def check(name,ok,detail):checks.append({'name':name,'pass':bool(ok),'detail':detail})
def snapshot(room=None):
    meshes=[]
    if room:
        meshes=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.get('room')==room]
    else:meshes=[o for c in bpy.data.collections if c.name.startswith(('01 |','02 |','03 |','04 |','05 |','06 |','07 |')) for o in c.objects if o.type=='MESH']
    return {o.name:hashlib.sha256(repr([tuple(round(x,6) for x in o.matrix_world@p.co) for p in o.data.vertices]).encode()).hexdigest() for o in meshes}
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
bpy.ops.wm.open_mainfile(filepath=str(PARENT));arch_parent=snapshot();girls=snapshot('girls');study=snapshot('study')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'V8-west-av-east-storage.blend'))
check('Architecture unchanged from preserved V7',snapshot()==arch_parent,{'meshes':len(arch_parent)})
check('Girls room geometry unchanged',snapshot('girls')==girls,{'meshes':len(girls),'height_mm':2350,'depth_status':'400 proxy'})
check('Study geometry unchanged',snapshot('study')==study,{'meshes':len(study)})
check('Parent and source bytes preserved',hashlib.sha256(PARENT.read_bytes()).hexdigest()==data['parent_sha256'] and hashlib.sha256(BASE.read_bytes()).hexdigest()==data['baseline_sha256'],'Existing shell and V7 untouched')
its=v['items'];living=[i for i in its if i['room']=='living'];roots={i['name']:bpy.data.objects[i['name']] for i in living}
bb={n:bounds(r.children) for n,r in roots.items()}
east=[i for i in living if i['name'].startswith('EAST STORAGE')]
check('East wall has exactly three 900 mm cabinets',len(east)==3 and all(abs(bb[i['name']][4]-bb[i['name']][1]-.9)<1e-5 for i in east),'2700 mm tall run; quantity is current hypothesis')
check('East cabinets retain 350 D / 2350 H',all(abs(bb[i['name']][3]-bb[i['name']][0]-.35)<1e-5 and abs(bb[i['name']][5]-2.35)<1e-5 for i in east),'Actual transformed saved meshes')
check('Former west/return/corner storage removed',not any(i['name'].startswith(('WEST STORAGE','RETURN STORAGE','L CORNER')) for i in living),'Storage scope changed; former capacity claims withdrawn')
limits=[5.55,8.486667];ey=[min(bb[i['name']][1] for i in east),max(bb[i['name']][4] for i in east)]
check('East cabinets within backing wall',ey[0]>=limits[0] and ey[1]<=limits[1],{'wall_y':limits,'cabinet_y':ey})
beam=bounds([bpy.data.objects['B01 | Living north window beam']])
check('East high cabinets clear north beam',ey[1]<beam[1],{'gap_mm':(beam[1]-ey[1])*1000,'beam_underside_mm':beam[2]*1000})
face=bounds([bpy.data.objects['77 TV display face']]);outer=bounds([bpy.data.objects['77 TV thin panel']])
console=bb['WEST TV CONSOLE ratio 3-to-2'];tv=bb['TV 77-inch 16-by-9 PROXY'];eye=bpy.data.objects['DESIGN V8 seated eye 3180 mm'].location
check('Visible TV diagonal remains 77 inches',abs(math.hypot(face[4]-face[1],face[5]-face[2])/.0254-77)<.001,{'diagonal_inches':math.hypot(face[4]-face[1],face[5]-face[2])/.0254})
check('Physical TV width is exactly two thirds console',abs((outer[4]-outer[1])/(console[4]-console[1])-2/3)<1e-5,{'tv_outer_width_mm':(outer[4]-outer[1])*1000,'console_width_mm':(console[4]-console[1])*1000})
check('3180 mm west screen-to-seated-eye distance',abs(eye.x-face[3]-3.18)<1e-5 and abs(eye.y-(face[1]+face[4])/2)<1e-5,{'eye':list(eye),'screen_front_x':face[3],'horizontal_distance_mm':(eye.x-face[3])*1000})
cy=sum(v['rooms']['living'][j] for j in (1,3))/2
speakers=[i for i in living if i['purpose']=='speaker']
check('AV centred on full west wall',abs((console[1]+console[4])/2-cy)<1e-5 and abs((face[1]+face[4])/2-cy)<1e-5 and abs(sum(i['centre'][1] for i in speakers)/2-cy)<1e-5,{'wall_midpoint_y':cy})
check('Two KEF Q11 Meta full envelopes modelled',len(speakers)==2 and all(i['dims']==[.380,.317,1.112] for i in speakers) and all(abs(bb[i['name']][5]-1.112)<1e-5 for i in speakers),{'maker_hwd_with_plinth_terminal_mm':[1112,317,380],'source':v['audio']['source']})
check('Speaker centres symmetric at 3200 separation',len(speakers)==2 and abs(abs(speakers[1]['centre'][1]-speakers[0]['centre'][1])-3.2)<1e-5,'10-degree toe-in provisional; finish/driver details illustrative')
check('Speaker rear planning allowance recorded',all(min(p[0] for p in i['polygon'])>.3 for i in speakers),{'min_reserved_rear_clearances_mm':[min(p[0] for p in i['polygon'])*1000 for i in speakers],'status':'Planning allowance, not acoustic tuning result'})
check('TV feet fit console top',tv[0]>=console[0] and tv[3]<=console[3] and tv[1]>=console[1] and tv[4]<=console[4],'Freestanding TV; actual product stand unselected')
westparts=[console,tv]+[bb[i['name']] for i in speakers]
check('All west AV parts inside west wall endpoints',all(b[1]>=3.446667 and b[4]<=8.486667 for b in westparts),{'north_end_gap_mm':(8.486667-max(b[4] for b in westparts))*1000,'south_end_gap_mm':(min(b[1] for b in westparts)-3.446667)*1000})
arch=[o for c in bpy.data.collections if c.name.startswith(('02 |','03 |','06 |','07 |')) for o in c.objects if o.type=='MESH']
hits=[[n,o.name] for n,b in bb.items() for o in arch if intersect(b,bounds([o]))]
check('Actual living meshes clear walls/beams',not hits,hits)
collisions=[]
for j,i in enumerate(living):
    for other in living[j+1:]:
        if i['purpose']=='screen' or other['purpose']=='screen':continue
        if overlap(i['polygon'],other['polygon']):collisions.append([i['name'],other['name']])
check('No unintended proxy footprint overlap',not collisions,collisions)
a,b,c,d=v['play_rect'];play=[(a,b),(c,b),(c,d),(a,d)]
check('1600 by 1870 floor-play footprint clear',not any(overlap(play,i['polygon']) for i in living if i['purpose']!='screen'),{'area_m2':(c-a)*(d-b)})
sofa=next(i for i in living if i['name'].startswith('SOFA'));gap=min(bb[i['name']][0] for i in east)-max(p[0] for p in sofa['polygon'])
check('Rear sofa-to-east-cabinet clearance recomputed',abs(gap-.806667)<.001,{'closed_gap_mm':gap*1000,'remaining_with_450_leaf_mm':(gap-.45)*1000,'comfort':'Unresolved / sequential use'})
door_hits=[]
for i in east:
    front=min(p[0] for p in i['polygon']);y0=min(p[1] for p in i['polygon']);y1=max(p[1] for p in i['polygon'])
    for hy,start,end in ((y0,90,180),(y1,180,270)):
        sector=[(front,hy)]+[(front+.45*math.cos(math.radians(t)),hy+.45*math.sin(math.radians(t))) for t in range(start,end+1)]
        door_hits.extend([i['name'],o['name']] for o in living if o is not i and o['purpose']!='screen' and overlap(sector,o['polygon']))
check('East 450 mm door sectors clear other furniture',not door_hits,door_hits)
band=[(1.6,3.446667),(5.073333,3.446667),(5.073333,4.716667),(1.6,4.716667)]
check('South entry/dining circulation band free of furniture',not any(overlap(band,i['polygon']) for i in living if i['purpose']!='screen'),'1270 mm geometric band across lower living zone; full route/comfort and recline/guest use remain unresolved')
for room,hx,hy,radius,start,end in [('girls',8.255,5.5,.9517,0,88),('study',7.9,5.5,.9533,92,180),('living',1.44,2.685,.71,-92,0)]:
    sector=[(hx,hy)]+[(hx+radius*math.cos(math.radians(t)),hy+radius*math.sin(math.radians(t))) for t in range(start,end+1)]
    hit=[i['name'] for i in its if i['room']==room and i['purpose']!='screen' and overlap(sector,i['polygon'])]
    check(room+' room-door sweep clear',not hit,hit)
check('All content groups still required, capacity reopened',v['storage']['samla_contents_boxes']==21 and v['storage']['existing_full_cupboard_content_groups_retained']==3,'Requirement/allocation record only; three east cabinets do not establish retained-content fit')
check('Server remains removed',bpy.data.objects.get('RETAINED R6 NAS') is None,'Owner direction preserved')
report={'all_pass':all(c['pass'] for c in checks),'checks':checks,'overall_feasibility':'Conditional. Passed geometry does not approve actual storage capacity, acoustics or product/site/household operation.',
    'gates':{'architectural_geometry':'pass','specified_tv_and_ratio_geometry':'pass','actual_content_capacity':'unresolved','speaker_acoustic_result':'unresolved','real_furniture_operation_and_comfort':'unresolved','budget_and_products':'unresolved'},
    'unresolved':['Three 900 mm east units are a proposed count; actual shelf interiors and all retained contents/possible overflow not yet established',
        'North beam/site ceiling and actual cabinet product tolerances: only ~37 mm model plan separation',
        '807 mm behind sofa / 357 mm with 450 mm leaf: sequential cabinet use, comfort and actual hinge/drawer travel',
        'Actual recliner full recline and window access, guest chairs and complete routes',
        'Speaker room tuning/toe-in, grille/finish, cable routes and amplifier/source hardware',
        'Actual TV bezel/stand/console products and seated eye/posture',
        'Girls depth, exact 2200 usable wall/fitting and night door/drawer access unchanged and unresolved',
        'Fixed west services, product costs in SGD and tall-unit support/glazing details']}
(OUT/'fit_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'all_pass':report['all_pass'],'checks':len(checks),'failures':[c for c in checks if not c['pass']]},indent=2));assert report['all_pass']
