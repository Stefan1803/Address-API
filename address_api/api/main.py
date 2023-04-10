# This part is added to be able to run the app from command prompt.
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Response, Depends, HTTPException
from model.api.model import UpdateAddressSchema, CreateAddressSchema
from model.database.model import Address, Base
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from math import sin, cos, sqrt, atan2, radians
from fastapi.responses import HTMLResponse

import logging
import uvicorn
import pandas as pd


# Creates logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('address_api_logger.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Create all tables stored in metadata
Base.metadata.create_all(bind=engine)

# Tags for endpoints - assigned in the definitions and visible in the swagger
tags_metadata = [
    {"name": "GET", "description": "This endpoints are used to display data"},
    {"name": "UPDATE", "description": "This endpoints are used to update data"},
    {"name": "DELETE", "description": "This endpoints are used to delete data"},
    {"name": "CREATE", "description": "This endpoints are used to add new data"}
]

# Description visible in the swagger
api_description = """
This is API for managing addresses.

## Access

Endpoints can be access by adding /**endpoint_name** after the server IP.

## Endpoints types

* **GET** - You can get data directly from the endpoint by adding
**/endpoint_name?parameter1=value1&parameter2=value2** , depending of the number of parameters.
* **POST** - Requires request body, schemas with examples are present in the bottom of the page.
"""

app = FastAPI(
    title="Address API Eastvantage",
    description=api_description,
    version="0.0.1",
    terms_of_service="https://eastvantage.com/company/",
    contact={
        "name": "Admin",
        "email": "stefan.toncev123@gmail.com",
    },
    license_info={
        "name": "Licence",
        "url": "https://eastvantage.com/company/",
    },
    openapi_tags=tags_metadata,
)


@app.get("/", tags=["GET"])
def root():
    return HTMLResponse(content=
                        """<html>
                                <head>
                                    <title>Address API Eastvantage</title>
                                </head>
                                <body>
                                    <h1> Welcome to Address API </h1>
                                </body>
                            </html>
                        """)


@app.get("/get_all_addresses", tags=["GET"])
def get_all_addresses(db: Session = Depends(get_db)):
    return db.query(Address).all()


@app.post("/create_address", tags=["CREATE"])
def create_address(object_body: CreateAddressSchema, response: Response, db: Session = Depends(get_db)):
    address_model = Address()
    address_model.latitude = object_body.latitude
    address_model.longitude = object_body.longitude
    address_model.name = object_body.name
    address_model.description = object_body.description
    try:
        db.add(address_model)
        db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Record couldn't be added, no response from database."
        )

    return {"Success": "Address created!"}


@app.put("/update_address", tags=["UPDATE"])
def update_address(object_body: UpdateAddressSchema, db: Session = Depends(get_db)):
    address_model = db.query(Address).filter(Address.id == object_body.id).first()

    if address_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {object_body.id} : Does not exist"
        )

    address_model.latitude = object_body.new_latitude if object_body.new_latitude else address_model.latitude
    address_model.longitude = object_body.new_longitude if object_body.new_longitude else address_model.longitude
    address_model.name = object_body.new_name if object_body.new_name else address_model.name
    address_model.description = object_body.new_description if object_body.new_description else address_model.description
    db.add(address_model)
    db.commit()

    return {"Success": f"Address updated!"}


@app.delete("/delete_address/{id}", tags=["DELETE"])
def delete_address(id: int, db: Session = Depends(get_db)):
    book_model = db.query(Address).filter(Address.id == id).first()

    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {id} : Does not exist"
        )

    db.query(Address).filter(Address.id == id).delete()
    db.commit()
    return {"Success": "Address deleted!"}


@app.get("/get_address", tags=["GET"])
def get_address(latitude: float, longitude: float, distance: float, db: Session = Depends(get_db)):
    '''
    Provides all addresses in range of given distance from the point of given latitude and longitude
    '''

    if latitude > 90 or latitude < -90:
        raise HTTPException(
            status_code=422,
            detail="Latitude must be between -90 and 90"
        )
    if longitude < -180 or longitude > 180:
        raise HTTPException(
            status_code=422,
            detail="Longitude must be between -180 and 180"
        )

    try:
        data = db.query(Address).all()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="No response from database."
        )

    # Using Pandas DataFrame as not all databases have built-in math functions like sin,cos
    # This is safer approach to make sure calculations will be correct
    # If data is too big, column distance should be added and calculated in the database, as now all data is in memory
    # Example:
    # SELECT * FROM(
    #   SELECT *,(((acos(sin((@latitude*pi()/180)) * sin((latitude*pi()/180))+cos((@latitude*pi()/180)) *
    #   cos((latitude*pi()/180)) * cos(((@longitude - longitude)*pi()/180))))*180/pi())*60*1.1515*1.609344)
    #   as distance FROM addresses) t
    #   WHERE distance <= @distance
    # @latitude and @longitude are the latitude and longitude of the given point.
    # latitude and longitude are the columns of the table.

    df = pd.DataFrame([t.__dict__ for t in data])
    df = df.drop(columns=['_sa_instance_state'])

    def calculate_distance(row):
        # This approach below is using haversine formula - https://en.wikipedia.org/wiki/Haversine_formula

        r = 6373.0  # Approximate radius of earth in km

        # Converting to radians, as in Python, all the trigonometry functions use radians, not degrees.

        a = sin((radians(row['latitude']) - radians(latitude)) / 2) ** 2 + cos(radians(row['latitude'])) * \
            cos(radians(latitude)) * sin((radians(row['longitude']) - radians(longitude)) / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        d = r * c
        return d

    df['distance'] = df.apply(calculate_distance, axis=1)
    df = df[df['distance'] <= distance]
    df = df.drop(columns=['distance'])

    return df.to_dict(orient='records')


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
