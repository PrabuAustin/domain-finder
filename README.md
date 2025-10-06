# Domain Finder CLI

A small Python CLI that:
- Generates domain name candidates from a concept
- Checks availability via GoDaddy (with optional Domainr prefilter)
- Prints only the available domains

## Setup

1) Python 3.9+
2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Create a `.env` file with:

```bash
GODADDY_API_KEY=your_key
GODADDY_API_SECRET=your_secret
# Optional: set to OTE for sandbox checks (or leave blank for PROD)
GODADDY_ENV=PROD  # or OTE

# Optional Domainr
DOMAINR_API_KEY=your_domainr_key
```

## Defaults
- Default TLDs: `.com`, `.in`, `.ai`, `.co`, `.io` (used when none provided)

## Semantics
- `/generate` and CLI generation return candidate strings only (no availability filtering). This is by design.
- `/check` and `/find` perform registrar verification. Responses include both `available` and `unavailable` lists.

## CLI Usage

Basic (concept only; defaults used):
```bash
python -m domain_finder.cli "AI e-bike store in India"
```

Add/remove TLDs without overriding defaults:
```bash
python -m domain_finder.cli "AI e-bike store in India" --add-tlds .dev .shop --remove-tlds .co
```

Override TLDs completely:
```bash
python -m domain_finder.cli "AI e-bike store in India" --tlds .com .store
```

Other useful flags:
```bash
python -m domain_finder.cli "AI e-bike store in India" --check-type FULL --use-domainr-prefilter
```

## API Server (Swagger UI)

Run FastAPI server:
```bash
uvicorn domain_finder.api:app --reload --host 0.0.0.0 --port 8000
```
Open Swagger UI at `http://localhost:8000/docs`.

## Deploy to GitHub + Vercel

1) Commit and push to GitHub (new repo):
```bash
git init
git add .
git commit -m "feat: domain finder api + cli"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```
2) In Vercel, "New Project" → Import your GitHub repo.
3) Framework preset: "Other" (Python). Vercel detects `api/index.py`.
4) Set Environment Variables in Vercel dashboard:
   - `GODADDY_API_KEY`, `GODADDY_API_SECRET`, `GODADDY_ENV` (PROD or OTE)
   - Optional: `DOMAINR_API_KEY`
5) Deploy. Your API base URL will be like `https://<project>.vercel.app` → Swagger at `/docs`.

Notes for Vercel
- Config: `vercel.json` routes all paths to `api/index.py` (ASGI app).
- Runtime: Python 3.11; requirements are auto‑installed from `requirements.txt`.
- If you see cold starts, consider keeping the function warm or moving to a small VM.

## References
- GoDaddy Dev Portal: `https://developer.godaddy.com`
- Availability endpoint (commonly used): `https://pipedream.com/apps/godaddy`
- Rate limits: `https://developer.godaddy.com`
- Domainr: `https://domainr.com`
