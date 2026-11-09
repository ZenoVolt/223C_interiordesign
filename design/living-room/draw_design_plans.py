"""Draw standalone measured plans and comparison boards from Blender manifest."""
import json, math, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Arc
from PIL import Image, ImageDraw, ImageFont

REV3='--revision03' in sys.argv
REV2='--revision02' in sys.argv or REV3
OUT=Path(__file__).resolve().parent/'iterations'/('03-wall-bounded-american-walnut' if REV3 else ('02-wardrobe-and-full-height-packout' if REV2 else '01-family-room-triplets'))
DATA=json.loads((OUT/'layouts.json').read_text(encoding='utf-8'))
if DATA.get('valid_for_current_brief') is False:
    raise SystemExit('Iteration 01 is superseded; revise the inventory/layout before generating new current design boards.')
INK='#243a35';GREEN='#597665';PAPER='#f7f5ef';LINE='#8a9890'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':INK,'axes.titleweight':'bold'})
IDS={'SOFA':'S','RETAINED RECLINER':'R','RETAINED FOOTSTOOL':'F','NEW toy':'T','RETAINED R6':'N','SMALL':'s',
 'LOW PULL':'B','PULL-OUT':'P','REUSE girls cupboard 1':'C1','REUSE girls cupboard 2':'C2','REUSE study':'C3','NEW study':'U',
 'PACKOUT stack 1':'P1','PACKOUT stack 2':'P2'}
IDS.update({'NEW archive':'A','FIXED SLIDING':'W'})

def id_for(name):
    return next((v for k,v in IDS.items() if name.startswith(k)),'?')

def dim(ax,a,b,label,vertical=False):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'|-|','color':LINE,'lw':.9})
    x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
    ax.text(x+(.075 if vertical else 0),y+(0 if vertical else .06),label,ha='left' if vertical else 'center',va='center' if vertical else 'bottom',rotation=90 if vertical else 0,fontsize=9,bbox={'facecolor':PAPER,'edgecolor':'none','pad':1.5})

def plan(ax,variant,room,title,night=True):
    d=DATA['variants'][variant];r=d['rooms'][room];x0,y0,x1,y1=r
    ax.set_facecolor(PAPER);ax.set_aspect('equal');ax.set_xlim(x0-.3,x1+.45);ax.set_ylim(y0-.3,y1+.4)
    ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor='#efeee7',edgecolor='none'))
    if room=='study':
        ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor='#e8e8e2',hatch='///',edgecolor='#d6d8d1',lw=0))
        ax.add_patch(Rectangle((7.573333 if REV2 else 7.323333,6.68),.45 if REV2 else .7,2.2,facecolor='#dbe8dd',edgecolor=GREEN,lw=1.5))
        ax.text(6.15,7.5,'Other study area\nnot redesigned',ha='center',va='center',fontsize=9,color='#78857d')
    for w in d['walls']:
        a,b,c,e=w['rect']
        if c<x0-.1 or a>x1+.1 or e<y0-.1 or b>y1+.1:continue
        # Door/window header pieces must not fill openings in a top-view plan.
        if 'above ' in w['name']:continue
        ax.add_patch(Rectangle((a,b),c-a,e-b,facecolor='#394a44',edgecolor='none',zorder=5))
    # Windows remain in their original locations, marked over sill walls.
    windows={'living':[(.525,2.845,8.486667),(3.595,4.795,8.486667)],'study':[(5.793,7.573,9.16)],'girls':[(8.333,10.118,9.16)]}
    for a,b,y in windows[room]:ax.plot([a,b],[y,y],color='#8aa8ad',lw=4,zorder=7)
    if room in ('girls','study'):
        hx,hy,rad,start,end=(8.255,5.5,.9517,0,88) if room=='girls' else (7.9,5.5,.9533,92,180)
        ax.add_patch(Arc((hx,hy),2*rad,2*rad,theta1=start,theta2=end,color='#9b8065',ls='--',lw=1,zorder=8))
        ang=math.radians(88 if room=='girls' else 92)
        ax.plot([hx,hx+rad*math.cos(ang)],[hy,hy+rad*math.sin(ang)],color='#9b8065',lw=2,zorder=8)
    if room=='living':
        a,b,c,e=d['play_rect'];ax.add_patch(Rectangle((a,b),c-a,e-b,facecolor='#dbe4d5',edgecolor=GREEN,ls='--',lw=1.4))
        ax.text((a+c)/2,(b+e)/2,f'FLOOR PLAY\n{round((c-a)*1000)} x {round((e-b)*1000)}',ha='center',va='center',fontsize=9,color=GREEN)
        ax.annotate('Entry / dining / bedroom route',xy=(4.7,4.55),xytext=(2.55,3.9),ha='center',fontsize=8,arrowprops={'arrowstyle':'->','color':'#8c9f9e','connectionstyle':'angle3'})
    for it in d['items']:
        if it['room']!=room:continue
        if it['purpose']=='screen':continue
        if it['purpose']=='trundle_open' and not night:continue
        is_pull=it['purpose']=='trundle_open'
        col='#926b4b' if REV3 and it['name'].startswith(('NEW','LOW PULL','SMALL')) else it['colour']
        ax.add_patch(Polygon(it['polygon'],closed=True,facecolor=col if not is_pull else '#dce7dc',edgecolor='#5b695f',lw=.85,ls='--' if is_pull else '-',zorder=3 if is_pull else 4,alpha=.85))
        x,y=it['centre'];lab=id_for(it['name'])
        ax.text(x,y,lab,ha='center',va='center',fontsize=9,fontweight='bold',zorder=9)
    dim(ax,(x0,y1+.21),(x1 if room!='girls' else 10.803333,y1+.21),f'{5070 if room=="living" else 2670} mm')
    if room=='living':dim(ax,(x1+.2,y0),(x1+.2,y1),'5040 mm',True)
    else:dim(ax,(x1+.2,y0),(x1+.2,y1),'3610 mm',True)
    if room=='study':dim(ax,(7.16,6.68),(7.16,8.88),'2200 ONLY',True)
    if room=='girls':
        if REV2:
            dim(ax,(8.58,7.6),(8.85,7.6),'270',False)
            ax.text(8.71,7.35,'NOT A\nROUTE',fontsize=6,ha='center',color='#8c5444')
            dim(ax,(9.25,6.15),(9.25,7.06),'910 foot access',True)
            ax.annotate('',xy=(9.32,6.7),xytext=(8.74,5.9),arrowprops={'arrowstyle':'->','color':GREEN,'connectionstyle':'angle3'})
            ax.plot([8.58,9.03,9.03,8.58],[6.68,6.68,8.48,8.48],ls=':',color='#a77661',lw=1)
        else:
            dim(ax,(8.1333,7.6),(8.85,7.6),'~717',False)
            ax.text(8.35,6.35,'Night route',fontsize=7,rotation=90,ha='center',color=GREEN)
    ax.set_title(title,loc='left',fontsize=13,pad=20);ax.axis('off')

LEGENDS={
 'living':['S  Sofa proxy: 2500 x 1000 mm','R/F  Existing recliner + footstool: assumed sizes','T  New toy cupboard: 2400 x 500 x 800 H','N  Retained NAS: 233 x 543 x 465 H','s  Movable side table: 380 mm diameter','TV option uses a 65-inch screen proxy.'],
 'girls':['B  Low pull-out bed proxy: 2050 x 950 mm','P  Lower mattress: 950 mm pull-out extension','C1/C2  Reuse two 900 x 400 x 2000 H cupboards','~717 mm west route with bed fully open','~1070 mm cupboard front to bed foot','South wall placement frees the west route.'],
 'study':['C3  Reuse one 900 x 400 x 2000 H cupboard','U  New loose utility unit: 1300 x 700 x 2200 H','P1/P2  Packout: each 600 x 600 x 1050 H proxy','900 + 1300 = 2200 mm authorised wall run','Upper U shelves reserve study box contents.','Packout dimensions / exact wall endpoints: verify.']}
if REV2:
    LEGENDS['living']=['S  Sofa proxy: 2500 x 1000; R/F retained recliner/stool','T  New toy cupboard: 2400 x 500 x 800 H','A  New study-content archive cupboard: 800 x 500 x 2100 H','N  NAS: 233 x 543 x 465 H; s movable side table','Both toy and archive contents allocated to living cupboards.','Furniture/product fit and actual shelf capacity remain provisional.']
    LEGENDS['girls']=['B/P  Low pull-out bed: 2050 long, 950 / 1900 wide','W  Existing sliding wardrobe: 600 deep; full wall reserved','C1/C2  Existing metal cupboards on the available west wall','910 mm at bed foot; 270 mm side gap is NOT a route','Metal cupboard doors need bed stored for full access.','Wardrobe width/switch gap, bed product and end gaps: verify.']
    LEGENDS['study']=['C3  Existing cupboard: 900 x 400 x 2000 H','P1/P2  Freestanding stacks: 600 x 450 x 2000 H allowance','Each stack: 2 four-drawer + 1 three-drawer + 2 cabinets','900 + 600 + 600 + 100 gaps = 2200 mm','No enclosing cupboard or archive shelves above stacks.','Study-box contents move to new living archive cupboard.']
if REV3:
    LEGENDS['living'][1]='T  American walnut toy cupboard: 2000 x 500 x 900 H'
    LEGENDS['living'][2]='A  American walnut archive: 800 x 500 x 2100 H'
    LEGENDS['living'][4]='800 + 50 gap + 2000 = 2850 mm, within backing wall.'

def single(variant,room,name,title):
    fig=plt.figure(figsize=(10,10),facecolor=PAPER)
    ax=fig.add_axes([.07,.24,.84,.65]);plan(ax,variant,room,title)
    fig.text(.075,.965,'223C  /  FAMILY ROOM STUDY',fontsize=10,color=GREEN)
    fig.text(.075,.935,'REVISION 03 / AMERICAN WALNUT' if REV3 else ('REVISION 02' if REV2 else 'FIRST FURNITURE PASS'),fontsize=19,fontweight='bold',color=INK)
    for i,line in enumerate(LEGENDS[room]):fig.text(.085,.205-i*.024,line,fontsize=9)
    fig.text(.085,.035,'Measured shell; furniture proxies. Dimensions in mm. Do not scale image for purchase.',fontsize=8,color='#768277')
    fig.savefig(OUT/(name+'.png'),dpi=180,facecolor=PAPER);plt.close(fig)

single('A-with-tv','living','plan-A-living','A  /  Shared TV and floor play')
single('B-without-tv','living','plan-B-living','B  /  Conversation and floor play')
single('A-with-tv','girls','plan-shared-girls','GIRLS  /  Pull-out bed + reused cupboards')
single('A-with-tv','study','plan-shared-study','STUDY  /  Hinge-side wall only')

for variant,label in [('A-with-tv','A  /  WITH TV'),('B-without-tv','B  /  WITHOUT TV')]:
    fig,axs=plt.subplots(1,3,figsize=(17,8),facecolor=PAPER,gridspec_kw={'width_ratios':[1.45,1,1]})
    for ax,room,title in zip(axs,['living','girls','study'],['LIVING','GIRLS / NIGHT MODE','STUDY / 2200 WALL']):plan(ax,variant,room,title)
    fig.suptitle('223C   '+label+'   /   COORDINATED ROOM TRIPLET',x=.045,ha='left',y=.98,fontsize=20,fontweight='bold',color=INK)
    fig.text(.045,.12,'Shared: fixed sliding wardrobe retained; 3 full metal cupboards; 21 box contents; 2 freestanding 2000 mm Packout stacks.' if REV2 else 'Shared in both options: 3 existing full cupboards retained; 21 SAMLA box contents accounted for; 2 Packout stack proxies.',fontsize=11)
    fig.text(.045,.08,'Girls: night access at bed foot. Metal cupboard doors require bed stored for full access. Study archive moves to living.' if REV2 else 'Living toy storage + study upper archive storage are new furniture proxies. Girls use the dining table; no bunk or new desk.',fontsize=10)
    fig.text(.045,.04,'Furniture / Packout dimensions and storage fit remain provisional. Existing architecture preserved. See REVIEW.md for assumptions.',fontsize=9,color='#768277')
    fig.subplots_adjust(left=.04,right=.98,bottom=.2,top=.88,wspace=.1)
    fig.savefig(OUT/(variant+'-triplet-plan.png'),dpi=160,facecolor=PAPER);plt.close(fig)

# Native visual boards: compositing generated views with labels, without changing their geometry.
FONT='C:/Windows/Fonts/segoeui.ttf';BOLD='C:/Windows/Fonts/segoeuib.ttf'
def font(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,size)
def fit_image(canvas,file,rect):
    im=Image.open(OUT/file).convert('RGB');x,y,w,h=rect;im.thumbnail((w,h),Image.Resampling.LANCZOS)
    canvas.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))

for variant,label,desc in [('A-with-tv','A / Shared screen','Sofa faces the TV; adults overlook the central play area.'),('B-without-tv','B / Family lounge','Sofa faces into the room; clear floor play and conversation.')]:
    c=Image.new('RGB',(1800,1660),PAPER);dr=ImageDraw.Draw(c)
    dr.text((60,35),'223C / REVISION 03 / AMERICAN WALNUT' if REV3 else ('223C / REVISION 02' if REV2 else '223C / FIRST FURNITURE PASS'),font=font(24),fill=GREEN)
    dr.text((60,77),label,font=font(48,True),fill=INK);dr.text((60,140),desc,font=font(25),fill=INK)
    fit_image(c,variant+('-living-storage.png' if REV2 else '-living.png'),(40,192,850,610))
    fit_image(c,variant+'-living-reverse.png',(910,192,850,610))
    dr.text((60,817),'LIVING / STORAGE WALL' if REV2 else 'LIVING / ENTRY VIEW',font=font(22,True),fill=INK);dr.text((930,817),'LIVING / REVERSE VIEW',font=font(22,True),fill=INK)
    fit_image(c,'shared-girls-night.png',(40,885,560,420));fit_image(c,'shared-girls-storage.png',(620,885,560,420));fit_image(c,'shared-study.png',(1200,885,560,420))
    for x,text in [(60,'GIRLS / BED OPEN'),(640,'GIRLS / WARDROBE + CUPBOARDS' if REV2 else 'GIRLS / REUSED CUPBOARDS'),(1220,'STUDY / 2200 mm WALL')]:dr.text((x,1320),text,font=font(19 if REV2 else 20,True),fill=INK)
    lines=['Shared storage / sleeping arrangement in both triplets:',
     'Two existing cupboards in girls\u2019 room; one existing cupboard + new utility storage in study.',
     'New living toy cupboard; 21 box contents retained with repacking allowed. Low pull-out bed.',
     'Dimensioned proxy design: exact recliner, bed, Packout, cupboard interiors and site gaps need verification.']
    if REV2:
        lines=['Corrected: existing sliding wardrobe retained; Packout stacks freestanding at 2000 mm high.',
         'Study: 900 mm cupboard + two 600 mm stack allowances + 100 mm gaps = 2200 mm.',
         'Girls: bed-foot access at night; west metal cupboards need bed stored for full door access.',
         'Toy + study-box contents assigned to new living cupboards; product fit / actual shelf capacity unresolved.']
    if REV3:
        lines[0]='American walnut for new furniture; storage run ends inside the backing wall.'
        lines[1]='Living: 800 mm archive + 50 mm gap + 2000 mm toy cupboard = 2850 mm run.'
    for i,line in enumerate(lines):dr.text((60,1400+44*i),line,font=font(24 if i<3 else 21,i==0),fill=INK if i<3 else '#758176')
    c.save(OUT/(variant+'-board.jpg'),quality=94)
print('PLANS_AND_BOARDS_COMPLETE')
