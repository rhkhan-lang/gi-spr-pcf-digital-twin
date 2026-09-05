# Digital-twin architecture for the four-groove Au/TiO2/graphene SPR-PCF

## Current demo architecture

Browser UI
→ compact neural surrogate (runs in browser or Flask API)
→ pair metrics (resonance shift, WS, FWHM, FOM, separability)
→ inverse-design search
→ fabrication robustness Monte Carlo

Optional:
Browser UI → Flask `/api/simulate` → local COMSOL/MPh bridge → `.mph` model.

The shipped surrogate is synthetic and exists only to make the twin demonstrable before the multidimensional FEM database is available.

## Recommended research-grade architecture

1. **Authoritative physics asset**: versioned COMSOL model, material definitions, mesh settings, solver version, and spectral extraction scripts.
2. **Data layer**: geometry-level FEM database with full provenance, run IDs, hashes, solver settings, tissue RI source, and uncertainty metadata.
3. **Model layer**: ensemble/GPR/MLP surrogate with immutable model versions, train/test split by geometry, calibration metrics, OOD detector, and uncertainty estimates.
4. **Twin service**: REST API for prediction, inverse design, robustness, and validation.
5. **Validation loop**: every accepted optimizer candidate is re-simulated in full FEM before it can be marked “verified”.
6. **Experimental layer**: later add OSA spectra, environmental telemetry (temperature, humidity), sample metadata, and calibration status.
7. **Governance**: authentication, audit log, model/data version IDs, reproducible containers, automated tests, and clear research-vs-clinical disclaimers.

## Cloud + COMSOL pattern

A public cloud site cannot normally control a COMSOL desktop installation on a private computer. Use one of these patterns:

- **Surrogate-only public twin**: safest and easiest for a public research demo.
- **Protected COMSOL Server / licensed VM**: host COMSOL on a licensed server reachable only by the backend through VPN/private networking.
- **Local outbound bridge**: a small agent running beside COMSOL polls or receives authenticated jobs from the cloud and posts results back. This avoids opening inbound ports on the laboratory workstation.

Do not expose a raw COMSOL port or desktop machine directly to the internet.
