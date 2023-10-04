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
from .events import Receive


app = FastAPI()
mongodb_client = MongoClient("inventory_mongodb", 27017)

# emit_events = Emit()
# threading.Thread(target=Receive).start()

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
#----------------------------------------------------------------------USER CRUD---------------------------------------------
@app.post("/newuser/{user_name}", response_model=User)
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

    #logging.info(f"✨ New team created: {new_team}")
    #emit_events.send(inserted_id, "create", new_team.dict())
    return new_user

@app.get("/getuser/{user_id}", response_model=User)
def get_user(user_id: str)-> User:
    try:
        user_id = ObjectId(user_id)
        return User(
            **mongodb_client.inventory.users.find_one({"_id": user_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Player not found")


#--------------------------------------------------------------------------Shop----------------------------------------------------------
@app.post("/newitem", response_model=Item)
def add_item(item: Item) -> Item:
    inserted_id = mongodb_client.inventory.shop.insert_one(
        item.dict()
    ).inserted_id
    
    # mongodb_client.inventory.shop.update_one(
    #         {'_id': inserted_id}, {'$set':{'id':inserted_id}})
    
    new_item = Item(
        **mongodb_client.inventory.shop.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )
    #logging.info(f"✨ New team created: {new_team}")
    #emit_events.send(inserted_id, "create", new_team.dict())
    return new_item

@app.get("/getitem/{item_id}", response_model=Item)
def get_item(item_id: str)-> Item:
    try:
        item_id = ObjectId(item_id)
        return Item(
            **mongodb_client.inventory.shop.find_one({"_id": item_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.put("/updateitem/{item_id}", response_model=Item)
def update_item(item_id: str, item: dict)-> Item:
    try:
        item_id = ObjectId(item_id)
        mongodb_client.inventory.shop.update_one(
            {'_id': item_id}, {"$set": item})

        #emit_events.send(player_id, "update", player)

        return Item(
            **mongodb_client.inventory.shop.find_one({"_id": item_id})
        )

    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.delete("/deleteitem/{item_id}", response_model=str)
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

    #emit_events.send(player_id, "delete", player.dict())
    return 'ok'
#--------------------------------------------------------------------------Functionalities----------------------------------------------------------
#updates the items of a user, new_items is a list of Item
@app.put("/updateuseritems/{user_id}", response_model=User)
def update_user_items(user_id: str, new_items: list[dict]) -> User: 
    print(new_items)
    try:
        user_id = ObjectId(user_id)
        mongodb_client.inventory.users.update_one(
            {'_id': user_id}, {'$set':{'items':new_items}})

        #emit_events.send(player_id, "update", player)

        return User(
            **mongodb_client.inventory.users.find_one({"_id": user_id})
        )

    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="User not found")
    
#adds a specific quantity of one item to one user
@app.post("/{user_id}/{item_id}/{quantity}", response_model=User)
def add_item_to_user(user_id: str, item_id: str, quantity:int, action:int) -> User:
    user = get_user(user_id)
    old_items = user.items
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    print(old_items)
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
        else:
            old_items[indice]=old_items[indice].__dict__
        
    else: #si no lo tiene, lo agrega al final de la lista de items
        new_item = get_item(item_id)
        new_item.quantity=quantity
        new_item = new_item.__dict__
        old_items.append(new_item)
    new=[]
    for x in old_items:
        x=x.__dict__
        new.append(x)
    user2 = update_user_items(user_id, new)
    return user2



@app.post("/buy/{user_id}/{item_id}/{quantity}", response_model=int)
async def buy(user_id: str, item_id: str, quantity: int) -> int:
    #sacar el costo de 1 item, calcular costo total compra
    total_cost = quantity*get_item(item_id).buy_price
    #revisar si el usuario tiene disponible ese dinero
    if get_user(user_id).gold < total_cost :
        #error no hay plata
        return 0
    else:
        #agregar item
        user = add_item_to_user(user_id, item_id, quantity,1)
        #quitar dinero
        new_gold = user.gold - total_cost
        user_id = ObjectId(user_id)
        mongodb_client.inventory.users.update_one(
            {'_id': user_id}, {"$set": {'gold':new_gold}})
        return 1

@app.post("/sell/{user_id}/{item_id}/{quantity}", response_model=int)
async def sell(user_id: str, item_id: str, quantity: int) -> int:
    #revisar que tenga al menos quantity del item que quiere vender
    user = get_user(user_id)
    for item in user.items:
        if item.id == item_id:
            if quantity > item.quantity: #no hay suficiente cantidad
                print('holi')
                return 0
            else:
                #delete items from user's inventory
                user = add_item_to_user(user_id, item_id, quantity,-1)
                #add gold
                price = quantity*get_item(item_id).sell_price
                new_gold = user.gold + price
                user_id = ObjectId(user_id)
                mongodb_client.inventory.users.update_one(
                    {'_id': user_id}, {"$set": {'gold':new_gold}})
                return 1
    return 0
