# Q1 PDF audit and readiness assessment

## Files audited
- PDF: `Q1_SPR_PCF_ML_DT_Final_Audited_2026.pdf`
- TeX: `Q1_SPR_PCF_ML_DT_Final_Audited_2026.tex`
- Render check: 22 PDF pages rendered to PNG at 150 dpi and reviewed through a contact sheet.

## Technical PDF status
- Compile status: **Pass**.
- Page count: **22 pages**, A4, two-column Elsevier-style layout.
- Missing figures: **0** in the audited build.
- Undefined references: **0** in the audited build.
- Undefined citations: **0** in the audited build.
- Visible unresolved `??` markers: **0** by text extraction.
- PDF preflight: openable, unencrypted, not scanned.
- Remaining LaTeX warnings: mainly harmless bookmark/math-string warnings, float-only page notices, and underfull boxes. These are not fatal, but they should be cleaned if targeting a strict production workflow.

## Corrections applied during audit
1. Copied previously missing figure assets into the compile path.
2. Fixed the stray `\sep` keyword command that had accidentally appeared inside an Introduction paragraph.
3. Replaced the too-wide digital-twin closed-loop equation with a multi-line equation.
4. Switched the DT diagnostic figures from PDF includes to PNG includes to reduce font-embedding issues from generated plots.
5. Strengthened the wording around the DT and surrogate plots so they are described as **demonstrator-format** outputs, not final FEM-validated ML results.

## Visual/layout audit
- The manuscript now compiles and renders without missing figures.
- The Digital Twin interface appears on a dedicated figure page and is visually coherent.
- The surrogate architecture figure is correctly aligned with the stated 9-input, 64-64-32 hidden-layer, 6-output architecture.
- The DT diagnostic plots are readable, but page 12 is dense because it contains three figure blocks. For Q1 submission, move most DT diagnostics to Supplementary Information unless they are generated from real FEM-trained surrogate data.
- Page 15 contains many tissue-response plots. It is acceptable as a figure-heavy results page, but readability would improve if the multi-panel tissue spectra are split between the main paper and Supplementary Information.

## Q1-readiness assessment

### Strong points
- The manuscript now has a coherent Q1-style narrative: FEM baseline + physics-grounded inverse-design framework + DT interface.
- The paper honestly separates the validated FEM baseline from the not-yet-validated ML/DT workflow.
- The DT interface, surrogate architecture, and inverse-design discussion add a modern implementation layer.
- The comparison table and limitation section reduce the risk of overclaiming.

### Major Q1 blockers before final submission
1. **ML/DT plots are currently demonstrator-level.** Q1 reviewers will expect the training curves, parity plots, active-learning curve, and inverse-design convergence to come from a documented FEM/COMSOL dataset, not illustrative data.
2. **The spectral-grid inconsistency remains a scientific limitation.** The manuscript acknowledges that amplitude-sensitivity/phase-matching data and tissue confinement-loss data were exported on different spectral grids. For a strong Q1 submission, regenerate all CL, AS, WS, FWHM, FOM and modal-crossing results on one unified wavelength grid.
3. **Need full surrogate validation.** Add the FEM sampling plan, number of geometries, train/validation/test split, MAE/RMSE/R² for each output, uncertainty calibration, and unseen-geometry FEM verification.
4. **Need robustness with real perturbation simulations.** The tolerance section should include FEM-based perturbation results for Au thickness, TiO₂ thickness, groove radius, air-hole radii, and core dimensions.
5. **Biological RI source table should be strengthened.** Include exact normal/pathological RI values, measurement wavelength, tissue/sample type, temperature if available, and literature source for every GI case.
6. **Reference metadata should be verified.** Several 2025-2026 references and article details should be checked against DOI/publisher records before submission.

## Recommendation
- **PDF/LaTeX production quality:** acceptable draft, about **8/10** after the audit fixes.
- **Scientific Q1 readiness:** about **6.5/10** in its present form, because the DT/ML results are not yet backed by a real FEM-trained surrogate database and the spectral-grid inconsistency remains unresolved.
- **Best submission strategy now:** submit as a careful FEM baseline plus inverse-design/digital-twin framework only if the target journal accepts framework-style computational studies. For a stronger Q1 optics/sensing target, complete the unified FEM reruns and regenerate the surrogate/active-learning plots from actual data.

## Minimal Q1 upgrade checklist
- Regenerate unified wavelength-grid FEM data for all tissue cases.
- Train the 9 -> 64 -> 64 -> 32 -> 6 surrogate on actual FEM data.
- Replace all demonstrator diagnostic plots with real training/parity/optimization logs.
- Add a quantitative validation table with MAE, RMSE and R² for all outputs.
- Add uncertainty/OOD checks and full-FEM verification of optimized candidates.
- Move dashboard screenshots and extra ML diagnostics to Supplementary Information if the main article becomes too figure-heavy.
