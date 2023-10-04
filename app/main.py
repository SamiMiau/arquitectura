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


# class Plantation(BaseModel):
#     name: str
#     # tomato = 'Tomato'
#     # sunflower = 'Sunflower'
#     # default = 'no name'

# class Collectable(BaseModel):
#     id: str | None = None
#     name: Plantation = Plantation(name = "no name")
#     buy_price: int
#     sell_price: int
#     quantity: int = 1
#     description: str = ""

# class Fertilizer(BaseModel):
#     id: str | None = None
#     name: str = "Fertilizer"
#     buy_price: int
#     sell_price: int
#     quantity: int = 1
#     description: str = "To grow stuff faster"


@app.get("/")
async def root():
    return {"Hello": "World"}
#----------------------------------------------------------------------USER CRUD---------------------------------------------
@app.post("/newuser/{user_name}")
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

@app.get("/getuser/{user_id}")
def get_user(user_id: str)-> User:
    try:
        user_id = ObjectId(user_id)
        return User(
            **mongodb_client.inventory.users.find_one({"_id": user_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Player not found")


#--------------------------------------------------------------------------Shop----------------------------------------------------------
@app.post("/newitem")
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

@app.get("/getitem/{item_id}")
def get_item(item_id: str)-> Item:
    try:
        item_id = ObjectId(item_id)
        return Item(
            **mongodb_client.inventory.shop.find_one({"_id": item_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.put("/updateitem/{item_id}")
def update_item(item_id: str, item: dict):
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
    
@app.delete("/deleteitem/{item_id}")
def delete_item(item_id: str):
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
    return item
#--------------------------------------------------------------------------Functionalities----------------------------------------------------------
#updates the items of a user, new_items is a list of Item
@app.put("/updateuseritems/{user_id}")
def update_user_items(user_id: str, new_items: list[dict]) -> User: 
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
@app.post("/{user_id}/{item_id}/{quantity}")
def add_item_to_user(user_id: str, item_id: str, quantity:int):
    user = get_user(user_id)
    old_items = user.items
    added=False
    for indice in range(len(old_items)):
        if old_items[indice].id == item_id: #si ya lo tiene, suma la cantidad
            old_items[indice].quantity=old_items[indice].quantity+quantity
            added=True
        old_items[indice]=old_items[indice].__dict__
    if not added: #si no lo tiene, lo agrega al final de la lista de items
        new_item= get_item(item_id)
        new_item.quantity=quantity
        new_item=new_item.__dict__
        old_items.append(new_item)
    user2 = update_user_items(user_id, old_items)
    return user2



@app.get("/buy/{item_id}/{quantity}/{user_id}", response_model=int)
async def buy(item_id: int, quantity: int, user_id: str) -> int:
    #sacar el costo de 1 item, calcular costo total compra
    total_cost = quantity*get_precio(item_id)
    #revisar si el usuario tiene disponible ese dinero
    if get_user_gold(user_id) < total_cost :
        #error no hay plata
        return 0
    else:
        return 1

# @app.post("/add/{item_id}/{quantity}/{user_id}")
# def add_item(item_id: int, quantity: int, user_id: str) -> int:
#     #buscar al usuario y si no existe mandar error
#     #si existe darle la cantidad pedida del item
#     #editar log para que entregue toda la info
#     logging.info(f"Item added: {quantity}")


# # @app.get("/teams")
# # def teams_all(id: list[int] = Query(None)):
# #     filters = dict()
# #     if id:
# #         filters['_id'] = {"$in": [ObjectId(_id) for _id in id]}

# #     teams = [Team(**team).dict()
# #              for team in mongodb_client.service_02.teams.find(filters)]

# #     return teams


# # @app.get("/teams/{team_id}")
# # def teams_get(team_id: str):
# #     team = Team(
# #         **mongodb_client.service_02.teams.find_one({"_id": ObjectId(team_id)})
# #     ).dict()

# #     return team


# # @app.delete("/teams/{team_id}")
# # def teams_delete(team_id: str):
# #     team = Team(
# #         **mongodb_client.service_02.teams.find_one({"_id": ObjectId(team_id)})
# #     ).dict()

# #     mongodb_client.service_02.teams.delete_one({"_id": ObjectId(team_id)})

# #     emit_events.send(team_id, "delete", team.dict())

# #     return team


# # @app.post("/teams")
# # def teams_create(team: Team):
# #     # Make it slow
# #     time.sleep(3)

# #     inserted_id = mongodb_client.service_02.teams.insert_one(
# #         team.dict()
# #     ).inserted_id

# #     new_team = Team(
# #         **mongodb_client.service_02.teams.find_one(
# #             {"_id": ObjectId(inserted_id)}
# #         )
# #     )

# #     logging.info(f"✨ New team created: {new_team}")
# #     emit_events.send(inserted_id, "create", new_team.dict())

# #     return new_team
