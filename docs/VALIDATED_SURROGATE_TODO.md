# Validated surrogate TODO list

For Q1-level publication claims, complete these tasks:

1. Generate a multidimensional COMSOL/FEM database across the nine input dimensions.
2. Split data by geometry, not by neighboring RI points from the same geometry.
3. Train surrogate models for resonance wavelength, peak confinement loss, FWHM, sensitivity, FOM and separability.
4. Report MAE, RMSE, R² and parity plots on held-out geometries.
5. Run inverse-design candidates back through FEM for verification.
6. Replace all files labeled `demo/synthetic placeholder`.
7. Recreate the DT figures from real training logs and simulator query histories.
