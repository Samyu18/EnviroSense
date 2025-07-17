# EnviroSense

A Flask web app to monitor soil, air, and water quality by location.

## Features
- Real and demo data for soil, air, and water
- Mobile-friendly, interactive map

## How to Deploy (Render/Railway/Heroku)
1. Fork or clone this repo.
2. Make sure you have these files: `app.py`, `requirements.txt`, `Procfile`.
3. Push to GitHub.
4. Create a new web service on [Render](https://render.com), [Railway](https://railway.app), or [Heroku](https://heroku.com).
5. Connect your GitHub repo and deploy as a Python web service.
6. The service will auto-detect `Procfile` and run the app.

## Local Development
```bash
pip install -r requirements.txt
python3 app.py
```

## Notes
- The app will always show data (real if available, demo otherwise).
- For best results, deploy to a free Python web host (Render, Railway, Heroku). 