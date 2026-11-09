# 223C — existing architectural shell, version 02

Open **223C_Existing_Shell_v02.blend** in Blender 4.5 or newer. Version 01 is retained as the initial shell.

Version 02 moves the service-yard window onto the east wall as a three-panel slider above a confirmed 1000 mm-high wall; reverses the maid door to open outward; swaps study/girls door hinge sides without moving their doorways; and relocates the master door upper hinge to the centre of the 145 mm segment between the 365 and 1405 dimensions, across the passage to the bathrooms.

The scene uses metres internally and displays millimetres. Finished floor is Z=0; the unfinished ceiling underside is Z=2580 mm. Existing walls, doors, windows, beams and the confirmed 150 mm ceiling drop are separate editable objects. No loose furniture has been added.

## Review images

- `previews/01_architectural_shell.png` — whole-home overview.
- `previews/02_floor_plan.png` — labelled top view, with beams hidden.
- `previews/03_ceiling_structure.png` — beams and the confirmed false ceiling, with walls hidden.
- `previews/04_service_yard_window.png` — closer view of the corrected east-wall window.

## Working in Blender

- Collection **13 | Loose furniture** is ready for the next iteration.
- Toggle collection **06 | Beams** to inspect furniture placement without overhead obstructions.
- Collection **10 | Unfinished ceiling slab** starts hidden for the overview. Its underside is exactly 2580 mm; its thickness is a viewing aid.
- Collection **12 | Packed reference plans** contains both original plan images. They are packed into the file.
- Doors are parented to labelled hinge empties. Rotate a hinge around Z to swing its door.
- Six cameras are included: overall, top, ceiling structure, kitchen eye level, living eye level, and service-yard window.
- Collection **99 | Internal junction cutters** is a hidden modelling helper. Keep it for the non-destructive wall/beam junctions.

## Measurements and assumptions

`MODEL_NOTES.txt` and the Blender text block **READ ME — confirmed facts and assumptions** distinguish supplied facts from assumptions. Window elevations, door heights/hinge sides, some unlabelled beam drops, AC ledge details, finishes and the 60 mm bathroom floor drop remain provisional. Only the false ceiling explicitly shown in the beam sketch has been included.

The written 3610 mm study/girls room depth and 2285 mm maid room depth override small raster discrepancies. Fifteen independent clear-dimension measurements on the saved wall geometry pass a 5 mm raster tolerance; see `geometry_audit.json`. This check does not resolve inconsistent minor dimension chains or establish the accuracy of assumed openings/elevations.

## Rebuild

Editable elevation and finish assumptions are in `model_settings.json`; the wall layout and beam rectangles are in `build_house.py`. Run from this project folder:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --python 'model\build_house.py'
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --python 'model\verify_saved_model.py'
```

Rebuilding replaces the version 02 file and its four previews. Save furniture iterations under a new filename before rebuilding the source shell.
