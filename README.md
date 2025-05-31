# FastAPI URL Shortener

A simple URL shortening service built with FastAPI, featuring short code redirects, access logging, and admin access with environment variable authentication.

---

## Features

- Shorten long URLs to short codes
- Redirect short codes to original URLs
- Track visit counts and access logs
- Protected admin endpoint to view recent access logs

---

## Tech Stack

- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite/PostgreSQL
- Uvicorn (ASGI server)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- `pip` package manager
- Database setup (SQLite by default, can use PostgreSQL or others)

### Installation

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root or set environment variables directly:

SECRET_KEY=your-secret-key

Make sure to replace values with your actual secret key and database URL.

### Running the App

```bash
uvicorn main:app --reload
```
Open your browser and visit:

- API docs: http://127.0.0.1:8000/docs
- Alternative docs: http://127.0.0.1:8000/redoc

for documentation on the API and its endpoints

## API Endpoints

- `POST /shorten` - Shorten a long URL
- `GET /{code}` - Redirect to original URL for a given short code
- `GET /admin` - Admin endpoint to view access logs (requires `passwrd` query param matching `SECRET_KEY`)
- `GET /show` - Shows all the urls and shortcode present in the database(requires `show` query param matching `all`) 

## Testing

Run tests using [pytest](https://docs.pytest.org/):

```bash
pytest
```
Sample test cases are provided in `test_main.py` file which can be run using
`pytest test_main.py`

Make sure environment variables like SECRET_KEY are set before running tests.

You can use a .env file or set them in your terminal session.

## Deployment

### Deploying to Render

1. Push your code to a GitHub repository.
2. Go to [https://render.com](https://render.com) and create a new **Web Service**.
3. Connect your GitHub repository.
4. Set the following environment variables in the Render dashboard:
    `SECRET_KEY` – your secret key for admin access
5. Choose:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
6. Deploy the service and Render will handle the rest.

Your FastAPI app will be live at the URL provided by Render.