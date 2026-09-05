# Backend deployment guide

## Local Flask app

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
gunicorn -b 0.0.0.0:5000 backend.app:app
```

Open:

```text
http://localhost:5000
```

## Render deployment

Use the included `render.yaml` or create a Web Service with:

```bash
gunicorn -b 0.0.0.0:$PORT backend.app:app
```

## COMSOL bridge

The COMSOL connector is a template. Put a verified `.mph` file in `data/` and update parameter names in `backend/comsol_connector.py`. Do not expose a laboratory COMSOL workstation directly to the public internet.
