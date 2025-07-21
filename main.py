# B1: import fastapi
from fastapi import Body, FastAPI, Path, Query
from typing import List, Optional, Set
from routers import users
import os
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper

# Also it will be will be import load_dotenv to connect to our .env file
from dotenv import load_dotenv

# this line is to connect to our base dir and connect to our .env file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Body
# Pydantic Models
from pydantic import BaseModel, Field, HttpUrl

# B2: Tạo 1 instance của class FastAPI
app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.environ["SQLALCHEMY_DATABASE_URI"])
app.include_router(users.router)


# Nested Models
# Ngoài các kiểu int, float, str còn có thể thêm kiểu list hay set
# Trên lý thuyết có thể lặp đi lặp lại các models lồng nhau như sau: class Image nằm trong class Item, class Item nằm trong class Offer
class Image(BaseModel):
    url: HttpUrl  # (Định dạng HttpUrl)
    name: str


class Item3(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: Set[str] = []  # (Định dạng Set)
    images: Optional[List[Image]] = None  # (Định dạng List)


class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item3]


@app.post("/offers/")
async def create_offer(offer: Offer = Body(..., embed=True)):
    return offer


# Field: validate data hoặc thêm metadata trong 1 class
class Item2(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=3
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = None


@app.put("/items_3/{item_id}")
async def update_item_3(item_id: int, item: Item2 = Body(..., embed=True)):
    results = {"item_id": item_id, "item": item}
    return results


# ==> Param description có metadata là title, với length không vượt quá 3 từ, param price không được nhỏ hơn 0 và có metadata là description
# Multiple Parameters
class Item1(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


@app.put("/items_1/{item_id}")
async def update_item_1(item_id: int, item: Item1, user: User, importance: int = Body(...)):  # Singular values in body
    results = {"item_id": item_id, "item": item, "user": user}
    return results


# Multiple body params and query
@app.put("/items_2/{item_id}")
async def update_item_2(*, item_id: int, item: Item1, user: User, importance: int = Body(..., gt=0),
                        q: Optional[str] = None):  # importance must > 0
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


# QUERY PARAMETERS AND STRING VALIDATIONS
# Number validations: greater than or equal
@app.get("/items_8/{item_id}")
# với param ge = 100 của class Path, item_id bắt buộc phải là số lớn hơn hoặc bằng 100
# Number validations không chỉ hỗ trợ type integer mà còn hỗ trợ type float
# Giá trị tham số gt: >, ge: >=, lt: <, le: <=
async def read_items_3(*, item_id: int = Path(..., title="The ID of the item to get", ge=100),
                       q: str
                       ):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Path parameters and numeric validations
# Query parameters có class Query để khai báo metadata và validations, path parameters có class Pass với cơ chế tương tự
# Thêm title metadata cho path param item_id
@app.get("/items_7/{item_id}")
async def read_items_2(item_id: int = Path(..., title="The ID of the item to get"),
                       q: Optional[str] = Query(None, alias="item-query")
                       ):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Query parameter list / multiple values
@app.get("/items_6/")
async def read_items_1(q: Optional[List[str]] = Query(None)):
    query_items = {"q": q}
    return query_items


# ==> q là 1 List có thể chứa nhiều giá trị
@app.get("/items_5/")
async def read_items(q: Optional[str] = Query(None, max_length=5)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# ==> Câu lệnh q: Optional[str] = Query(None) cũng tương tự q: Optional[str] = None nhưng Query cung cấp các param khác như max_length, min_length, regex,...
# Bạn có thể tăng giới hạn ký tự thành 250 (Mặc định của max_length là 50)    
# Request body
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


# Request body + path parameters
# FastAPI hỗ trợ khai báo tham số URL và request body cùng lúc, framework sẽ biết tham số nào truyền từ đường dẫn và tham số nào lấy từ request    
@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}


@app.post("/items/")
async def create_item(item: Item):  # Khai báo dưới dạng parameter
    # Use model
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


# Dựa trên việc import Pydantic module, FastAPI hỗ trợ:
# - Đọc request body dưới dạng json
# - Chuyển đổi định dạng biến
# - Validate dữ liệu
# - Khai báo format mặc định của request body, class item trên là 1 ví dụ
# - Gen JSON Schema cho model của bạn
# - Schema sẽ được gen thành UI của OpenAI doc    
# 4) Query paremeter
# B3: Tạo đường dẫn, bắt đầu từ /
# B4: Khai báo phương thức HTTP: post, get, put, delete hay (*) option, head, patch, trace
# B5: Khai báo hàm
# Query parameters
# Nếu truyền dưới dạng key-value JSON thì ở trong FastAPI có hỗ trợ với tên gọi "query" parameters
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]  # pair format: key-value


@app.get("/items_1/")
async def read_item_1(skip: int = 0, limit: int = 10):
    # B6: Trả về content với format dict, list, str, int,... 
    return fake_items_db[skip: skip + limit]  # trả về dữ liệu từ skip đến skip + limit


# 8) Required query parameters
@app.get("/items_4/{item_id}")
async def read_user_item2(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item


# ==> Nếu chỉ truyền vào giá trị của item_id còn giá trị của needy bỏ trống thì sẽ sinh ra lỗi
# 7) Multiple path and query parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    item = {"item_id": item_id, "owner_id": user_id}
    return item


# 6) Query parameter type conversion
@app.get("/items_3/{item_id}")
async def read_item_3(item_id: str,
                      short: bool = False):  # param short với định dạng boolean có giá trị mặc định là False
    item = {"item_id": item_id}
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# ==> Test http://127.0.0.1:8000/items/foo?short=1
# or
# http://127.0.0.1:8000/items/foo?short=False
# 5) Optional parameters
@app.get("/items_2/{item_id}")
async def read_item_2(item_id: str, q: Optional[str] = None):
    # param item_id: format string
    # param q: format string, default value: None, Optional: help you find error that happen
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


# 1) Thứ tự /users/me trước
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


# Rồi đến /users/{user_id} sau
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


# ==> Nếu để /users/{user_id} trước thì user_id sẽ nhận giá trị me
# 2) Path in path: hỗ trợ khai báo đường dẫn trong đường dẫn API nhờ vào việc based starlette
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# 3) Path parameters (with types: read_item(item_id: int))
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/")
async def root():
    # variables and data types
    x = 5
    name = "Alice"
    price = 19.99
    is_active = True
    # conditional statements
    if x > 10:
        print("Large")
    elif x == 10:
        print("Equal")
    else:
        print("Small")
    # for loop
    for i in range(5):
        print(i)
    # while loop
    count = 0
    while count < 5:
        print(count)
        count += 1
    # Lists
    fruits = ["apple", "banana", "cherry"]
    print(fruits)
    fruits.append("orange")
    # Dictionaries
    person = {"name": "Alice", "age": 30}
    print(person["name"])
    return {"message": "Hello World"}
