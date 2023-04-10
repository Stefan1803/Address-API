from typing import Optional
from pydantic import BaseModel, Field


class GetAddressesSchema(BaseModel):
    latitude: float = Field(..., gt=-90, lt=90)
    longitude: float = Field(..., gt=-180, lt=180)
    distance: float = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "latitude": 2.3123,
                "longitude": 1.3145,
                "distance": 3.211
            }
        }


class CreateAddressSchema(BaseModel):
    latitude: float = Field(..., gt=-90, lt=90)
    longitude: float = Field(..., gt=-180, lt=180)
    name: str = Field(...)
    description: Optional[str] = Field(default=None)

    class Config:
        schema_extra = {
            "example": {
                "latitude": 2.3123,
                "longitude": 1.3145,
                "name": "Super cool place",
                "description": "This place is super cool"
            }
        }


class UpdateAddressSchema(BaseModel):
    id: int = Field(...)
    new_latitude: Optional[float] = Field(default=None, gt=-90, lt=90)
    new_longitude: Optional[float] = Field(default=None, gt=-180, lt=180)
    new_name: Optional[str] = Field(default=None)
    new_description: Optional[str] = Field(default=None)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "new_latitude": 2.3123,
                "new_longitude": 1.3145,
                "new_name": "Not that cool place",
                "new_description": "This place used to be cool, but now it's not :("
            }
        }
