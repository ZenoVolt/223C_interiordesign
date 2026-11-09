"""Verify meaningful fit invariants in generated furniture manifest (not product approval)."""
import json, hashlib, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REV2='--revision02' in sys.argv
OUT=Path(__file__).resolve().parent/'iterations'/('02-wardrobe-and-full-height-packout' if REV2 else '01-family-room-triplets')
d=json.loads((OUT/'layouts.json').read_text(encoding='utf-8'))
if d.get('valid_for_current_brief') is False:
    raise SystemExit('Iteration 01 is superseded by owner corrections; do not issue current fit claims from its proxy inventory.')
checks=[]
def check(name,ok,detail):checks.append({'name':name,'pass':bool(ok),'detail':detail})
def rect(p):return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
def overlap(a,b):
    # Separating-axis test for actual rotated rectangular footprints; touching edges allowed.
    for p in (a,b):
        for i in range(len(p)):
            u,v=p[i],p[(i+1)%len(p)];axis=(-(v[1]-u[1]),v[0]-u[0])
            pa=[x*axis[0]+y*axis[1] for x,y in a];pb=[x*axis[0]+y*axis[1] for x,y in b]
            if max(pa)<=min(pb)+1e-5 or max(pb)<=min(pa)+1e-5:return False
    return True
check('Architectural baseline byte-for-byte unchanged',hashlib.sha256((ROOT/'model'/'223C_Existing_Shell_v02.blend').read_bytes()).hexdigest()==d['baseline_sha256'],d['baseline_sha256'])
for name,v in d['variants'].items():
    its=v['items'];room=lambda r:[i for i in its if i['room']==r]
    study=room('study');storage=[i for i in study if i['purpose']=='storage' or (REV2 and i['purpose']=='equipment')]
    span_min=min(rect(i['polygon'])[1] for i in storage);span_max=max(rect(i['polygon'])[3] for i in storage)
    check(name+' study storage within authorised 2200 mm',abs(span_min-6.68)<1e-5 and abs(span_max-8.88)<1e-5 and abs(span_max-span_min-2.2)<1e-5,{'start_y':span_min,'end_y':span_max,'length_mm':(span_max-span_min)*1000})
    check(name+' three existing cupboards retained',sum(i['name'].startswith('REUSE') for i in its)==3,'Two girls, one study')
    equipment=[i for i in study if i['purpose']=='equipment']
    check(name+' two Packout stack envelopes retained',len(equipment)==2 and (not REV2 or all(i['dims'][2]==2 for i in equipment)),'Two freestanding 2000 mm stacks' if REV2 else 'Actual stacks remain unmeasured')
    check(name+' 21 box contents included',v['storage']['samla_contents_boxes']==21,'10 toy-box + 11 study-box contents; repacking allowed')
    # Broad closed cabinet envelope contains its lower equipment placeholders in plan.
    if not REV2:
        utility=next(i for i in study if i['name'].startswith('NEW study'));ur=rect(utility['polygon'])
        for it in study:
            if it['purpose']=='equipment':
                pr=rect(it['polygon']);check(name+' '+it['name']+' inside utility footprint',all([pr[0]>=ur[0]-.001,pr[1]>=ur[1]-.001,pr[2]<=ur[2]+.001,pr[3]<=ur[3]+.001]),'Proxy envelope only, shelf/hinge/actual-case fit not proved')
    else:
        ward=next(i for i in room('girls') if i['purpose']=='fixed')
        check(name+' fixed sliding wardrobe reserved',abs(ward['dims'][1]-.6)<1e-6 and ward['dims'][0]>1.8,'Full south-wall envelope reserved; 600 mm depth owner-confirmed')
        foot=[(8.85,6.15),(10.75,6.15),(10.75,7.06),(8.85,7.06)]
        check(name+' 910 mm bed-foot band free in night mode',not any(overlap(foot,i['polygon']) for i in room('girls')),'This is the access band; 270 mm beside lower mattress is not a walking route')
        for it in equipment:
            a,b,c,e=rect(it['polygon']);use=[(a-.45,b),(a,b),(a,e),(a-.45,e)]
            check(name+' '+it['name']+' drawer allowance clear',not any(overlap(use,j['polygon']) for j in study if j is not it),'450 mm forward planning allowance; actual full drawer stroke to verify')
    a,b,c,e=v['play_rect'];play=[(a,b),(c,b),(c,e),(a,e)]
    living=[i for i in room('living') if i['purpose']!='screen']
    check(name+' marked play area clear of furniture',not any(overlap(play,i['polygon']) for i in living),{'play_area_m2':round((c-a)*(e-b),3)})
    collisions=[]
    for r in ('living','girls','study'):
        items=[i for i in room(r) if i['purpose']!='screen' and (REV2 or i['purpose']!='equipment')]
        for j,it in enumerate(items):
            for other in items[j+1:]:
                if overlap(it['polygon'],other['polygon']):collisions.append([it['name'],other['name']])
    check(name+' no unintended furniture footprint overlap',not collisions,collisions)
    # Open door sectors must remain free. Sampled polygons are conservative at 1-degree steps.
    for r,hx,hy,radius,start,end in [('girls',8.255,5.5,.9517,0,88),('study',7.9,5.5,.9533,92,180)]:
        sector=[(hx,hy)]+[(hx+radius*math.cos(math.radians(t)),hy+radius*math.sin(math.radians(t))) for t in range(start,end+1)]
        hit=[i['name'] for i in room(r) if (REV2 or i['purpose']!='equipment') and overlap(sector,i['polygon'])]
        check(name+' '+r+' full modelled door swing clear',not hit,hit)
    for r in ('living','girls','study'):
        hits=[]
        for it in room(r):
            if it['purpose']=='screen' or (not REV2 and it['purpose']=='equipment'):continue
            for w in v['walls']:
                if 'above ' in w['name']:continue
                a,b,c,e=w['rect'];poly=[(a,b),(c,b),(c,e),(a,e)]
                if overlap(it['polygon'],poly):hits.append([it['name'],w['name']])
        check(name+' '+r+' furniture clears wall footprints',not hits,hits)
report={'scope':'Proxy footprint, modelled door sweep and baseline checks; not a site/product/structural or complete storage-capacity approval.',
 'all_pass':all(c['pass'] for c in checks),'checks':checks,
 'unresolved':['Exact study permitted segment endpoints','Actual Packout stack dimensions','Selected pull-out bed and retained recliner envelopes','Girls south-wall jamb/skirting and cupboard width tolerances','Shelf loads, usable cupboard interiors and actual content fit','Installed finish and lighting appearance']}
if REV2:
    report['overall_feasibility']='Conditional: metal cupboard doors require bed stored for full access; foot-access night arrangement awaits owner acceptance. Storage capacity/product/site checks remain unresolved.'
    report['full_cupboard_access_all_bed_states']=False
    report['unresolved']=['Exact study and girls west-wall segment endpoints','Bed/recliner product dimensions','Acceptance of metal-cupboard access restricted with bed open','Actual usable cupboard capacity and content fit','Final Packout drawer stroke / installed accessories','Built-in wardrobe width, switch gap, height and finish','Installed lighting / finish appearance']
(OUT/'fit_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'all_pass':report['all_pass'],'checks':len(checks),'failures':[c for c in checks if not c['pass']]},indent=2))
raise SystemExit(0 if report['all_pass'] else 1)
