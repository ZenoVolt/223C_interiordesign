# Version 7 — actual product modules and 360 mm north setback

10 November 2026, Singapore time. Current proposal, parent version 6. Earlier models remain preserved. This implements the owner's latest cabinet dimensions and setback while keeping the east TV, viewing distance, reference styles and no-server instruction.

[Image board](V7-board.jpg) · [Living plan, TV elevation and viewing section](V7-layout-and-viewing.png) · [630 corner detail](V7-l-corner.png) · [Girls cabinets](V7-girls-cabinets.png) · [Editable Blender model](V7-product-modules.blend) · [Dimensions/parameters](layouts.json)

## Owner-confirmed dimensions and arrangement

| Item | Version 7 |
| --- | --- |
| Living straight cabinet range | Available 800 or 900 W; **350 D × 2350 H mm** |
| West run selected | **Five 800 mm units**, 4000 mm total |
| L corner | **630 × 630 × 2350 H mm**, open shelves, from owner's photo |
| Short return | One **800 W × 350 D × 2350 H mm** unit |
| North setback | **360 mm**, owner required |
| Girls run | **800 + 800 + 600 W**, all **2350 H mm**; depth still a **400 mm proxy** |
| Living TV | **77-inch visible 16:9 area**, east wall, freestanding console |
| Assumed viewing distance | **3180 mm**, seated eye to screen front |
| Server | Removed from living by owner direction; no destination elsewhere assumed |

West-wall dimension chain is **40 south gap + 630 corner + 10 join + 4000 cabinets + 360 north setback = 5040 mm**. A 900 + four 800 run would be 100 mm too long with this corner/gap/setback arrangement, so the available 800 mm modules are used throughout the west run. The return begins 10 mm after the corner footprint and ends 60 mm before the short backing wall's east endpoint. West back-wall offset remains about 33 mm.

The real open corner replaces the previous blind void. Its full 630 mm square envelope is reserved. The illustrated L shelf contour uses 350 mm legs and alternating end panels based on the photograph; exact shelf shape, connectors and usable interior dimensions remain unverified. No invented litre capacity is credited. The source photo labels 235 cm height; owner also confirmed 2350 mm height for straight and girls' cabinets.

## Reference appearance and retained decisions

Living: walnut frames, vertical reeded main and separate upper glass pairs, solid lower drawer, brass knobs/hinges. Girls: two 800 units based on the second supplied reference, with upper reeded glass, open book/toy niche and closed wood base; 600 unit based on the first, with open shelves/display stands and four lower drawers. Reference photos are retained in `design/living-room/reference/`. Glass, hardware, timber finish and shown contents are visual approximations, not identified products or actual packing evidence.

Existing shell, fixed girls south wardrobe and study remain intact. Study retains one existing full metal cupboard and two 2000 H Packout stacks with the owner-supplied composition. Girls' two full metal-cupboard content groups remain assigned to their new run. Ten toy-box and eleven study-box contents remain allocated to living storage; repacking is allowed. The reduction from 500 to 350 mm depth **reopens actual content fit**. Previous 621/588 L allowances are not current capacity evidence. Replaced metal carcasses have no in-home destination selected.

## Viewing and access trade-offs

Screen front x=4.970 m and assumed eye x=1.790 m at y=6.950 m give **3180 mm horizontal viewing distance**. Eye height is an assumed 1120 mm, 100 mm ahead of the sofa proxy centre. The visible area is approximately 1705 × 959 mm; the console remains a separately assumed 2000 W × 450 D carcass × 550 H unit, with about 19 mm additional pull projection. Real product feet and seated posture must be checked before purchase.

The 350 mm storage depth increases rear sofa access to about **807 mm**. An assumed 400 mm cabinet leaf leaves about **407 mm** when open: this is a geometric remainder, not an approved walking/standing clearance. Use storage sequentially; actual product hinges and household comfort remain unresolved. Floor play remains **1850 × 1750 mm**. Actual Stressless full recline, guest-chair setup and exact power/AV locations have not been validated.

The north beam model starts 160 mm from the north wall and has a provisional 2255 mm underside. The owner-required 360 mm setback leaves 200 mm in plan before it; the 2350 H units do not intersect it. There is nominally 230 mm to the 2580 mm unfinished ceiling datum; actual installed finishes/levels remain to verify.

Girls' exact 2200 mm run still has **zero spare fitting tolerance**. Night access is at the bed foot: about 910 mm. The 270 mm gap alongside the lower mattress is not a walking route. Full hinged-door and drawer operation remains restricted with the trundle extended; 600 drawer travel and actual hinge geometry need product checks. The new 2350 mm height does not resolve that access issue.

## Checks and next decision

[28 independent saved-file/model checks](fit_checks.json) pass: 246 architectural meshes unchanged, source shell bytes preserved, exact module width/depth/heights, corner envelope, 360 setback and 5040 chain, return endpoint, modelled room/maid door sweeps, west leaf sectors, furniture/play footprints, server removal, 77-inch visible area and 3180 mm eye distance. Final board, plan, corner and girls views were visually inspected. These passes establish the stated model geometry, not site/product/capacity approval.

Recommend this as the current measured comparison: it uses the actual offered sizes and preserves the requested TV assumptions. The next decision is whether the approximately 807 mm rear sofa band works for frequent cupboard use; actual product drawings and a tape-out will decide that. Girls' door/drawer use with the bed open and actual usable contents capacity also remain unresolved. Product prices, availability, delivery and costs in SGD have not been sourced. No purchase, disposal, service alteration or built-in work is authorized by this proposal.

Reproduce with Blender `generate_revision07.py`, then `verify_revision07.py`; generate the board/plan with Python `draw_revision07.py` (which imports shared plan drawing helpers). Baseline and parents are preserved separately.
