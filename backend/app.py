from __future__ import annotations
import json, os, csv, time
from pathlib import Path
import numpy as np
from flask import Flask, request, jsonify, send_from_directory

try:
    from .surrogate_runtime import store
except ImportError:
    from surrogate_runtime import store

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / 'frontend'
DATA = ROOT / 'data'
VALIDATION_LOG = DATA / 'validation_log.csv'

app = Flask(__name__, static_folder=None)

GEOM_COLS = store.input_cols[:-1]

@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND, filename)

def parse_geometry(body):
    return store.clip_geometry(body)

@app.post('/api/predict')
def predict():
    body = request.get_json(force=True)
    geometry = parse_geometry(body)
    geometry['analyte_ri'] = float(body.get('analyte_ri', 1.39))
    return jsonify({
        'prediction': store.predict_dict(geometry),
        'geometry': {k: geometry[k] for k in GEOM_COLS},
        'analyte_ri': geometry['analyte_ri'],
        'evidence_level': store.meta['model_kind'],
        'warning': store.meta['warning'],
    })

@app.post('/api/pair')
def pair():
    body = request.get_json(force=True)
    geometry = parse_geometry(body)
    n0 = float(body.get('normal_ri', 1.385))
    n1 = float(body.get('pathological_ri', 1.395))
    return jsonify({
        'geometry': geometry,
        'pair': store.pair_metrics(geometry, n0, n1),
        'evidence_level': store.meta['model_kind'],
        'warning': store.meta['warning'],
    })

@app.post('/api/optimize')
def optimize():
    body = request.get_json(force=True)
    n0 = float(body.get('normal_ri', 1.385))
    n1 = float(body.get('pathological_ri', 1.395))
    objective = body.get('objective', 'fom')
    target_lambda = float(body.get('target_resonance_nm', 1800))
    n_candidates = int(np.clip(body.get('n_candidates', 6000), 500, 30000))
    rng = np.random.default_rng(int(body.get('seed', 17)))
    G = store.random_geometries(n_candidates, rng)

    # Build vectorized normal/pathological batches.
    Xn = np.column_stack([G, np.full(n_candidates, n0)])
    Xp = np.column_stack([G, np.full(n_candidates, n1)])
    Yn = store.predict_array(Xn); Yp = store.predict_array(Xp)
    dn = abs(n1-n0) if abs(n1-n0) > 1e-12 else 1e-12
    dl = np.abs(Yp[:,0]-Yn[:,0])
    ws = dl/dn
    fwhm = np.maximum(1e-9, (Yn[:,1]+Yp[:,1])/2)
    fom = ws/fwhm
    D = dl/fwhm
    mean_as = (Yn[:,4]+Yp[:,4])/2

    if objective == 'separability': score = D
    elif objective == 'ws': score = ws
    elif objective == 'target':
        score = fom - 0.002*np.abs(Yn[:,0]-target_lambda)
    elif objective == 'balanced':
        score = (fom/np.percentile(fom,95)) + (D/np.percentile(D,95)) + 0.25*(mean_as/np.percentile(mean_as,95))
    else: score = fom
    idx = int(np.nanargmax(score))
    geom = {k: float(G[idx,j]) for j,k in enumerate(GEOM_COLS)}
    geom['graphene_layers'] = int(round(geom['graphene_layers']))
    pairm = store.pair_metrics(geom, n0, n1)
    return jsonify({
        'objective': objective,
        'score': float(score[idx]),
        'geometry': geom,
        'pair': pairm,
        'evaluated_candidates': n_candidates,
        'warning': 'Optimization is over the synthetic demo surrogate. Full-FEM revalidation is mandatory before research use.'
    })

@app.post('/api/robustness')
def robustness():
    body = request.get_json(force=True)
    geom = parse_geometry(body)
    n0 = float(body.get('normal_ri', 1.385)); n1 = float(body.get('pathological_ri', 1.395))
    n_mc = int(np.clip(body.get('n_mc', 400), 50, 5000))
    rng = np.random.default_rng(int(body.get('seed', 23)))
    rows = []
    for _ in range(n_mc):
        g = dict(geom)
        g['gold_thickness_nm'] += rng.uniform(-1.0, 1.0)
        g['tio2_thickness_nm'] += rng.uniform(-1.0, 1.0)
        for k in ['groove_radius_um','ah1_um','ah2_um','core_width_um','core_height_um']:
            g[k] *= 1+rng.uniform(-0.02,0.02)
        if rng.random() < 0.10:
            g['graphene_layers'] += rng.choice([-1,1])
        g = store.clip_geometry(g)
        m = store.pair_metrics(g, n0, n1)
        rows.append([m['wavelength_sensitivity_nm_per_riu'], m['figure_of_merit_riu_inv'], m['spectral_separability_D']])
    A = np.asarray(rows)
    labels = ['wavelength_sensitivity_nm_per_riu','figure_of_merit_riu_inv','spectral_separability_D']
    summary = {}
    for i,k in enumerate(labels):
        summary[k] = {
            'mean': float(A[:,i].mean()), 'std': float(A[:,i].std(ddof=1)),
            'p05': float(np.percentile(A[:,i],5)), 'p50': float(np.percentile(A[:,i],50)),
            'p95': float(np.percentile(A[:,i],95)), 'worst': float(A[:,i].min())
        }
    return jsonify({'n_mc': n_mc, 'summary': summary,
                    'warning': 'Demo surrogate robustness only; replace with FEM-verified Monte Carlo for publication claims.'})

@app.post('/api/validate')
def validate():
    """Store one externally validated FEM/experimental point for later retraining."""
    body = request.get_json(force=True)
    row = [body.get(k,'') for k in store.input_cols + store.output_cols]
    new = not VALIDATION_LOG.exists()
    with VALIDATION_LOG.open('a', newline='') as f:
        w = csv.writer(f)
        if new: w.writerow(store.input_cols + store.output_cols + ['timestamp_utc'])
        w.writerow(row + [time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())])
    return jsonify({'status':'logged','path':'data/validation_log.csv',
                    'note':'This endpoint logs validated points; it does not silently retrain the public demo model.'})

@app.post('/api/simulate')
def simulate():
    try:
        try:
            from .comsol_connector import connect, query_comsol
        except ImportError:
            from comsol_connector import connect, query_comsol
    except Exception as e:
        return jsonify({'error':'COMSOL bridge unavailable', 'detail':str(e)}), 501
    model_path = DATA/'spr_pcf_four_groove.mph'
    if not model_path.exists():
        return jsonify({'error':'No COMSOL model found', 'detail':f'Expected {model_path.name} in data/ on the machine running this backend.'}), 501
    body = request.get_json(force=True)
    geometry = parse_geometry(body)
    ri = float(body.get('analyte_ri', 1.39))
    x = np.array([geometry[k] for k in GEOM_COLS]+[ri], float)
    if not hasattr(app,'_comsol_model'):
        app._comsol_client, app._comsol_model = connect(str(model_path))
    y = query_comsol(x, app._comsol_model)
    return jsonify({'prediction':{k:float(v) for k,v in zip(store.output_cols,y)},'source':'COMSOL'})

@app.get('/api/status')
def status():
    return jsonify({
        'surrogate_loaded': True,
        'model_kind': store.meta['model_kind'],
        'comsol_model_present': (DATA/'spr_pcf_four_groove.mph').exists(),
        'validation_points': max(0, sum(1 for _ in VALIDATION_LOG.open())-1) if VALIDATION_LOG.exists() else 0,
        'reference_ws_nm_per_riu': store.meta.get('reference_ws_nm_per_riu',{}),
        'reference_archived_as_riu_inv': store.meta.get('reference_archived_as_riu_inv',{}),
        'warning': store.meta['warning'],
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT','5000'))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG')=='1')
