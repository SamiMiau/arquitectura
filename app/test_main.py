from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

# Response test
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

#  ------------------------------------------------------------------ User tests
# def test_add_user():
#     response = client.get("/newuser/{user_name}")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}
    
# def test_get_user():
#     response = client.get("/getuser/{user_id}")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

# def test_get_userid():
#     response = client.get("/getuserid/{user_name}")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

#the only important one here
def test_get_all_inventory_successful():
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.json() == [
  {
    "id": "6541129ff9f09a26f61f909b",
    "name": "Rose",
    "buy_price": 1,
    "sell_price": 999,
    "quantity": 49,
    "description": "Very pretty"
  },
  {
    "id": "65427686797f24b109923641",
    "name": "Strawberry",
    "buy_price": 10,
    "sell_price": 5,
    "quantity": 3,
    "description": "nice!"
  }
]

#  ------------------------------------------------------------------ Shop tests

def test_add_item():
    response = client.get("/newitem")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_get_all_items():
    response = client.get("/market")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_get_item():
    response = client.get("/getitem/{item_name}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_update_item():
    response = client.get("/updateitem/{item_name}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_delete_item():
    response = client.get("/deleteitem/{item_name}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

#  ------------------------------------------------------------------ Items tests

def test_update_user_items():
    response = client.get("/updateuseritems/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_add_item_to_user():
    response = client.get("/{user_id}/{item_name}/{quantity}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

#  ------------------------------------------------------------------ User actions tests

def test_buy_successful():
    response = client.get("/buy/{user_id}/{item_name}/{quantity}")
    assert response.status_code == 200
    assert response.json() == 1
def test_buy_unsuccessful():
    response = client.get("/buy/{user_id}/{item_name}/{quantity}")
    assert response.status_code == 200
    assert response.json() == 0

def test_sell_successful():
    response = client.get("/sell/{user_id}/{item_name}/{quantity}")
    assert response.status_code == 200
    assert response.json() == 1
def test_sell_unsuccessful():
    response = client.get("/sell/{user_id}/{item_name}/{quantity}")
    assert response.status_code == 200
    assert response.json() == 0