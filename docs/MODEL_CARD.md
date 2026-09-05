# Model card — packaged demo surrogate

## Purpose
Provide an immediately interactive digital-twin demonstration while the publication-grade multidimensional FEM database is being generated.

## Inputs
1. Au thickness, 18–20 nm
2. TiO2 thickness, 11–13 nm
3. graphene layers, 0–2
4. groove radius, 0.37–0.41 µm
5. ah1, 0.35–0.45 µm
6. ah2, 0.10–0.20 µm
7. core width, 0.13–0.26 µm
8. core height, 0.20–0.40 µm
9. analyte RI, 1.33–1.45

## Outputs
- resonance wavelength;
- FWHM;
- peak confinement-loss proxy;
- local wavelength-sensitivity proxy;
- amplitude-sensitivity proxy.

## Training data
3,200 synthetic, Latin-hypercube-like samples generated from a smooth nonlinear response function anchored to the manuscript calibration and design ranges.

## Validation
The included metrics quantify fit to the *synthetic response function only*. They do not establish accuracy against COMSOL, experiment, or biological samples.

## Prohibited interpretation
Do not cite the packaged model's R2/RMSE as FEM or experimental validation. Do not use it for clinical decision support.

## Replacement criteria
A research-grade model should be trained on a geometry-level FEM database and evaluated using an untouched test set, 5-fold cross-validation, uncertainty calibration, OOD testing, and independent full-FEM verification of optimizer-selected candidates.
