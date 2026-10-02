# 🔗 Shortly - URL Shortener with Click Analytics

A Flask web app that shortens long URLs and tracks click analytics for each link.

## Features
- Shorten any URL with an auto-generated code
- Custom aliases (3-10 alphanumeric characters)
- Click tracking (timestamp, IP address, browser)
- Stats page with a clicks-per-day chart
- Delete links
- Input validation and duplicate alias checks

## Tech Stack
- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML, CSS, Jinja2, Chart.js

## Getting Started

### Prerequisites
- Python 3.9+

### Installation
```bash
git clone https://github.com/<your-username>/url-shortener.git
cd url-shortener
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Project Structure
```
url-shortener/
├── app.py            # Flask app, models and routes
├── requirements.txt
├── static/style.css
└── templates/        # base, index, stats pages
```

## Screenshots
_Add screenshots here (put images in a `screenshots/` folder)._

## Future Improvements
- User accounts and login
- Link expiry dates
- QR code generation
- REST API with authentication
- Deployment with Docker/Gunicorn
