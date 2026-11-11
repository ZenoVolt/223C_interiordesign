"""V7 measured living plan, TV elevation/section and inspected-render board."""
import importlib.util,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;OUT=HERE/'iterations'/'07-product-modules-360-setback'
spec=importlib.util.spec_from_file_location('plans',HERE/'draw_revision05.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
g.OUT=OUT;g.v=next(iter(json.loads((OUT/'layouts.json').read_text(encoding='utf-8'))['variants'].values()));g.REFERENCE=True
v=g.v;view=v['viewing'];W=view['screen_width_mm']/1000;H=view['screen_height_mm']/1000
fig=plt.figure(figsize=(17,11),facecolor=g.PAPER)
ax=fig.add_axes([.045,.18,.48,.70]);g.draw(ax,'living');ax.set_title('LIVING / 77-INCH EAST TV / 360 SETBACK',loc='left',fontsize=14,fontweight='bold',pad=18)
ax.plot([1.79,4.97],[6.95,6.95],color=g.GREEN,lw=1,ls=':',zorder=20);ax.plot(1.79,6.95,'o',color=g.INK,ms=3,zorder=21)
ax.text(4.82,6.95,'77 TV',rotation=90,color='white',ha='center',fontsize=7,zorder=21)
g.dim(ax,(.383333,7.8),(1.19,7.8),'807 rear gap')
ax=fig.add_axes([.57,.53,.38,.33]);ax.set_aspect('equal');ax.set_xlim(-1.5,1.5);ax.set_ylim(-.35,1.97)
ax.add_patch(Rectangle((-1,0),2,.55,facecolor=g.WOOD,edgecolor=g.INK))
for x in (-1/3,1/3):ax.plot([x,x],[.08,.5],color=g.INK,lw=.6)
ax.add_patch(Rectangle((-W/2,.64),W,H,facecolor='#344341',edgecolor=g.INK));ax.plot([-1.35,1.35],[0,0],color=g.GREEN,lw=.8)
g.dim(ax,(-W/2,1.77),(W/2,1.77),f'77-inch / {round(W*1000)} visible width')
g.dim(ax,(-1,-.23),(1,-.23),'2000 console (provisional)')
g.dim(ax,(1.12,.64),(1.12,.64+H),f'{round(H*1000)}',True)
ax.text(0,.27,'550 H / 450 D carcass',ha='center',fontsize=9,color=g.PAPER)
ax.set_title('EAST WALL / TV ELEVATION',loc='left',fontsize=13,fontweight='bold');ax.axis('off')
ax=fig.add_axes([.57,.19,.38,.28]);ax.set_aspect('equal');ax.set_xlim(-.1,5.35);ax.set_ylim(-.35,2.7)
ax.add_patch(Rectangle((.033333,0),.35,2.35,facecolor=g.WOOD,edgecolor=g.INK));ax.add_patch(Rectangle((1.19,.12),1,.74,facecolor='#c9bca5',edgecolor=g.INK))
ax.add_patch(Rectangle((4.583333,0),.45,.55,facecolor=g.WOOD,edgecolor=g.INK));ax.plot([4.97,4.97],[.64,.64+H],color=g.INK,lw=3)
ax.plot([0,5.2],[0,0],color=g.GREEN,lw=.8);ax.plot(1.79,1.12,'o',color=g.INK,ms=4)
g.dim(ax,(1.79,1.12),(4.97,1.12),'3180 mm seated eye to screen')
g.dim(ax,(.383333,-.17),(1.19,-.17),'807')
ax.text(.21,1.4,'2350 H / WEST STORAGE',ha='center',va='center',rotation=90,fontsize=7,color=g.PAPER)
ax.text(1.79,1.43,'Assumed eye 1120 H',fontsize=8,ha='center');ax.set_title('VIEWING / SECTION THROUGH SOFA',loc='left',fontsize=13,fontweight='bold');ax.axis('off')
fig.text(.045,.95,'223C / VERSION 7 / 77-INCH EAST TV + REFERENCE CABINETS',fontsize=21,fontweight='bold',color=g.INK)
for y,line in [(.12,'3.18 m is measured from the assumed seated eye to the visible screen face; sofa/product posture remains provisional.'),(.085,'West access: about 807 mm behind sofa, 407 mm remaining with a 400 mm door leaf open. Tight, sequential use; comfort unverified.'),(.05,'360 mm north setback. Five 800 mm west units + 630 corner + 800 return; 2350 H. Girls depth/content/night-access limits remain.')]:fig.text(.045,y,line,fontsize=10,color=g.INK)
fig.savefig(OUT/'V7-layout-and-viewing.png',dpi=160,facecolor=g.PAPER);plt.close(fig)

c=Image.new('RGB',(2000,1830),g.PAPER);d=ImageDraw.Draw(c)
d.text((55,30),'223C / VERSION 7 / AMERICAN WALNUT + REEDED GLASS',font=g.font(25),fill=g.GREEN)
d.text((55,75),'77-inch TV east / 3.18 m viewing',font=g.font(48,True),fill=g.INK)
d.text((55,143),'Five 800 mm west units + 630 mm corner + 800 mm return. 350 D / 2350 H. No server.',font=g.font(26),fill=g.INK)
for name,(x,y,w,h) in zip(['V7-east-tv-wall.png','V7-seated-view.png','V7-west-storage.png','V7-girls-cabinets.png'],[(40,205,940,700),(1020,205,940,700),(40,1000,940,640),(1020,1000,940,640)]):g.place(c,name,x,y,w,h)
for x,y,label in [(55,920,'EAST / TV + WALNUT CONSOLE'),(1035,920,'SOFA / ASSUMED SEATED EYE'),(55,1635,'WEST / CABINETS BEHIND SOFA'),(1035,1635,'GIRLS / 800 + 800 + 600 mm')]:d.text((x,y),label,font=g.font(23,True),fill=g.INK)
d.text((55,1690),'Rear sofa gap: 807 mm. Storage access is tight; full product / household comfort checks remain.',font=g.font(25),fill=g.INK)
d.text((55,1735),'Girls: two 800 glass/niche/base units + one 600 open-shelf/drawer unit, all 2350 mm high.',font=g.font(24),fill=g.GREEN)
d.text((55,1775),'Dimensioned proxies; reeded glass and contents illustrative. See review for beam, fitting and night-access limits.',font=g.font(22),fill=g.GREEN)
c.save(OUT/'V7-board.jpg',quality=94)
print('V7_PLAN_AND_BOARD_COMPLETE')
