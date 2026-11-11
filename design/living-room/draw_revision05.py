"""Measured V5 plans and solid/reeded comparison boards."""
import json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,Arc
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent/'iterations'/'05-full-west-storage-l-return'
REFERENCE=(OUT/'layouts-reference.json').exists()
v=next(iter(json.loads((OUT/('layouts-reference.json' if REFERENCE else 'layouts.json')).read_text(encoding='utf-8'))['variants'].values()))
PAPER='#f7f5ef';INK='#243a35';GREEN='#597665';WOOD='#926b4b'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'text.color':INK})
def dim(ax,a,b,label,vertical=False):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'|-|','color':GREEN,'lw':.8},zorder=20)
    ax.text((a[0]+b[0])/2+(.06 if vertical else 0),(a[1]+b[1])/2+(0 if vertical else .05),label,ha='left' if vertical else 'center',va='center' if vertical else 'bottom',rotation=90 if vertical else 0,fontsize=8,zorder=21,bbox={'facecolor':PAPER,'edgecolor':'none','pad':1})
def draw(ax,kind):
    room='girls' if kind=='girls' else 'living'
    limits={'living':(-.5,5.65,2.3,8.95),'corner':(-.3,2.7,1.65,5.3),'girls':(7.72,11.53,5.23,9.57)}[kind]
    ax.set_xlim(limits[:2]);ax.set_ylim(limits[2:]);ax.set_aspect('equal');ax.set_facecolor(PAPER)
    for w in v['walls']:
        if 'above ' in w['name']:continue
        a,b,c,d=w['rect'];ax.add_patch(Rectangle((a,b),c-a,d-b,color='#394a44',lw=0,zorder=5))
    for it in v['items']:
        if it['room']!=room:continue
        name=it['name'];p=it['purpose'];color=WOOD if p in ('storage','filler') else it['colour']
        if p=='trundle_open':color='#dce7dc'
        if p=='equipment_in_bay':color='#434849'
        ax.add_patch(Polygon(it['polygon'],closed=True,facecolor=color,edgecolor='#5b695f',lw=.8,zorder=7 if p=='equipment_in_bay' else 3,ls='--' if p=='trundle_open' else '-',hatch='///' if p=='corner_void' else None,alpha=.9))
        x,y=it['centre'];label=''
        if name.startswith('WEST STORAGE'):label=name.split()[-1];x+=.06
        elif name.startswith('RETURN'):label='L1\n'+str(round(it['dims'][0]*1000))
        elif name.startswith('L CORNER'):label='L\n630'
        elif name.startswith('NEW girls'):label='G'+name[-1]+'\n'+str(round(it['dims'][0]*1000))
        elif name.startswith('LOW PULL'):label='BED'
        elif p=='trundle_open':label='PULL-OUT'
        elif p=='fixed':label='EXISTING\nWARDROBE'
        elif name.startswith('SOFA'):label='SOFA'
        elif 'RECLINER' in name:label='CHAIR'
        elif 'FOOTSTOOL' in name:label='STOOL'
        if name=='WEST STORAGE W1':
            label='W1' if REFERENCE else 'W1\nNAS'
            if kind=='corner':y+=.23
        if label:ax.text(x,y,label,ha='center',va='center',fontsize=7 if kind!='corner' else 8,fontweight='bold',zorder=12)
    if kind=='living':
        for x0,x1 in ((.525,2.845),(3.595,4.795)):ax.plot([x0,x1],[8.486667]*2,color='#8aa8ad',lw=4,zorder=8)
        a,b,c,d=v['play_rect'];ax.add_patch(Rectangle((a,b),c-a,d-b,facecolor='#dbe4d5',edgecolor=GREEN,ls='--',zorder=1))
        ax.text((a+c)/2,(b+d)/2,f'FLOOR PLAY\n{round((c-a)*1000)} x {round((d-b)*1000)}',ha='center',va='center',color=GREEN,fontsize=9)
        ax.add_patch(Rectangle((0,8.326667),5.073333,.16,facecolor='#a9b8b8',hatch='///',alpha=.7,zorder=6))
        dim(ax,(0,8.76),(5.073333,8.76),'5070 mm');dim(ax,(5.35,3.446667),(5.35,8.486667),'5040 mm',True)
        main=[i for i in v['items'] if i['name'].startswith('WEST STORAGE')]
        lo=min(p[1] for i in main for p in i['polygon']);hi=max(p[1] for i in main for p in i['polygon']);front=max(p[0] for i in main for p in i['polygon'])
        dim(ax,(front+.35,lo),(front+.35,hi),f'{round((hi-lo)*1000)} / {len(main)} modules',True)
        setback=v['checks']['living_north_setback_mm']
        ax.annotate(f'{setback} mm north setback\nbeam kept clear',xy=(front,hi),xytext=(1.65,8.02),fontsize=7,arrowprops={'arrowstyle':'->','color':GREEN},zorder=21)
        ax.annotate('Entry / dining / bedrooms',xy=(4.9,4.5),xytext=(2.3,3.55),fontsize=8,arrowprops={'arrowstyle':'->','color':GREEN})
        ax.text(-.30,6.2,f'WEST / {round(main[0]["dims"][2]*1000)} H STORAGE',rotation=90,ha='center',va='center',fontsize=8)
        title='LIVING / NO TV'
    elif kind=='corner':
        hx,hy=1.44,2.685;ax.add_patch(Arc((hx,hy),1.42,1.42,theta1=-90,theta2=-2,color='#9b8065',ls='--',zorder=8))
        ax.plot([hx,hx+.71*math.cos(math.radians(-2))],[hy,hy+.71*math.sin(math.radians(-2))],color='#9b8065',lw=2,zorder=8)
        dim(ax,(.583333,4.98),(1.483333,4.98),'900 return');dim(ax,(1.72,3.486667),(1.72,3.986667),'500 D',True)
        ax.annotate('Blind corner\nNO storage credit',xy=(.28,3.8),xytext=(1.1,4.55),fontsize=8,arrowprops={'arrowstyle':'->','color':GREEN},zorder=21)
        ax.annotate('50 mm before wall end',xy=(1.50,3.47),xytext=(.45,3.06),fontsize=7,arrowprops={'arrowstyle':'->','color':GREEN},zorder=21)
        ax.text(.7,2.1,'MAID ROOM',ha='center',fontsize=8,color=GREEN);ax.text(2.1,2.35,'ENTRY',ha='center',fontsize=8,color=GREEN)
        if not REFERENCE:ax.text(.73,4.3,'Open NAS bay',fontsize=7,zorder=21)
        title='L-RETURN / CORNER DETAIL'
    else:
        ax.plot([8.333,10.118],[9.16]*2,color='#8aa8ad',lw=4,zorder=8)
        hx,hy=8.255,5.5;ax.add_patch(Arc((hx,hy),1.9034,1.9034,theta1=0,theta2=88,color='#9b8065',ls='--',zorder=8))
        ax.plot([hx,hx+.9517*math.cos(math.radians(88))],[hy,hy+.9517*math.sin(math.radians(88))],color='#9b8065',lw=2,zorder=8)
        dim(ax,(8.133333,9.41),(10.803333,9.41),'2670 mm upper width');dim(ax,(11.31,5.55),(11.31,9.16),'3610 mm',True)
        dim(ax,(7.95,6.68),(7.95,8.88),'2200 / zero spare',True);dim(ax,(9.3,6.15),(9.3,7.06),'910 foot band',True)
        dim(ax,(8.58,7.6),(8.85,7.6),'270');ax.text(8.71,7.37,'NOT A\nROUTE',ha='center',fontsize=6,color='#8c5444');title='GIRLS / NIGHT MODE'
    ax.set_title(title,loc='left',fontsize=13,fontweight='bold',pad=18);ax.axis('off')
def plans():
    fig,axs=plt.subplots(1,3,figsize=(18,10),facecolor=PAPER,gridspec_kw={'width_ratios':[1.4,1,1.05]})
    for ax,kind in zip(axs,['living','corner','girls']):draw(ax,kind)
    fig.suptitle('223C / VERSION 5 / 2400 mm WALNUT + REEDED GLASS',x=.04,y=.96,ha='left',fontsize=22,fontweight='bold')
    for y,line in [( .14,'L: six 700 mm modules + 900 mm return; blind corner excluded. No TV or living server.' if REFERENCE else 'L: six 700 mm modules + 900 mm return; blind corner excluded. No TV; open NAS bay in W1.'),(.105,'2400 H units stop 200 mm short of north wall; beam underside 2255 mm in source model. Verify actual ceiling/beam.'),(.07,'Girls: two 800 glass/niche/base units + 600 open-shelf/drawers. All 2400 H; 400 D provisional; zero fitting tolerance.' if REFERENCE else 'Girls: 800 + 800 + 600 W x 2400 H; 400 D provisional. Full door use needs trundle stored. Actual capacity unresolved.'),(.035,'Furniture proxies; dimensions in mm. Actual contents and girls night door/drawer access unresolved; study/wardrobe retained.')]:fig.text(.04,y,line,fontsize=10,color=INK)
    fig.subplots_adjust(left=.04,right=.97,top=.87,bottom=.19,wspace=.18);fig.savefig(OUT/('V5-reference-coordinated-plan.png' if REFERENCE else 'V5-coordinated-plan.png'),dpi=160,facecolor=PAPER);plt.close(fig)
    for kind in ('living','corner','girls'):
        fig,ax=plt.subplots(figsize=(10,10),facecolor=PAPER);draw(ax,kind)
        fig.text(.07,.965,'223C / VERSION 5 / 2400 H STORAGE',fontsize=17,fontweight='bold')
        fig.text(.07,.025,'Dimensioned proxies; see REVIEW.md for beam, fitting, storage and access limits.',fontsize=9,color=GREEN)
        fig.subplots_adjust(top=.89,bottom=.06,left=.06,right=.91);fig.savefig(OUT/(('reference-plan-' if REFERENCE else 'plan-')+kind+'.png'),dpi=160,facecolor=PAPER);plt.close(fig)
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',size)
def place(canvas,name,x,y,w,h):
    im=Image.open(OUT/name).convert('RGB');im.thumbnail((w,h),Image.Resampling.LANCZOS);canvas.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))
def board(reeded=False,reference=False):
    c=Image.new('RGB',(2000,1830),PAPER);d=ImageDraw.Draw(c)
    d.text((55,30),'223C / VERSION 5 / AMERICAN WALNUT',fill=GREEN,font=font(25))
    d.text((55,75),'Owner references / walnut + reeded glass' if reference else ('Reeded glass / full west storage' if reeded else 'Solid walnut / full west storage'),fill=INK,font=font(48,True))
    d.text((55,143),'2400 mm cabinets. No TV or living server. Storage wraps onto the L-return.' if reference else '2400 mm tall cabinets. No TV. Storage wraps onto the short L-return.',fill=INK,font=font(27))
    files=['V5-reference-west-storage.png','V5-reference-l-return.png','V5-reference-living-entry.png','girls-reference-storage.png'] if reference else (['V5-reeded-west-storage.png','V5-reeded-l-return.png','V5-reeded-living-entry.png','girls-reeded-storage.png'] if reeded else ['V5-west-storage.png','V5-l-return-living.png','V5-living-entry.png','girls-storage.png'])
    for name,(x,y,w,h) in zip(files,[(40,205,1060,750),(1120,205,840,750),(40,1000,940,640),(1020,1000,940,640)]):place(c,name,x,y,w,h)
    for x,y,label in [(55,955,'WEST / SIX 700 mm MODULES'),(1135,955,'L-RETURN / BLIND CORNER'),(55,1635,'LIVING / FAMILY SEATING'),(1035,1635,'GIRLS / 800 + 800 + 600 mm')]:d.text((x,y),label,fill=INK,font=font(23,True))
    d.text((55,1690),'North: 200 mm setback clears low beam. Return: 900 mm wide; blind corner excluded.',fill=INK,font=font(25))
    d.text((55,1735),'Girls: full doors need trundle stored. Actual site, product and content fit remain unresolved.',fill=GREEN,font=font(23))
    if reeded or reference:d.text((55,1775),'Illustrative glass / contents: translucency and hardware need a real product sample.',fill=GREEN,font=font(22))
    c.save(OUT/('V5-reference-board.jpg' if reference else ('V5-reeded-board.jpg' if reeded else 'V5-solid-board.jpg')),quality=94)
if __name__=='__main__':
    plans()
    board()
    if (OUT/'girls-reeded-storage.png').exists():board(True)
    if (OUT/'girls-reference-storage.png').exists():board(reference=True)
    print('V5_PLANS_AND_BOARDS_COMPLETE')
