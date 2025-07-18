# EnviroSense

A web application to monitor soil, air, and water quality by location.

## Features
- Select a location on the map
- View soil, air, and water quality data
- Data visualization with charts

## Tech Stack
- Frontend: HTML, CSS, JS, Bootstrap, Leaflet.js, Chart.js
- Backend: Python, Flask
- APIs: WAQI, Ambee (free tier), dummy data for soil/water
- Hosting: Flask serves both frontend and backend

## Project Structure
```
EnviroSense/
├── app.py
├── requirements.txt
├── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── README.md
```

## Setup & Run (Local)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Flask app:
   ```bash
   python3 app.py
   ```
3. Open your browser to [http://localhost:5001](http://localhost:5001)

## Usage
- The app serves both the frontend and API from the same server.
- The API endpoint is `/api/environment?lat=...&lon=...`

## Deployment
- Deploy the whole folder to any Python/Flask-compatible host (Render, Railway, etc.).
- No need to separate frontend and backend.

## Notes
- Update your WAQI API token as needed in your environment variables.
- All static files and the API are served by Flask. 