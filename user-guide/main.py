from enum import Enum
from datetime import datetime, time, timedelta
from typing import Set, Union, List
from uuid import UUID
from fastapi import FastAPI, Query, Path, Body, status, Form, HTTPException
from pydantic import BaseModel, Field, HttpUrl, EmailStr


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Union[str, None] = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: Union[str, None] = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: Union[float, None] = None
    tags: Set[str] = set()
    image: Union[Image, None] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


class Offer(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    items: List[Item]


class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


items = {"foo": "foo is not fool"}


app = FastAPI()

# PATH PARAMETER


@app.post("/login/", tags=["users"])
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


# Don't do this in production!
@app.post(
    "/user/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
async def create_user(user: UserIn):
    return user


@app.get("/")
async def home():
    return {"message": "Hello World!"}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}


@app.get("/items/{item_id}", response_model=Item, tags=["items"])
async def read_item(
    *,
    item_id: UUID = Path(title="The ID of the item to get"),
    q: Union[str, None] = Query(
        default=None,
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        regex="^fixedquery$",
        deprecated=True,
    ),
    short: bool = False,
    # start_datetime: Union[datetime, None] = Body(default=None),
    # end_datetime: Union[datetime, None] = Body(default=None),
    # repeat_at: Union[time, None] = Body(default=None),
    # process_after: Union[timedelta, None] = Body(default=None),
):
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    item = {
        "item_id": item_id,
    }
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/users/{user_id}/items/{item_id}", tags=["items"])
async def read_user_item(
    user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# QUERY PARAMETER

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/", tags=["items"])
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


@app.post("/items/", tags=["items"])
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}", tags=["items"])
async def update_item(item_id: int, item: Item, user: User, importance: int = Body()):

    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


@app.post("/offers/", tags=["offers"])
async def create_offer(offer: Offer):
    return offer


@app.post("/images/multiple/", tags=["images"])
async def create_multiple_images(*, images: List[Image]):
    return images
