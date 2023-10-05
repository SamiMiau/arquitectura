from enum import Enum

import time
import logging
import threading
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, Query
from fastapi import HTTPException
from pydantic import BaseModel

from .events import Emit
#from .events import Receive


app = FastAPI()
mongodb_client = MongoClient("inventory_mongodb", 27017)

emit_events = Emit()
#threading.Thread(target=Receive).start()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

    
class Item(BaseModel):
    id: str | None = None
    name: str = ""
    buy_price: int | None = None
    sell_price: int | None = None
    quantity: int | None = 1
    description: str = "stuff!!"
    class Config:
        schema_extra = {
            "example": {
                "id": "53",
                "name": "Strawberry seeds",
                "buy_price": 500,
                "sell_price": 5,
                "quantity": 4,
                "description":  "Plant it on your farm!"
            }
        }
    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)   

class User(BaseModel):
    id: str | None = None
    name: str = "Player"
    gold: int = 0
    items: list[Item]=[]
    class Config:
        schema_extra = {
            "example": {
                "id": "10",
                "name": "Facundo"
            }
        }
    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)        


@app.get("/")
async def root():
    return {"Hello": "World"}
#----------------------------------------------------------------------USER---------------------------------------------
@app.post("/newuser/{user_name}", response_model=User, tags=["user"])
def add_user(user_name: str) -> User:
    user = User(name=user_name, gold=1000)
    inserted_id = mongodb_client.inventory.users.insert_one(
        user.dict()
    ).inserted_id

    new_user = User(
        **mongodb_client.inventory.users.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )
    logging.info(f"✨ New user created: {user}")
    emit_events.send(inserted_id, "create", new_user.dict())
    return new_user

@app.get("/getuser/{user_id}", response_model=User, tags=["user"])
def get_user(user_id: str)-> User:
    try:
        user_id = ObjectId(user_id)
        return User(
            **mongodb_client.inventory.users.find_one({"_id": user_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/inventory", response_model=list[Item], tags=["user inventory"])
def get_all_inventory(user_id: str)-> list[Item]:
    user = get_user(user_id)
    items = user.items
    return items
#--------------------------------------------------------------------------Shop----------------------------------------------------------
@app.post("/newitem", response_model=Item, tags=["shop"])
def add_item(item: Item) -> Item:
    inserted_id = mongodb_client.inventory.shop.insert_one(
        item.dict()
    ).inserted_id
    
    new_item = Item(
        **mongodb_client.inventory.shop.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )
    logging.info(f"✨ New item created on the shop: {new_item}")
    emit_events.send(inserted_id, "create", new_item.dict())
    return new_item

@app.get("/market", response_model=list[Item], tags=["shop"])
def get_all_items(id: list[int] = Query(None))-> list[Item]:
    filters = dict()
    if id:
        filters['_id'] = {"$in": [ObjectId(_id) for _id in id]}

    shop_items = [Item(**item).dict() for item in mongodb_client.inventory.shop.find(filters)]

    return shop_items
    

@app.get("/getitem/{item_id}", response_model=Item, tags=["items"])
def get_item(item_id: str)-> Item:
    try:
        item_id = ObjectId(item_id)
        return Item(
            **mongodb_client.inventory.shop.find_one({"_id": item_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.put("/updateitem/{item_id}", response_model=Item, tags=["items"])
def update_item(item_id: str, item: dict)-> Item:
    try:
        item_id = ObjectId(item_id)
        item = mongodb_client.inventory.shop.update_one(
            {'_id': item_id}, {"$set": item})
        
        logging.info(f"✨ Item updated from shop: {item}")
        emit_events.send(item_id, "update", item)

        return Item(
            **mongodb_client.inventory.shop.find_one({"_id": item_id})
        )

    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.delete("/deleteitem/{item_id}", response_model=str, tags=["items"])
def delete_item(item_id: str) -> str:
    try:
        item_id = ObjectId(item_id)
        item = Item(
            **mongodb_client.inventory.shop.find_one({"_id": item_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")

    mongodb_client.inventory.shop.delete_one(
        {"_id": ObjectId(item_id)}
    )

    logging.info(f"✨ Item deleted from shop: {item}")
    emit_events.send(item_id, "delete", item.dict())
    return 'ok'
#--------------------------------------------------------------------------Functionalities----------------------------------------------------------
#updates the items of a user, new_items is a list of Item
@app.put("/updateuseritems/{user_id}", response_model=User, tags=["user"])
def update_user_items(user_id: str, new_items: list[dict]) -> User: 
    print(new_items)
    try:
        user_id = ObjectId(user_id)
        mongodb_client.inventory.users.update_one(
            {'_id': user_id}, {'$set':{'items':new_items}})
        user = User(
            **mongodb_client.inventory.users.find_one({"_id": user_id})
        )

        logging.info(f"✨ Inventory items updated for user: {user}")
        emit_events.send(user_id, "update", user.dict())

        return user

    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="User not found")
    
#adds a specific quantity of one item to one user
@app.post("/{user_id}/{item_id}/{quantity}", response_model=User, tags=["user"])
def add_item_to_user(user_id: str, item_id: str, quantity:int, action:int) -> User:
    if quantity<=0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
    else:
        user = get_user(user_id)
        old_items = user.items
        found = False
        for indice in range(len(old_items)):
            if old_items[indice].id == item_id: #si ya lo tiene, suma la cantidad
                found=True
                break
        if found:
            old_items[indice].quantity = old_items[indice].quantity + quantity*action
                #old_items[indice]=old_items[indice].__dict__
            if old_items[indice].quantity == 0:
                old_items.pop(indice)
            
        else: #si no lo tiene, lo agrega al final de la lista de items
            new_item = get_item(item_id)
            new_item.quantity=quantity
            old_items.append(new_item)

        new=[] #to transform into dictionary
        for x in old_items:
            x=x.dict()
            new.append(x)
        user2 = update_user_items(user_id, new)

        logging.info(f"✨ {quantity} of item: {item_id} added to inventory for user: {user2}")
        emit_events.send(user_id, "update", user2.dict())
        return user2

@app.post("/buy/{user_id}/{item_id}/{quantity}", response_model=int, tags=["user actions"])
async def buy(user_id: str, item_id: str, quantity: int) -> int:
    if quantity<=0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
    else:
        total_cost = quantity*get_item(item_id).buy_price
        if get_user(user_id).gold < total_cost :
            #error no hay plata
            return 0
        else:
            payload = {'user_id':user_id, 'item_id': item_id, 'quantity': quantity, 'gold_spent': total_cost}
            user = add_item_to_user(user_id, item_id, quantity,1)
            new_gold = user.gold - total_cost
            user_id = ObjectId(user_id)
            mongodb_client.inventory.users.update_one(
                {'_id': user_id}, {"$set": {'gold':new_gold}})
            
            logging.info(f"✨ {quantity} of item: {item_id} purchased by user: {user}")
            emit_events.send(user_id, "purchase", payload)
            return 1

@app.post("/sell/{user_id}/{item_id}/{quantity}", response_model=int, tags=["user actions"])
async def sell(user_id: str, item_id: str, quantity: int) -> int:
    if quantity<=0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
    else:
        user = get_user(user_id)
        for item in user.items:
            if item.id == item_id:
                if quantity > item.quantity: 
                    return 0
                else:
                    user = add_item_to_user(user_id, item_id, quantity,-1)
                    price = quantity*get_item(item_id).sell_price
                    payload = {'user_id':user_id, 'item_id': item_id, 'quantity': quantity, 'gold_earned': price}
                    new_gold = user.gold + price
                    user_id = ObjectId(user_id)
                    mongodb_client.inventory.users.update_one(
                        {'_id': user_id}, {"$set": {'gold':new_gold}})
                    logging.info(f"✨ {quantity} of Item: {item_id} sold by user: {user}")
                    emit_events.send(user_id, "purchase", payload)
                    return 1
        return 0
