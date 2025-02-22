from fastapi import FastAPI, Query, Path, HTTPException, status, Body, Request, Form,UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from cars_db import collection
import random
import os
import shutil

templates = Jinja2Templates(directory="templates")


class Car(BaseModel):
    image: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = Field(..., ge=1970, le=2026)
    price: Optional[float] = None
    engine: Optional[str] = "V4"
    autonomous: Optional[bool] = None
    sold: Optional[List[str]] = None

static_folder = 'static'
image_folder = os.path.join(static_folder,'images')
os.makedirs(image_folder,exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root(req: Request, response_class=RedirectResponse):
    # return templates.TemplateResponse("home.html", {"request": req, "title":"FastApi- Home"})
    return RedirectResponse(url="/cars", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/cars", response_class=HTMLResponse)
def get_cars(req: Request, number: Optional[str] = Query("10", max_length=3)):
    res = []
    cars = list(collection.find({}, {"_id": 0}).sort("car_id",-1))
    for car in cars[: int(number)]:
        res.append({str(car["car_id"]): car})
    return templates.TemplateResponse("index.html", {"request": req, "cars": res,"title":"CarList"})


@app.post("/search", response_class=RedirectResponse)
def search(id: str = Form(...)):
    return RedirectResponse("/cars/" + id, status_code=302)

@app.get("/create", response_class=HTMLResponse)
def create_car(req:Request):
    return templates.TemplateResponse("create.html",{"request":req})

@app.get("/cars/{id}", response_class=HTMLResponse)
def get_car_by_id(req: Request, id: int = Path(..., ge=1, le=1000)):
    car = collection.find_one({"car_id": id}, {"_id": 0})
    s_car = []
    if car :
        s_car.append({id:car})
    res = templates.TemplateResponse("index.html", {"request": req, "cars": s_car,"title":"car"})
    if not car:
        res.status_code = 404
    return res



@app.post("/cars", response_class=RedirectResponse)
async def add_cars(req:Request,
    car_image: UploadFile = Form(...),
    make: Optional[str] = Form(...),
    model: Optional[str] = Form(...),
    year: Optional[int] = Form(...),
    price: Optional[float] = Form(...),
    engine: Optional[str] = Form(...),
    autonomous: Optional[bool] = Form(...),
    sold: List[str] = Form([]) 
    ):

    image_filename = os.path.join(image_folder, car_image.filename)
    with open(image_filename, "wb") as buffer:
        shutil.copyfileobj(car_image.file, buffer)
    
    # generate unique id
    last_car = collection.find_one(sort=[("car_id",-1)])
    new_car_id = last_car["car_id"] + 1 if last_car else 1

    new_car = {
        "car_id": new_car_id,
        "image": car_image.filename,
        "make": make,
        "model": model,
        "year": year,
        "price": price,
        "engine": engine,
        "autonomous": autonomous,
        "sold": sold or [],
    }

    if not new_car:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No cars to be added"
        )
    
    collection.insert_one(new_car)
    
    return RedirectResponse("/cars",status_code=302)

@app.post("/edit/{car_id}",response_class=HTMLResponse)
def edit_car(req:Request,
        car_image: UploadFile = Form(...),
        make: Optional[str] = Form(...),
        model: Optional[str] = Form(...),
        year: Optional[int] = Form(...),
        price: Optional[float] = Form(...),
        engine: Optional[str] = Form(...),
        autonomous: Optional[bool] = Form(...),
        sold: List[str] = Form([]),car_id :int = Path(...)
        ):
    
    exist = collection.find({"car_id":car_id})
    if not exist:
        return templates.TemplateResponse("index.html",{"request":req,"title":"Edit Car","cars":car},status_code=status.HTTP_404_NOT_FOUND)        

    update_data = {}

    if car_image.filename:
        image_filename = os.path.join(image_folder, car_image.filename)
        with open(image_filename, "wb") as buffer:
            shutil.copyfileobj(car_image.file, buffer)
        update_data["image"] = car_image.filename
    if make:
        update_data["make"] = make
    if model:
        update_data["model"] = model
    if year:
        update_data["year"] = year
    if price:
        update_data["price"] = price
    if engine:
        update_data["engine"] = engine
    if autonomous is not None:
        update_data["autonomous"] = autonomous
    if sold is not None:
        update_data["sold"] = sold
    
    updated_car = collection.find_one_and_update({"car_id":car_id},{"$set":update_data},return_document=True)

    if not updated_car:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Car Updated Failed"
        )
    
    return RedirectResponse("/cars",status_code=302)


@app.get("/edit",response_class=HTMLResponse)
def edit_car(req:Request,id:int = Query(...)):
    car = collection.find_one({"car_id":id})
    if not car:
        return templates.TemplateResponse("index.html",{"request":req,"title":"Edit Car","cars":car},status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse("edit.html",{"request":req,"car":car,"title":"Edit Car"})

@app.put("/cars/{id}", response_model=Dict[str, Car])
def update_car(id: int, car: Car = Body(...)):
    stored = cars.get(id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Car is not found by this id"
        )
    stored = Car(**stored)
    new = car.dict(exclude_unset=True)
    new = stored.copy(update=new)
    cars[id] = jsonable_encoder(new)
    res = {}
    res[str(id)] = cars[id]
    return res

@app.post("/delete/{id}",response_class=RedirectResponse)
def delete_car(req:Request,id: int = Path(...)):
    res = collection.delete_one({"car_id":id})
    if res.deleted_count == 0:
        return templates.TemplateResponse("index.html",{"request":req,"title":"Edit Car","cars":[]},status_code=status.HTTP_404_NOT_FOUND)
    return RedirectResponse(url="/cars",status_code=303)