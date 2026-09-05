# Recommended upgrades from demo twin to publication-grade digital twin

## Priority 1 — replace synthetic surrogate with real FEM data

- Generate 300–500 initial Sobol/Latin-hypercube geometries over the eight physical variables.
- Use one common spectral grid and track the same core/SPP resonance branch.
- Export normal/pathological resonance, FWHM, peak loss, WS, AS (only after co-registration), FOM, effective indices, and solver metadata.
- Keep complete geometries together when splitting train/validation/test data.
- Train GPR/ensemble/MLP candidates and report R2, MAE, RMSE, learning curves, uncertainty calibration, and OOD performance.

## Priority 2 — close the digital-twin loop

- Optimizer proposes candidate geometry.
- Surrogate ranks it with uncertainty.
- Candidate is sent to COMSOL.
- FEM result is compared with surrogate prediction.
- Only validated points are admitted to the authoritative dataset.
- Periodically retrain and version the surrogate.

## Priority 3 — fabrication robustness

- Au thickness ±1 nm.
- TiO2 thickness ±1 nm.
- Rgr, ah1, ah2, cw, ch ±2%.
- Add correlated fabrication errors and coating nonuniformity, not just independent uniform noise.
- Report mean, SD, p05, worst-case FOM and separability.

## Priority 4 — real sensor telemetry

When hardware exists, ingest:
- optical-spectrum-analyzer trace;
- source power and polarization;
- temperature;
- flow/sample state;
- calibration reference spectrum;
- coating batch/device ID.

The digital twin can then estimate latent states (effective RI, drift, coating degradation) rather than only predicting from geometry.

## Priority 5 — uncertainty and trust

- Add a distance-to-training-domain/OOD score.
- Refuse or warn on extrapolative requests.
- Display surrogate uncertainty bands on spectra.
- Record model version and dataset hash for every prediction.
- Require FEM confirmation when uncertainty exceeds a threshold.

## Priority 6 — richer inverse design

- Multi-objective Pareto front: worst-case tissue separability, mean FOM, mean |AS|, robustness, fabrication complexity.
- Active learning: acquire geometries where expected improvement and predictive uncertainty are both high.
- Robust Bayesian optimization rather than optimizing a nominal geometry only.
- Compare against OFAT, random search, GA/PSO, and standard Bayesian optimization using the same FEM-call budget.

## Priority 7 — online platform

For a public demo, deploy either:
- `frontend/standalone.html` to GitHub Pages/Netlify; or
- the full Flask app to Replit/Render/Railway/Docker.

For COMSOL integration, keep the public interface separate from the licensed solver using a protected bridge or COMSOL Server.
