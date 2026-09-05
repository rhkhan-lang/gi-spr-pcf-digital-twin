# GI SPR-PCF Digital Twin — Full GitHub Package

This repository contains a complete digital-twin package for the proposed Au/TiO₂/graphene-coated four-groove SPR-PCF biosensor for normal/pathological gastrointestinal tissue RI interrogation.

## What is included

- `index.html`: static GitHub Pages entrypoint.
- `frontend/`: interactive browser digital twin.
- `backend/`: Flask API, surrogate runtime and COMSOL connector template.
- `data/`: demo surrogate files, manuscript reference-performance values and FEM database templates.
- `docs/`: GitHub upload guide, deployment guide, DT architecture notes, publication disclosure note and validation TODO list.
- `manuscript/`: audited TeX/PDF manuscript support and DT manuscript figures.
- `deploy/`: static/GitHub Pages, Render and Replit helper notes.

## Open locally without a server

Double-click `index.html` or open it in a browser.

## Run full backend locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
gunicorn -b 0.0.0.0:5000 backend.app:app
```

Then open `http://localhost:5000`.

## GitHub Pages upload

Upload the complete contents of this folder to a GitHub repository and enable **Settings → Pages → Deploy from branch → main → /root**.

## Scientific status warning

The browser predictor and demo validation files are demonstration-level surrogate outputs. They are included to show the digital-twin workflow. Before reporting publication-grade digital-twin prediction accuracy, replace them with a FEM-trained and independently validated surrogate, then regenerate the validation, active-learning, inverse-design and tolerance figures.
