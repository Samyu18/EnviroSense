# EnviroSense

A web application to monitor soil, air, and water quality by location.

## Features
- Select a location on the map
- View soil, air, and water quality data (real or demo)
- Data visualization with charts
- Works on desktop and mobile

## Deployment

### Backend (Flask API)
1. Go to the `backend/` folder.
2. Deploy to [Render](https://render.com/) or [Railway](https://railway.app/) as a Python web service.
   - Use `backend/requirements.txt` and `backend/Procfile`.
   - The entrypoint is `backend/app.py`.
3. After deployment, note your backend URL (e.g., `https://your-backend.onrender.com`).

### Frontend (GitHub Pages)
1. Go to the `frontend/` folder.
2. Edit `main.js` and set `BACKEND_URL` to your deployed backend API URL (e.g., `https://your-backend.onrender.com/api`).
3. Push the contents of `frontend/` to a GitHub repository.
4. Enable GitHub Pages in your repo settings (set source to `/frontend` or root, as needed).
5. Visit your GitHub Pages site and use the app!

## Project Structure
```
EnviroSense/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Procfile
├── frontend/
│   ├── index.html
│   └── main.js
├── README.md
```

## Notes
- The frontend will not work unless you set `BACKEND_URL` in `main.js` to your deployed backend API.
- Demo/sample data is shown if real data is not available for a location. 