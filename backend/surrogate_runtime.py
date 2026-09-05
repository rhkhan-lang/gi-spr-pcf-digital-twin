from __future__ import annotations
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

class SurrogateRuntime:
    def __init__(self, json_path: str | None = None):
        path = Path(json_path) if json_path else DATA / 'surrogate_weights_compact.json'
        self.meta = json.loads(path.read_text())
        self.input_cols = self.meta['input_cols']
        self.output_cols = self.meta['output_cols']
        self.bounds = self.meta['bounds']
        self.baseline = self.meta['baseline']
        self.x_mean = np.asarray(self.meta['x_mean'], float)
        self.x_scale = np.asarray(self.meta['x_scale'], float)
        self.y_mean = np.asarray(self.meta['y_mean'], float)
        self.y_scale = np.asarray(self.meta['y_scale'], float)
        W = self.meta['weights']
        self.layers = []
        for idx in (0, 2, 4, 6):
            self.layers.append((np.asarray(W[f'net.{idx}.weight'], float), np.asarray(W[f'net.{idx}.bias'], float)))

    @staticmethod
    def silu(x):
        return x / (1.0 + np.exp(-np.clip(x, -60, 60)))

    def predict_array(self, X):
        X = np.atleast_2d(np.asarray(X, float))
        h = (X - self.x_mean) / self.x_scale
        for i, (w, b) in enumerate(self.layers):
            h = h @ w.T + b
            if i < len(self.layers)-1:
                h = self.silu(h)
        return h * self.y_scale + self.y_mean

    def row_from_dict(self, d):
        return np.asarray([float(d[k]) for k in self.input_cols], float)

    def predict_dict(self, d):
        y = self.predict_array(self.row_from_dict(d))[0]
        return {k: float(v) for k, v in zip(self.output_cols, y)}

    def pair_metrics(self, geometry, normal_ri, pathological_ri):
        g = dict(geometry)
        g['analyte_ri'] = float(normal_ri)
        yn = self.predict_array(self.row_from_dict(g))[0]
        g['analyte_ri'] = float(pathological_ri)
        yp = self.predict_array(self.row_from_dict(g))[0]
        dn = abs(float(pathological_ri)-float(normal_ri))
        dl = abs(float(yp[0]-yn[0]))
        ws = dl/dn if dn > 1e-12 else float((yn[3]+yp[3])/2)
        fwhm_avg = max(1e-9, float((yn[1]+yp[1])/2))
        fom = ws/fwhm_avg
        D = dl/fwhm_avg
        return {
            'normal': {k: float(v) for k,v in zip(self.output_cols, yn)},
            'pathological': {k: float(v) for k,v in zip(self.output_cols, yp)},
            'delta_ri': dn,
            'delta_lambda_nm': dl,
            'wavelength_sensitivity_nm_per_riu': ws,
            'mean_fwhm_nm': fwhm_avg,
            'figure_of_merit_riu_inv': fom,
            'spectral_separability_D': D,
        }

    def clip_geometry(self, d):
        out = {}
        for k in self.input_cols:
            if k == 'analyte_ri':
                continue
            lo, hi = self.bounds[k]
            val = float(d.get(k, self.baseline[k]))
            if k == 'graphene_layers':
                val = round(val)
            out[k] = float(np.clip(val, lo, hi))
        return out

    def random_geometries(self, n, rng):
        cols = self.input_cols[:-1]
        X = np.zeros((n, len(cols)), float)
        for j,k in enumerate(cols):
            lo,hi = self.bounds[k]
            X[:,j] = rng.uniform(lo,hi,n)
        X[:,2] = np.rint(X[:,2])
        return X

store = SurrogateRuntime()
