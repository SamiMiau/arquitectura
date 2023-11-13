from fastapi.testclient import TestClient
# import requests

from main import app

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
    response = client.get("/inventory?user_id=655150ba2232f506445756a4")
    assert response.status_code == 200
    assert response.json() == [
  {
    "id": "65516ccbd1694e37ed09683e",
    "name": "Strawberry",
    "buy_price": 50,
    "sell_price": 10,
    "quantity": 5,
    "description": "Nice and sweet!!"
  },
  {
    "id": "65516da0d1694e37ed09683f",
    "name": "Pear",
    "buy_price": 100,
    "sell_price": 50,
    "quantity": 2,
    "description": "Perame tantito"
  }
]
def test_get_all_inventory_unsuccessful_404():
    #user id not found
    response = client.get("/inventory?user_id=123456")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }

#  ------------------------------------------------------------------ Shop tests

def test_add_item():
    response = client.post("/newitem", json={
        "name": "TestItem",
        "buy_price": 10000,
        "sell_price": 500,
        "description": "Test Description"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestItem"
    assert data["buy_price"] == 10000
    assert data["sell_price"] == 500
    assert data["quantity"] == 1
    assert data["description"] == "Test Description"

def test_get_all_items_successful():
    response = client.get("/market")
    assert response.status_code == 200
    assert type(response.json()[0]) == dict

# def test_get_item():
#     response = client.get("/getitem/{item_name}")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

# def test_update_item():
#     response = client.get("/updateitem/{item_name}")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

# def test_delete_item():
#     response = client.get("/deleteitem/{item_name}")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

# #  ------------------------------------------------------------------ Items tests

# def test_update_user_items():
#     response = client.get("/updateuseritems/{user_id}")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

# def test_add_item_to_user():
#     response = client.get("/{user_id}/{item_name}/{quantity}")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

# #  ------------------------------------------------------------------ User actions tests

# def test_buy_successful():
#     response = client.get("/buy/{user_id}/{item_name}/{quantity}")
#     assert response.status_code == 200
#     assert response.json() == 1
# def test_buy_unsuccessful():
#     response = client.get("/buy/{user_id}/{item_name}/{quantity}")
#     assert response.status_code == 200
#     assert response.json() == 0

# def test_sell_successful():
#     response = client.get("/sell/{user_id}/{item_name}/{quantity}")
#     assert response.status_code == 200
#     assert response.json() == 1
# def test_sell_unsuccessful():
#     response = client.get("/sell/{user_id}/{item_name}/{quantity}")
#     assert response.status_code == 200
#     assert response.json() == 0