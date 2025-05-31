from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pydantic import BaseModel, HttpUrl, Field

from hashlib import sha256
import base64

from datetime import datetime
import os

from database import engine, SessionLocal
import model

app = FastAPI(
    title="URL Shortener API", description="A simple API to shorten and resolve URLs."
)
origins = ["http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)

model.Base.metadata.create_all(bind=engine)


@app.get("/hello", description="hello")
def hello():
    return "Hi, How you doing ?"


@app.get("/", summary="Github link", description="Returns github repository link")
def about():
    return {"About Page": "https://github.com/aby-jo/URL_Shortener"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class URLRequest(BaseModel):
    long_url: HttpUrl = Field(..., description="The original long URL to shorten")


class URLResponse(BaseModel):
    id: int = Field(..., description="Unique ID of the shortened URL record")
    short_code: str = Field(..., description="Generated short code")
    created_at: datetime = Field(
        ..., description="Timestamp when the short URL was created"
    )


@app.post(
    "/shorten",
    response_model=URLResponse,
    summary="Create short URL",
    description="Generate a short URL code from a long URL.",
)
def shorten(request: URLRequest, db: Session = Depends(get_db)):
    url = str(request.long_url)
    exisiting_url = (
        db.query(model.ShortURL).filter(model.ShortURL.original_url == url).first()
    )
    if exisiting_url:
        return {
            "id": exisiting_url.uuid,
            "short_code": exisiting_url.short_code,
            "created_at": exisiting_url.created_at,
        }
    shortcode = url_shortener(url)
    while True:
        newurl = model.ShortURL(original_url=url, short_code=shortcode)
        try:
            db.add(newurl)
            db.commit()
            db.refresh(newurl)
            break
        except IntegrityError:
            db.rollback()
            shortcode = url_shortener(url, salt=True, prevcode=shortcode)

    return {
        "id": newurl.uuid,
        "short_code": newurl.short_code,
        "created_at": newurl.created_at,
    }


def url_shortener(url, salt=False, prevcode=None):
    if not salt:
        return short_code_generator(url)
    if prevcode is None:
        raise ValueError("prevcode must be provided when salt=True")
    salting_charater = "x"
    newcode = prevcode
    while newcode == prevcode:
        url += salting_charater
        newcode = short_code_generator(url)
    return newcode


def short_code_generator(url):
    hashinput = (url).encode()
    hashcode = sha256(hashinput).digest()
    encoded_short_code = base64.urlsafe_b64encode(hashcode)
    shortcode = encoded_short_code.decode()
    output = shortcode[:8]
    return output


@app.get(
    "/show",
    summary="Show all short codes",
    description="Returns all short codes and their original URLs if query parameter `show=all` is provided.",
)
def get_all_codes(show: str = Query(None), db: Session = Depends(get_db)):
    if show == "all":
        results = db.query(model.ShortURL.short_code, model.ShortURL.original_url).all()
        short_urls = [{"short_code": code, "org_url": url} for code, url in results]
        return short_urls
    return {"error": "Invalid query parameter"}


@app.get(
    "/admin",
    summary="Get access logs of a shortcode",
    description="Returns the 10 most recent timestamps for a given shortcode, along with its total visit count.",
)
def get_access_logs(
    passwrd: str = Query(None), code: str = Query(None), db: Session = Depends(get_db)
):
    key = os.getenv("SECRET_KEY")
    if passwrd != key:
        return {"error": "Unauthorized Access"}
    if not code:
        return {"error": "Please provide code"}
    results = (
        db.query(model.AccessLog.short_code, model.AccessLog.time_stamp)
        .filter(model.AccessLog.short_code == code)
        .order_by(model.AccessLog.time_stamp.desc())
        .limit(10)
        .all()
    )
    count = (
        db.query(model.ShortURL.visit_count)
        .filter(model.ShortURL.short_code == code)
        .first()
    )
    access_logs = [
        {"short_code": code, "timestamp": time_stamp} for code, time_stamp in results
    ]
    return {"visit_count": count[0] if count else 0, "access_logs": access_logs}


@app.get(
    "/{code}",
    summary="Get the original url of the short code",
    description="Returns a redirect to the original url",
)
def resolve(code: str, db: Session = Depends(get_db)):
    org_link = (
        db.query(model.ShortURL).filter(model.ShortURL.short_code == code).first()
    )
    if org_link:
        new_time_stamp = model.AccessLog(short_code=org_link.short_code)
        org_link.visit_count += 1
        org_link.access_log.append(new_time_stamp)
        db.commit()
        return RedirectResponse(url=org_link.original_url)
    raise HTTPException(status_code=404, detail="Short code not found")
