# Revision 03 — wall-bounded storage and American walnut

9 November 2026. Applies the owner's instruction that A's cupboard must not extend beyond its backing wall, and that new wooden furniture use American walnut. Both A and B use the same corrected storage and finish so their comparison remains consistent.

| Deliverable | A — with TV | B — without TV |
| --- | --- | --- |
| Image board | [A board](A-with-tv-board.jpg) | [B board](B-without-tv-board.jpg) |
| Coordinated plans | [A plan](A-with-tv-triplet-plan.png) | [B plan](B-without-tv-triplet-plan.png) |
| Living storage-wall view | [A storage](A-with-tv-living-storage.png) | [B storage](B-without-tv-living-storage.png) |
| Editable model | [A Blender](A-with-tv.blend) | [B Blender](B-without-tv.blend) |

Shared: [girls' plan](plan-shared-girls.png), [study plan](plan-shared-study.png), [girls day](shared-girls-day.png), [girls night](shared-girls-night.png), [girls storage](shared-girls-storage.png), [study stacks](shared-study.png).

## Wall boundary correction

The living backing wall runs approximately y=5.550–8.487 m in the shell: about 2937 mm. Revision 02's archive cupboard projected beyond its south end. Revision 03 uses:

- Archive cupboard: 800 W × 500 D × 2100 H mm; along-wall span y=5.590–6.390 m.
- Gap: 50 mm.
- Toy/media cupboard: **2000 W × 500 D × 900 H mm**; span y=6.440–8.440 m.
- Total run: 2850 mm, leaving approximately 40 mm at the south end and 47 mm at the north end.

Both bodies and their modelled fronts/handles stay within the wall endpoints. The low cupboard is shorter and 100 mm taller than revision 02. The TV moves onto its centre and rises 100 mm with the unit; its size remains a 65-inch proxy. The proposed toy internal envelope is now about 621 L instead of 653 L, against ten boxes' 450 L nominal capacity. Contents are not discarded; actual shelf/content fit remains unresolved. Archive allowance remains about 588 L against eleven boxes' 495 L nominal capacity.

## Finish

American walnut is applied to the new cupboard carcasses, tops and fronts, the new pull-out bed timber, side table and sofa feet. It is an illustrative procedural wood material, not an approved physical sample, product, stain or veneer match. Upholstery and bedding remain textiles. Retained Stressless wood/leather, stainless-steel cupboards, Packout stacks, existing built-in wardrobe and architectural finishes are retained as existing/proxy materials.

## Constraints carried forward

Both freestanding Packout stacks remain 2000 mm high with the owner-specified module composition. The study still uses only its 2200 mm hinge-side run. The girls' existing sliding wardrobe remains reserved at 600 mm depth.

The girls' room **still has a day/night operating restriction**: full metal-cupboard door access needs the pull-out bed stored. Night access is at the bed foot, approximately 910 mm deep. The 270 mm side gap is not a walking route. This restriction has not been accepted or resolved by the owner and is not changed by the material/wall-boundary edit.

## Checks

[Footprint checks](fit_checks.json) include cupboard endpoints against the backing wall in both variants, while retaining the prior door-sweep, free-floor, fixed-wardrobe and full-height equipment checks. [Saved-file audit](saved_file_audit.json) independently reads the actual saved Blender meshes to confirm cupboard endpoints and walnut fronts, retained full-height stack composition, wardrobe presence and unchanged source architectural geometry. These are geometry/material checks, not product/site or usable-capacity approval.

Reproduce from the project root:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --python 'design\living-room\generate_revision02.py' -- --revision03
python 'design\living-room\verify_designs.py' --revision03
python 'design\living-room\draw_design_plans.py' --revision03
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --python 'design\living-room\verify_saved_designs.py' -- --revision03
```

This saves to revision 03, preserving earlier iterations and the source shell.
