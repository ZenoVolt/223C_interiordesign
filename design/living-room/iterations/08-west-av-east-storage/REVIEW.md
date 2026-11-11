# Version 8 — centred west AV and three east cabinets

New proposal after [V7](../07-product-modules-360-setback/REVIEW.md); all parent models and the architectural shell are preserved. Implements the owner's new west TV/console/KEF arrangement and tentative three-cabinet east wall. Overall layout, contents fit and acoustics are not yet accepted.

[Image board](V8-board.jpg) · [Measured plan / west elevation / viewing section](V8-layout-and-viewing.png) · [Editable Blender model](V8-west-av-east-storage.blend) · [Seated view](V8-seated-view.png) · [East storage view](V8-east-storage.png) · [Parameters](layouts.json) · [Saved-model checks](fit_checks.json)

## Arrangement and dimensions

| Component | Version 8 |
| --- | --- |
| East tall storage | **3 × 900 W × 350 D × 2350 H mm**, walnut/reeded reference fronts. Quantity is a proposal |
| West console | **About 2590 W**, 450 D carcass + 19 mm pull projection, 550 H; provisional loose console |
| West TV | **77-inch visible 16:9**, about 1705 × 959 mm active area; proxy outer width 1727 mm |
| Width proportion | **Physical, bezel-inclusive TV width = 2/3 console width**, rather than diagonal or area |
| Viewing | **3180 mm** horizontal distance from assumed seated eye to screen front |
| Speakers | **Pair of KEF Q11 Meta**, full **1112 H × 317 W × 380 D mm** terminal/plinth envelopes |
| AV symmetry | Console, TV and pair midpoint at **y=5.966667 m**, centre of the full 5040 mm west wall |
| Speaker starting positions | Centres 3200 mm apart, 10° toe-in, around 300 mm bounding-envelope rear clearance |
| Floor play | **1600 × 1870 mm**, about 2.99 m² |

The speaker dimensions are from [KEF's official Q11 Meta specifications](https://international.kef.com/products/q11-meta); see the [official Q Series manual](https://images.salsify.com/image/upload/s--oYdpVA3V--/ebnntv3ljqcad5t2iefe.pdf) for product setup. Walnut appearance, cone locations and body detailing are illustrative. Speaker starting positions are design assumptions, not measured acoustic results. Amplifier/source equipment and cable routes have not been selected.

The east backing wall is about 2937 mm long. A geometrically centred 2700 mm high-cabinet run would intersect the north beam. This proposal starts at **y=5.590 m** and ends **8.290 m**, leaving about **37 mm in plan before the beam**, 40 mm at the south backing-wall end and 197 mm to the north wall. Verify actual site/ceiling/tolerances before selecting furniture. The former 360 mm west cabinet setback is not transferred to the east wall; every west AV component now ends about 731 mm before the west wall's north/south endpoints.

The screen face is **x=0.103333 m**, the assumed seated eye **x=3.283333 m**, at the same y axis. Assumed eye height remains 1120 mm and eye offset 100 mm toward the screen from the sofa proxy centre. Actual TV bezel/stand and sofa/posture may change console sizing or seating position.

## Benefits and trade-offs

This version gives a centred, balanced AV wall with the requested large-console proportion. The former tall west run, open corner and return are removed. The sofa faces west and the Stressless chair/footstool move to the north end. Girls' room, study and fixed wardrobe are unchanged, verified against the saved parent geometry; server remains removed.

Rear sofa-to-east-front clearance is about **807 mm**. A nominal **450 mm leaf** leaves about **357 mm** with the door open: sequential cupboard use, not a comfortable passage approval. Actual hinges, drawers, retained recliner full operation, north window access, guest seating and complete household routes still need confirmation. A 1270 mm geometric band across the south living area remains free of furniture; it is not a general accessibility standard or whole-route certification.

Tall straight storage falls from **4800 mm in V7 to 2700 mm**, about **44% less frontage**, with the open corner also removed. All **21 box contents remain required**, repacking allowed. Their provisional destination is the east run; the low console adds storage but is not automatically equivalent capacity. Actual interior/content fit and any overflow remain **unresolved**. The three existing full-cupboard content groups remain required: two in the girls' new run and one in the study. No purge or unspecified destination has been assumed.

Girls' 800/800/600 mm units remain 2350 H, with 400 D still provisional. Their exact 2200 mm run has zero spare fitting tolerance and full door/drawer operation still depends on bed state. These limits do not improve merely because the living room changed.

## Validation and recommendation

**29 saved-model checks pass**: unchanged architecture and parent/source bytes; girls/study mesh identity; three 900 × 350 × 2350 units; beam/wall separation; actual 77-inch visible area and exact physical 2/3 width ratio; 3180 mm eye distance; west-wall symmetry; complete KEF envelopes; speaker/TV/console and other furniture footprints; cabinet and room-door sweeps; floor play and entry band. Final plans and four rendered views were visually inspected.

Geometry passes are separate from feasibility: actual contents, acoustic performance, product hardware, site levels, comfort and budget remain unresolved. No products/prices in SGD have been sourced and no purchase or fixed-service work is implied.

Recommend keeping this as the **AV-focused comparison with V7**. The next decision is whether three east cabinets can retain the actual stored contents while giving acceptable access behind the sofa. Speaker positions should then be tuned in the room. Reproduce using Blender `generate_revision08.py` and `verify_revision08.py`, followed by Python `draw_revision08.py`.
