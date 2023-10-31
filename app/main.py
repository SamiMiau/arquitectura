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
from fastapi.middleware.cors import CORSMiddleware

from .events import Emit
#from .events import Receive


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """
    Creates a new user with the given name \n
    Returns the user created
    """
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
    """
    Finds the user with the given id \n
    Returns the user
    """
    try:
        user_id = ObjectId(user_id)
        return User(
            **mongodb_client.inventory.users.find_one({"_id": user_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="User not found")
@app.get("/getuserid/{user_name}", response_model=str, tags=["user"])
def get_userid(user_name: str)-> str:
    """
    Finds the user with the given name \n
    Returns the user's id
    """
    try:
        return User(
            **mongodb_client.inventory.users.find_one({"name": user_name})
        ).id
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="User not found")
    
@app.get("/inventory", response_model=list[Item], tags=["user inventory"])
def get_all_inventory(user_id: str)-> list[Item]:
    """
    Fetches all of the items a user has in their inventory \n
    Returns a list of items
    """
    user = get_user(user_id)
    items = user.items
    return items
#--------------------------------------------------------------------------Shop----------------------------------------------------------
@app.post("/newitem", response_model=Item, tags=["shop"])
def add_item(item: Item) -> Item:
    """
    Creates a new item \n
    Returns the item created
    """
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
    """
    Fetches all of the items that exist (for now we assume all of the items are on the shop) \n
    Returns a list of items
    """
    filters = dict()
    if id:
        filters['_id'] = {"$in": [ObjectId(_id) for _id in id]}

    shop_items = [Item(**item).dict() for item in mongodb_client.inventory.shop.find(filters)]

    return shop_items
    

@app.get("/getitem/{item_name}", response_model=Item, tags=["items"])
def get_item(item_name: str)-> Item:
    """
    Fetches an item with the given name \n
    Returns the item
    """
    try:        
        return Item(
            **mongodb_client.inventory.shop.find_one({"name": item_name})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.put("/updateitem/{item_name}", response_model=Item, tags=["items"])
def update_item(item_name: str, item: dict)-> Item:
    """
    Updates the item that corresponds with the given name and all of it's parameters  \n
    Returns the item
    """
    try:      
        it = get_item(item_name)
        print(it)
        item_new = mongodb_client.inventory.shop.update_one(
            {'_id': ObjectId(it.id)}, {"$set": item})
        
        logging.info(f"✨ Item updated from shop: {item}")
        emit_events.send(item_name, "update", item)

        return get_item(item["name"])
            #**mongodb_client.inventory.shop.find_one({"_id": ObjectId(it.id)})
        

    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.delete("/deleteitem/{item_name}", response_model=str, tags=["items"])
def delete_item(item_name: str) -> str:
    """
    Deletes an item with the given name from the shop (it doesn't delete it from players inventory. This could lead to errors and will later be fixed) \n
    Returns ok if the delete was successful
    """
    try:
        item = Item(
            **mongodb_client.inventory.shop.find_one({"name": item_name})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Item not found")

    mongodb_client.inventory.shop.delete_one(
        {"_id": ObjectId(item.id)}
    )

    logging.info(f"✨ Item deleted from shop: {item}")
    emit_events.send(item_name, "delete", item.dict())
    return 'ok'
#--------------------------------------------------------------------------Functionalities----------------------------------------------------------
#updates the items of a user, new_items is a list of Item
@app.put("/updateuseritems/{user_id}", response_model=User, tags=["user"])
def update_user_items(user_id: str, new_items: list[dict]) -> User: 
    """
    Rewrites all of the items a user with the given id has on their inventory \n
    Returns the user
    """
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
@app.post("/{user_id}/{item_name}/{quantity}", response_model=User, tags=["user"])
def add_item_to_user(user_id: str, item_name: str, quantity:int, action:int) -> User:
    """
    Adds the given quantity of an item to the user with the given item name \n
    Returns the user
    """
    if quantity<=0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
    else:
        user = get_user(user_id)
        old_items = user.items
        found = False
        for indice in range(len(old_items)):
            if old_items[indice].name == item_name: #si ya lo tiene, suma la cantidad
                found=True
                break
        if found:
            old_items[indice].quantity = old_items[indice].quantity + quantity*action
                #old_items[indice]=old_items[indice].__dict__
            if old_items[indice].quantity == 0:
                old_items.pop(indice)
            
        else: #si no lo tiene, lo agrega al final de la lista de items
            new_item = get_item(item_name)
            new_item.quantity=quantity
            old_items.append(new_item)

        new=[] #to transform into dictionary
        for x in old_items:
            x=x.dict()
            new.append(x)
        user2 = update_user_items(user_id, new)

        logging.info(f"✨ {quantity} of item: {item_name} added to inventory for user: {user2}")
        emit_events.send(user_id, "update", user2.dict())
        return user2

@app.post("/buy/{user_id}/{item_name}/{quantity}", response_model=int, tags=["user actions"])
async def buy(user_id: str, item_name: str, quantity: int) -> int:
    """
    If the user with the given id has enough gold deletes the gold needed for the buy and adds the item to their inventory \n
    Returns 1 if the purchase was successful, 0 otherwise
    """
    if quantity<=0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
    else:
        item = get_item(item_name)
        item_id = ObjectId(item.id)
        total_cost = quantity*item.buy_price
        if get_user(user_id).gold < total_cost :
            #error no hay plata
            return 0
        else:
            payload = {'user_id':user_id, 'item_name': item_name, 'quantity': quantity, 'gold_spent': total_cost}
            user = add_item_to_user(user_id, item_name, quantity,1)
            new_gold = user.gold - total_cost
            user_id = ObjectId(user_id)
            mongodb_client.inventory.users.update_one(
                {'_id': user_id}, {"$set": {'gold':new_gold}})
            
            logging.info(f"✨ {quantity} of item: {item_name} purchased by user: {user}")
            emit_events.send(user_id, "purchase", payload)
            return 1

@app.post("/sell/{user_id}/{item_name}/{quantity}", response_model=int, tags=["user actions"])
async def sell(user_id: str, item_name: str, quantity: int) -> int:
    """
    If the user with the given id has enough of the item to complete the sale then deletes the required amount of the item from their inventory and adds the corresponding gold \n
    Returns 1 if the sell was successful, 0 otherwise
    """
    if quantity<=0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
    else:
        user = get_user(user_id)
        for item in user.items:
            if item.name == item_name:
                if quantity > item.quantity: 
                    return 0
                else:
                    item_id = get_item(item_name).id
                    user = add_item_to_user(user_id, item_name, quantity,-1)
                    price = quantity*get_item(item_name).sell_price
                    payload = {'user_id':user_id, 'item_name': item_name, 'quantity': quantity, 'gold_earned': price}
                    new_gold = user.gold + price
                    user_id = ObjectId(user_id)
                    mongodb_client.inventory.users.update_one(
                        {'_id': user_id}, {"$set": {'gold':new_gold}})
                    logging.info(f"✨ {quantity} of Item: {item_name} sold by user: {user}")
                    emit_events.send(user_id, "purchase", payload)
                    return 1
        return 0
