from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel,Field
import uuid
from typing import List, Annotated

class Item(BaseModel):
    id:uuid.UUID =Field(default_factory=uuid.uuid4)
    name:str
    price:int


class ParamsALL(BaseModel):
    model_config={"extra":"forbid"}
    limit : int =Field(100, gt=0,lt=1000)
    offset : int =Field(0,ge=0)
app=FastAPI()
#fake db for testing
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# creating crud 
items:List[Item]=[]

@app.get("/")
async def home_page():
    return "welcome to fastAPI project"


@app.post("/create")
async def create_item(item:Item):
    new_item = Item(id=uuid.uuid4(),name=item.name, price=item.price)
    items.append(new_item)
    return ("new Item creeated",new_item)


@app.get("/items",response_model=List[Item])
async def get_all_items():
    return items

@app.get("/items/{item_id}",response_model=Item)
async def get_item_by_id(item_id:uuid.UUID):
    for item in items:
        if item.id ==item_id:
            return item
    
    raise HTTPException(status_code=404, detail="Item for id not found")

@app.get("/qparam")
async def read_item(s:int=0, limit:int|None = None):
    return fake_items_db[s]


@app.get("/newparams/")
async def new_params(filter_query:Annotated[ParamsALL,Query()]):
    return filter_query

@app.put("/items/{item_id}", response_model=Item)
async def update_items(item_id:uuid.UUID,updated_item:Item):
    for index, item in enumerate(items):
        if item.id == item_id:
            items[index] = updated_item
            return ("items are updated",updated_item)
    raise HTTPException(status_code=404, detail="Item not available")


@app.delete("/items/{item_id}")
async def delete_item(item_id:uuid.UUID):
    for index, item in enumerate(items):
        if item.id ==item_id :
            deleted=items.pop(index)
            return ("The item was deleted", deleted)
    raise HTTPException(status_code=404, detail="not found")
