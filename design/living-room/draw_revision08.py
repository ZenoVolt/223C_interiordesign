"""V8 measured top view, centred AV elevation, viewing section and render board."""
import json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,Arc
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent/'iterations'/'08-west-av-east-storage'
v=next(iter(json.loads((OUT/'layouts.json').read_text(encoding='utf-8'))['variants'].values()))
PAPER='#f7f5ef';INK='#243a35';GREEN='#597665';WOOD='#926b4b';LINE='#8a9890'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'text.color':INK})
def dim(ax,a,b,label,vertical=False):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'|-|','color':LINE,'lw':.8},zorder=20)
    ax.text((a[0]+b[0])/2+(.055 if vertical else 0),(a[1]+b[1])/2+(0 if vertical else .04),label,ha='left' if vertical else 'center',va='center' if vertical else 'bottom',rotation=90 if vertical else 0,fontsize=8,zorder=21,bbox={'facecolor':PAPER,'edgecolor':'none','pad':1})
fig=plt.figure(figsize=(17,11),facecolor=PAPER)
ax=fig.add_axes([.045,.18,.48,.70]);ax.set_aspect('equal');ax.set_xlim(-.45,5.65);ax.set_ylim(2.95,8.97);ax.set_facecolor(PAPER)
for w in v['walls']:
    if 'above ' in w['name']:continue
    a,b,c,d=w['rect'];ax.add_patch(Rectangle((a,b),c-a,d-b,color='#394a44',lw=0,zorder=5))
for a,b in ((.525,2.845),(3.595,4.795)):ax.plot([a,b],[8.486667]*2,color='#8aa8ad',lw=4,zorder=8)
ax.add_patch(Rectangle((0,8.326667),5.073333,.16,facecolor='#a9b8b8',hatch='///',alpha=.6,zorder=6))
a,b,c,d=v['play_rect'];ax.add_patch(Rectangle((a,b),c-a,d-b,facecolor='#dbe4d5',edgecolor=GREEN,ls='--',zorder=1));ax.text((a+c)/2,(b+d)/2,'FLOOR PLAY\n1600 x 1870',ha='center',va='center',color=GREEN,fontsize=9)
for it in v['items']:
    if it['room']!='living':continue
    if it['purpose']=='screen':
        ax.plot([v['viewing']['screen_front_x_m']]*2,[it['centre'][1]-it['dims'][1]/2,it['centre'][1]+it['dims'][1]/2],color=INK,lw=4,zorder=12)
        continue
    p=it['purpose'];name=it['name'];color=WOOD if p=='storage' else it['colour']
    ax.add_patch(Polygon(it['polygon'],closed=True,facecolor=color,edgecolor='#5b695f',lw=.8,alpha=.9,zorder=3))
    x,y=it['centre'];label=''
    if name.startswith('EAST STORAGE'):label=name[-2:]+'\n900'
    elif name.startswith('WEST TV CONSOLE'):label='CONSOLE';x+=.10
    elif p=='speaker':label='Q11';x+=.02
    elif name.startswith('SOFA'):label='SOFA'
    elif 'RECLINER' in name:label='R'
    elif 'FOOTSTOOL' in name:label='F'
    elif name.startswith('SMALL'):label='s'
    ax.text(x,y,label,ha='center',va='center',fontsize=7,fontweight='bold',rotation=90 if 'CONSOLE' in label else 0,zorder=12)
cy=v['audio']['west_wall_midpoint_y_m'];eye=v['viewing']['seated_eye_m'];sx=v['viewing']['screen_front_x_m']
ax.plot([sx,eye[0]],[cy,cy],ls=':',color=GREEN,lw=1,zorder=20);ax.plot(eye[0],eye[1],'o',color=INK,ms=3,zorder=21)
for it in v['items']:
    if not it['name'].startswith('EAST STORAGE'):continue
    front=4.69;y0=min(p[1] for p in it['polygon']);y1=max(p[1] for p in it['polygon'])
    for hy,start,end in ((y0,90,180),(y1,180,270)):
        ax.add_patch(Arc((front,hy),.9,.9,theta1=start,theta2=end,color='#a77661',ls=':',lw=.7,zorder=2))
dim(ax,(0,8.76),(5.073333,8.76),'5070 mm')
dim(ax,(-.23,3.446667),(-.23,8.486667),'5040 mm west wall',True)
dim(ax,(5.33,5.59),(5.33,8.29),'2700 / three 900',True)
dim(ax,(3.883333,6.55),(4.69,6.55),'807 rear gap')
ax.annotate('Centred west AV axis',xy=(.6,cy),xytext=(1.1,3.77),fontsize=8,arrowprops={'arrowstyle':'->','color':GREEN},zorder=22)
ax.annotate('Entry / dining / bedrooms',xy=(4.9,4.25),xytext=(2.3,3.35),fontsize=8,arrowprops={'arrowstyle':'->','color':GREEN})
ax.set_title('LIVING / WEST AV + EAST STORAGE',loc='left',fontsize=14,fontweight='bold',pad=18);ax.axis('off')

view=v['viewing'];W=view['physical_tv_outer_width_mm']/1000;H=view['screen_height_mm']/1000;CW=view['console_width_mm']/1000
ax=fig.add_axes([.57,.52,.38,.34]);ax.set_aspect('equal');ax.set_xlim(-2.75,2.75);ax.set_ylim(-.35,2.1)
ax.add_patch(Rectangle((-CW/2,0),CW,.55,facecolor=WOOD,edgecolor=INK))
for x in (-CW/6,CW/6):ax.plot([x,x],[.08,.5],color=INK,lw=.6)
ax.add_patch(Rectangle((-W/2,.629),W,H+.022,facecolor='#344341',edgecolor=INK))
for x in (-1.6,1.6):
    ax.add_patch(Rectangle((x-.1585,0),.317,.051,facecolor='#434844',edgecolor=INK))
    ax.add_patch(Rectangle((x-.105,.051),.210,1.061,facecolor=WOOD,edgecolor=INK))
    for z,r in ((.91,.052),(.695,.0825),(.475,.0825),(.255,.0825)):ax.add_patch(plt.Circle((x,z),r,facecolor='#434844',edgecolor=INK,lw=.5))
dim(ax,(-W/2,1.80),(W/2,1.80),f'77-inch TV / {round(W*1000)} outer width')
dim(ax,(-CW/2,-.22),(CW/2,-.22),f'{round(CW*1000)} console / TV is 2/3 its width')
ax.plot([-2.52,2.52],[0,0],color=GREEN,lw=.8);ax.plot([0,0],[0,1.7],color=GREEN,ls=':',lw=.6)
ax.text(-1.6,1.24,'Q11 Meta',ha='center',fontsize=8);ax.text(1.6,1.24,'Q11 Meta',ha='center',fontsize=8)
ax.text(0,.25,'550 H / 450 D carcass provisional',ha='center',fontsize=8,color=PAPER)
ax.set_title('WEST ELEVATION / CENTRED ON 5040 WALL',loc='left',fontsize=13,fontweight='bold');ax.axis('off')

ax=fig.add_axes([.57,.19,.38,.28]);ax.set_aspect('equal');ax.set_xlim(-.1,5.35);ax.set_ylim(-.35,2.7)
ax.add_patch(Rectangle((.04,0),.45,.55,facecolor=WOOD,edgecolor=INK));ax.plot([sx,sx],[.64,.64+H],color=INK,lw=3)
ax.add_patch(Rectangle((2.883333,.12),1,.74,facecolor='#c9bca5',edgecolor=INK))
ax.add_patch(Rectangle((4.69,0),.35,2.35,facecolor=WOOD,edgecolor=INK));ax.plot([0,5.2],[0,0],color=GREEN,lw=.8)
ax.plot(eye[0],eye[2],'o',color=INK,ms=4);dim(ax,(sx,1.12),(eye[0],1.12),'3180 mm screen face to seated eye')
dim(ax,(3.883333,-.17),(4.69,-.17),'807')
ax.text(4.86,1.35,'2350 H / EAST STORAGE',rotation=90,ha='center',va='center',fontsize=7,color=PAPER)
ax.text(3.28,1.43,'Assumed eye 1120 H',ha='center',fontsize=8)
ax.set_title('VIEWING / SECTION THROUGH SOFA',loc='left',fontsize=13,fontweight='bold');ax.axis('off')
fig.text(.045,.95,'223C / VERSION 8 / CENTRED WEST TV + KEF / EAST STORAGE',fontsize=21,fontweight='bold',color=INK)
for y,line in [(.12,'West: 77-inch visible display, approx 2590 console, KEF Q11 Meta pair at 3200 mm centres. Toe-in / room tuning provisional.'),(.085,'East: three 900 x 350 x 2350 H cupboards. Rear sofa gap 807 mm, about 357 mm remaining with 450 mm leaf open.'),(.05,'Tall storage frontage falls from 4800 to 2700 mm and corner is removed; actual retained-content capacity is unresolved.')]:fig.text(.045,y,line,fontsize=10,color=INK)
fig.savefig(OUT/'V8-layout-and-viewing.png',dpi=160,facecolor=PAPER);plt.close(fig)

def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',size)
def place(canvas,name,x,y,w,h):
    im=Image.open(OUT/name).convert('RGB');im.thumbnail((w,h),Image.Resampling.LANCZOS);canvas.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))
c=Image.new('RGB',(2000,1830),PAPER);d=ImageDraw.Draw(c)
d.text((55,30),'223C / VERSION 8 / AMERICAN WALNUT + REEDED GLASS',font=font(25),fill=GREEN)
d.text((55,75),'West TV + KEF / east storage',font=font(48,True),fill=INK)
d.text((55,143),'77-inch TV. Approx 2.59 m console. Three 900 mm cupboards. 3.18 m viewing retained.',font=font(26),fill=INK)
for name,(x,y,w,h) in zip(['V8-west-av.png','V8-seated-view.png','V8-east-storage.png','V8-entry.png'],[(40,205,940,700),(1020,205,940,700),(40,1000,940,640),(1020,1000,940,640)]):place(c,name,x,y,w,h)
for x,y,label in [(55,920,'WEST / CENTRED TV + Q11 META PAIR'),(1035,920,'SOFA / ASSUMED 3180 mm EYE DISTANCE'),(55,1635,'EAST / THREE 900 mm CABINETS'),(1035,1635,'ENTRY / SEATING AND FLOOR PLAY')]:d.text((x,y),label,font=font(23,True),fill=INK)
d.text((55,1690),'Physical TV width = 2/3 console width. KEF speaker envelopes include plinths and terminals.',font=font(25),fill=INK)
d.text((55,1735),'807 mm behind sofa; storage capacity and sequential door use still need actual product/content checks.',font=font(23),fill=GREEN)
d.text((55,1775),'Girls / study retained. Server removed. Speaker styling, finish and acoustic positions are provisional.',font=font(22),fill=GREEN)
c.save(OUT/'V8-board.jpg',quality=94)
print('V8_PLAN_AND_BOARD_COMPLETE')
