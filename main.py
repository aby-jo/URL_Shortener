from fastapi import FastAPI
app=FastAPI()
@app.get('/')
def hello():
    return "Hello"
@app.get("/about")
def about():
    return {"about":"About Page"}