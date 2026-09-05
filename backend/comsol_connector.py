"""Optional local COMSOL bridge for the four-groove Au/TiO2/graphene SPR-PCF.

This file is a carefully drafted integration template and cannot be end-to-end verified without
COMSOL + a licensed model. It should run on the workstation/VM that owns the COMSOL license.
Do not expose COMSOL directly to the public internet; use this through a protected backend,
VPN, or an outbound local-agent workflow.

Expected COMSOL global parameter names
-------------------------------------
Gt_nm, TiO2_nm, graphene_layers, Rgr_um, ah1_um, ah2_um, cw_um, ch_um, analyte_RI

Expected derived-value expressions (rename below if your model differs)
---------------------------------------------------------------------
resonance_lambda_nm, fwhm_nm, peak_loss_dbcm, local_ws_nm_riu, amplitude_sensitivity_riu_inv
"""
from __future__ import annotations
import numpy as np
import mph  # optional: pip install mph, requires local COMSOL installation

PARAMS = [
    ('Gt_nm','nm'), ('TiO2_nm','nm'), ('graphene_layers',''),
    ('Rgr_um','um'), ('ah1_um','um'), ('ah2_um','um'),
    ('cw_um','um'), ('ch_um','um'), ('analyte_RI','')
]
EXPRESSIONS = [
    ('resonance_lambda_nm','nm'),
    ('fwhm_nm','nm'),
    ('peak_loss_dbcm',''),
    ('local_ws_nm_riu',''),
    ('amplitude_sensitivity_riu_inv',''),
]

def connect(model_path: str):
    client = mph.start(cores=4)
    model = client.load(model_path)
    return client, model


def query_comsol(x_phys_row, model, study_name='Study 1'):
    x = np.asarray(x_phys_row, float)
    if x.size != 9:
        raise ValueError('Expected 9 values: 8 geometry parameters + analyte_RI')
    for (name,unit),value in zip(PARAMS,x):
        if name == 'graphene_layers':
            value = int(round(value))
        expr = f'{value} [{unit}]' if unit else f'{value}'
        model.parameter(name, expr)

    # Depending on your COMSOL topology, geometry changes may require model.build()/mesh()
    # before solve(). Verify node names in a one-point smoke test.
    model.solve(study_name)

    out = []
    for expr,unit in EXPRESSIONS:
        val = model.evaluate(expr, unit) if unit else model.evaluate(expr)
        out.append(float(np.squeeze(val)))
    return np.asarray(out, float)


def smoke_test(model_path='spr_pcf_four_groove.mph'):
    client, model = connect(model_path)
    x = np.array([19,12,1,0.39,0.40,0.15,0.26,0.40,1.39],float)
    print('input',x)
    print('output',query_comsol(x,model))
    client.remove(model)

if __name__ == '__main__':
    smoke_test()
