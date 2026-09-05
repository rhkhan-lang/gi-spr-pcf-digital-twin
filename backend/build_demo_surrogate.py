"""Build a browser-portable demo surrogate for the four-groove Au/TiO2/graphene SPR-PCF.

IMPORTANT
---------
This script creates a *synthetic physics-grounded demonstration surrogate* anchored to
parameter ranges and baseline values reported in the manuscript. It is NOT a replacement
for the multidimensional COMSOL/FEM database required for a publication-grade digital twin.
Replace `synthetic_response()` data with verified FEM rows and retrain before using the app
for research claims.
"""
from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

INPUT_COLS = [
    "gold_thickness_nm", "tio2_thickness_nm", "graphene_layers",
    "groove_radius_um", "ah1_um", "ah2_um", "core_width_um",
    "core_height_um", "analyte_ri"
]
OUTPUT_COLS = [
    "resonance_wavelength_nm", "fwhm_nm", "peak_loss_db_cm",
    "local_ws_nm_per_riu", "amplitude_proxy_riu_inv"
]
BOUNDS = {
    "gold_thickness_nm": (18.0, 20.0),
    "tio2_thickness_nm": (11.0, 13.0),
    "graphene_layers": (0.0, 2.0),
    "groove_radius_um": (0.37, 0.41),
    "ah1_um": (0.35, 0.45),
    "ah2_um": (0.10, 0.20),
    "core_width_um": (0.13, 0.26),
    "core_height_um": (0.20, 0.40),
    "analyte_ri": (1.33, 1.45),
}
BASELINE = {
    "gold_thickness_nm": 19.0,
    "tio2_thickness_nm": 12.0,
    "graphene_layers": 1.0,
    "groove_radius_um": 0.39,
    "ah1_um": 0.40,
    "ah2_um": 0.15,
    "core_width_um": 0.26,
    "core_height_um": 0.40,
    "analyte_ri": 1.39,
}

# Reference deterministic FEM values reported in the manuscript; these are displayed in
# the app as literature/manuscript reference values and are NOT training labels here.
REFERENCE_WS = {
    "Esophageal tumor": 8695.65,
    "Pancreatic adenocarcinoma": 4583.33,
    "IPMN": 4090.91,
    "Tubulovillous adenoma": 2105.26,
    "Colon adenocarcinoma": 2000.00,
    "Metastatic liver tissue (MET)": 2162.16,
    "Hepatocellular carcinoma (HCC)": 2013.42,
}
REFERENCE_AS = {
    "Esophageal tumor": -375.93,
    "Pancreatic adenocarcinoma": -953.79,
    "IPMN": -680.56,
    "Tubulovillous adenoma": -240.74,
    "Colon adenocarcinoma": -175.34,
    "Metastatic liver tissue (MET)": 235.73,
    "Hepatocellular carcinoma (HCC)": 221.12,
}


def _norm_geometry(x: np.ndarray) -> np.ndarray:
    """Map 8 geometry dimensions into approximately [-1, 1]."""
    centers = np.array([19.0, 12.0, 1.0, .39, .40, .15, .195, .30])
    scales  = np.array([1.0, 1.0, 1.0, .02, .05, .05, .065, .10])
    return (x[..., :8] - centers) / scales


def synthetic_response(X: np.ndarray, noise: bool = True, seed: int | None = None) -> np.ndarray:
    """Smooth nonlinear stand-in for a full FEM response.

    It deliberately contains coupled interactions so the inverse design task is genuinely
    multidimensional. The baseline resonance is anchored near the manuscript calibration
    lambda_res = 3455.32*n - 3035.55 around n=1.39, while geometry can modify the local slope.
    """
    X = np.atleast_2d(X).astype(float)
    z = _norm_geometry(X)
    ri = X[:, 8]

    # A hidden coupled optimum close to, but not exactly at, the OFAT baseline.
    zopt = np.array([0.20, 0.25, 0.0, 0.40, 0.30, -0.25, 0.70, 0.65])
    sig  = np.array([0.80, 0.80, 0.85, 0.85, 0.90, 0.85, 0.90, 0.90])
    q = np.exp(-0.5 * np.sum(((z - zopt) / sig) ** 2, axis=1))

    # Non-separable interactions emulate the coupled dispersion/coupling landscape.
    inter = (0.16*z[:,0]*z[:,1] + 0.10*z[:,3]*z[:,4]
             -0.11*z[:,2]*z[:,5] + 0.08*z[:,6]*z[:,7])

    local_ws = 2450 + 5200*q + 750*inter + 240*np.sin(1.2*z[:,3]-0.7*z[:,5])
    local_ws = np.clip(local_ws, 1500, 9000)

    # Calibration anchor from the manuscript at n=1.39, plus geometry-dependent shift.
    lam_ref = 3455.32*1.39 - 3035.55
    geo_shift = (24*z[:,0] + 18*z[:,1] + 22*z[:,2] + 38*z[:,3]
                 + 28*z[:,4] - 20*z[:,5] + 34*z[:,6] + 30*z[:,7]
                 + 12*z[:,0]*z[:,1] + 8*z[:,3]*z[:,4])
    resonance = lam_ref + geo_shift + local_ws*(ri-1.39) + 5000*(ri-1.39)**2

    # Narrower linewidth near the coupled optimum; penalties away from it.
    fwhm = 36 + 54*(1-q) + 7*np.abs(inter) + 5*(ri-1.39)**2/0.06**2
    fwhm = np.clip(fwhm, 28, 125)

    # Peak confinement-loss proxy, consistent with the hundreds of dB/cm scale in source plots.
    peak_loss = 180 + 610*q + 55*z[:,0] - 35*z[:,5] + 45*z[:,3]*z[:,4]
    peak_loss = np.clip(peak_loss, 80, 820)

    # Auxiliary amplitude-sensitivity proxy. It is deliberately labeled as a proxy in the UI
    # because the archived AS spectra in the manuscript are not spectrally co-registered.
    as_proxy = 120 + 900*q + 100*np.abs(inter) + 80*np.maximum(0, -z[:,5])
    as_proxy = np.clip(as_proxy, 120, 1100)

    Y = np.column_stack([resonance, fwhm, peak_loss, local_ws, as_proxy])
    if noise:
        rng = np.random.default_rng(seed)
        Y = Y + rng.normal(0, [1.2, 0.7, 4.0, 18.0, 4.0], size=Y.shape)
    return Y


class DemoNet(nn.Module):
    def __init__(self, n_in=9, n_out=5):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_in, 32), nn.SiLU(),
            nn.Linear(32, 32), nn.SiLU(),
            nn.Linear(32, 16), nn.SiLU(),
            nn.Linear(16, n_out),
        )
    def forward(self, x):
        return self.net(x)


def latin_hypercube(n: int, d: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # Minimal dependency-free Latin hypercube.
    u = (np.arange(n)[:, None] + rng.random((n, d))) / n
    out = np.empty_like(u)
    for j in range(d):
        out[:, j] = u[rng.permutation(n), j]
    return out


def sample_design(n: int, seed: int) -> np.ndarray:
    unit = latin_hypercube(n, 9, seed)
    lo = np.array([BOUNDS[c][0] for c in INPUT_COLS])
    hi = np.array([BOUNDS[c][1] for c in INPUT_COLS])
    X = lo + unit*(hi-lo)
    # Graphene is physically discrete.
    X[:,2] = np.clip(np.rint(X[:,2]), 0, 2)
    return X


def metrics(y, yp):
    err = yp-y
    rmse = np.sqrt(np.mean(err**2, axis=0))
    mae = np.mean(np.abs(err), axis=0)
    ssr = np.sum(err**2, axis=0)
    sst = np.sum((y-y.mean(axis=0))**2, axis=0)
    r2 = 1-ssr/sst
    return rmse, mae, r2


def main():
    torch.manual_seed(8)
    np.random.seed(8)
    X = sample_design(3200, 42)
    Y = synthetic_response(X, noise=True, seed=42)
    Xtest = sample_design(800, 777)
    Ytest = synthetic_response(Xtest, noise=False)

    x_mean = X.mean(0).astype(np.float32); x_scale = X.std(0).astype(np.float32)
    y_mean = Y.mean(0).astype(np.float32); y_scale = Y.std(0).astype(np.float32)
    Xn = torch.tensor((X-x_mean)/x_scale, dtype=torch.float32)
    Yn = torch.tensor((Y-y_mean)/y_scale, dtype=torch.float32)

    model = DemoNet()
    opt = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=1e-5)
    bs = 512
    for epoch in range(220):
        perm = torch.randperm(len(Xn))
        for i in range(0, len(Xn), bs):
            idx = perm[i:i+bs]
            opt.zero_grad()
            pred = model(Xn[idx])
            loss = nn.functional.smooth_l1_loss(pred, Yn[idx])
            loss.backward(); opt.step()
        if epoch in (120, 185):
            for g in opt.param_groups: g['lr'] *= 0.35

    model.eval()
    with torch.no_grad():
        predn = model(torch.tensor((Xtest-x_mean)/x_scale, dtype=torch.float32)).numpy()
    Ypred = predn*y_scale+y_mean
    rmse, mae, r2 = metrics(Ytest, Ypred)

    ckpt = {
        "model_state": model.state_dict(),
        "x_mean": x_mean, "x_scale": x_scale,
        "y_mean": y_mean, "y_scale": y_scale,
        "input_cols": INPUT_COLS, "output_cols": OUTPUT_COLS,
        "bounds": BOUNDS, "baseline": BASELINE,
    }
    torch.save(ckpt, DATA/"surrogate_demo.pt")

    compact_weights = {k: np.round(v.detach().cpu().numpy(), 7).tolist()
                       for k,v in model.state_dict().items()}
    compact = {
        "model_kind": "synthetic_physics_grounded_demo",
        "warning": "Not FEM-validated. Replace with a surrogate trained on the multidimensional FEM database before research use.",
        "weights": compact_weights,
        "x_mean": x_mean.tolist(), "x_scale": x_scale.tolist(),
        "y_mean": y_mean.tolist(), "y_scale": y_scale.tolist(),
        "input_cols": INPUT_COLS, "output_cols": OUTPUT_COLS,
        "bounds": {k:list(v) for k,v in BOUNDS.items()},
        "baseline": BASELINE,
        "reference_ws_nm_per_riu": REFERENCE_WS,
        "reference_archived_as_riu_inv": REFERENCE_AS,
    }
    with open(DATA/"surrogate_weights_compact.json", "w") as f:
        json.dump(compact, f, separators=(",",":"))

    report = {
        "n_synthetic_train": len(X), "n_synthetic_test": len(Xtest),
        "model": "9-32-32-16-5 MLP, SiLU",
        "important_warning": "Metrics below assess fit to the synthetic demo response only; they are not FEM validation metrics.",
        "per_output": {
            OUTPUT_COLS[i]: {"rmse": float(rmse[i]), "mae": float(mae[i]), "r2": float(r2[i])}
            for i in range(len(OUTPUT_COLS))
        }
    }
    with open(DATA/"surrogate_demo_metrics.json", "w") as f: json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
