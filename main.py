from fastapi import FastAPI,HTTPException,Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel,HttpUrl
from hashlib import sha256
import base64
from database import engine,SessionLocal
import model

app=FastAPI()
origins=['http://localhost:8000']
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_headers=["*"],allow_methods=["*"],allow_credentials=True)
       
model.Base.metadata.create_all(bind=engine)
@app.get('/')
def hello():
    return "Hi, How you doing ?"
@app.get("/about")
def about():
    return {"about":"About Page"}

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class URLRequest(BaseModel):
    long_url:HttpUrl
@app.post('/shorten')
def shorten(request: URLRequest,db: Session=Depends(get_db)):
    url=str(request.long_url)
    exisiting_url=db.query(model.ShortURL).filter(model.ShortURL.original_url==url).first()
    if exisiting_url:
        return {"id":exisiting_url.uuid,"short_code":exisiting_url.short_code,"created_at":exisiting_url.created_at}
    shortcode=url_shortener(url)
    while True:
        newurl=model.ShortURL(original_url=url,short_code=shortcode)
        try:
            db.add(newurl)
            db.commit()
            db.refresh(newurl)
            break
        except IntegrityError:
            db.rollback()
            shortcode=url_shortener(url,salt=True,prevcode=shortcode)
            
    return{"id":newurl.uuid,"short_code":newurl.short_code,"created_at":newurl.created_at}

def url_shortener(url,salt=False,prevcode=None):
    if not salt:
        return short_code_generator(url)
    if prevcode is None:
        raise ValueError("prevcode must be provided when salt=True")
    salting_charater="x"
    newcode=prevcode
    while newcode==prevcode:
        url+=salting_charater
        newcode=short_code_generator(url)
    return newcode
    
def short_code_generator(url):
    hashinput=(url).encode()
    hashcode=sha256(hashinput).digest()
    encoded_short_code=base64.urlsafe_b64encode(hashcode)
    shortcode=encoded_short_code.decode()
    output=shortcode[:8]
    return output

@app.get('/{code}')
def resolve(code:str, db: Session=Depends(get_db)):
    link=db.query(model.ShortURL).filter(model.ShortURL.short_code==code).first()
    if link:
        link.visit_count+=1
        db.commit()
        return RedirectResponse(url=link.original_url)
    raise HTTPException(status_code=404,detail="Short code not found")
