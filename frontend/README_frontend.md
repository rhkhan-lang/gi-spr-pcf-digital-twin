# GI SPR-PCF Digital Twin V2

A static, upload-ready digital twin for the Au/TiO2/graphene four-groove SPR-PCF biosensor.

## Improvements in V2
- Uses the exact manuscript sensor geometry image as the default geometry view.
- Adds an interactive schematic with the same four-groove topology and eight design variables.
- Adds the actual manuscript Core X/Y and SPP X/Y mode-distribution images.
- Adds 3D and transparent 3D manuscript views.
- Keeps RI-pair interrogation, inverse-design search, and fabrication-tolerance exploration.
- Clearly separates manuscript/FEM assets from the demonstration browser surrogate.

## Deployment
Upload the folder contents to GitHub Pages, Netlify, Cloudflare Pages, or any static website host. `index.html` is the entry point.

## Scientific caution
The current browser predictor is a demonstration surrogate, not a FEM-validated digital-twin model. For a research-grade DT, replace the demo equations with a surrogate trained on your multidimensional COMSOL/FEM database and add OOD/uncertainty estimates plus FEM revalidation of optimized candidates.
