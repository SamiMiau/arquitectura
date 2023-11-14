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
    "quantity": 4,
    "description": "Nice and sweet!!"
  },
  {
    "id": "65516da0d1694e37ed09683f",
    "name": "Pear",
    "buy_price": 999,
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

def test_add_item_allparameters():
    response = client.post("/newitem", json={
        "name": "TestItem1",
        "buy_price": 10000,
        "sell_price": 500,
        "description": "Test Description"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestItem1"
    assert data["buy_price"] == 10000
    assert data["sell_price"] == 500
    assert data["quantity"] == 1
    assert data["description"] == "Test Description"
def test_add_item_someparameters():
    response = client.post("/newitem", json={
        "name": "TestItem2",
        "buy_price": 10000,
        "sell_price": 500,
        "quantity": 1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestItem2"
    assert data["buy_price"] == 10000
    assert data["sell_price"] == 500
    assert data["quantity"] == 1
    assert data["description"] == "stuff!!"

def test_get_all_items_successful_all():
    response = client.get("/market")
    assert response.status_code == 200
    assert type(response.json()[0]) == dict
def test_get_all_items_successful_list():
    response = client.get("/market?id=65516ccbd1694e37ed09683e&id=65516da0d1694e37ed09683f")
    assert response.status_code == 200
    assert response.json() == [
  {
    "id": "65516ccbd1694e37ed09683e",
    "name": "Strawberry",
    "buy_price": 50,
    "sell_price": 10,
    "quantity": 1,
    "description": "Nice and sweet!!"
  },
  {
    "id": "65516da0d1694e37ed09683f",
    "name": "Pear",
    "buy_price": 999,
    "sell_price": 50,
    "quantity": 1,
    "description": "Perame tantito"
  }
]
def test_get_all_items_unsuccessful_list():
    response = client.get("/market?id=75516da0d1694e37ed09683f")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Items not found"
    }

def test_get_item_successful():
    response = client.get("/getitem/Strawberry")
    assert response.status_code == 200
    assert response.json() == {
      "id": "65516ccbd1694e37ed09683e",
      "name": "Strawberry",
      "buy_price": 50,
      "sell_price": 10,
      "quantity": 1,
      "description": "Nice and sweet!!"
    }
def test_get_item_unsuccessful_404():
    response = client.get("/getitem/Frutilla")
    assert response.status_code == 404
    assert response.json() == {
      "detail": "Item not found"
    }

def test_update_item():
    response = client.put("/updateitem/Pear", json = {
    "name": "Pear",
    "buy_price": 1000,
    "sell_price": 50,
    "quantity": 1,
    "description": "Perame tantito"
    })
    assert response.status_code == 200
    assert response.json() == {
    "id": "65516da0d1694e37ed09683f",
    "name": "Pear",
    "buy_price": 1000,
    "sell_price": 50,
    "quantity": 1,
    "description": "Perame tantito"
    }
    response2 = client.put("/updateitem/Pear", json = {
    "name": "Pear",
    "buy_price": 999,
    "sell_price": 50,
    "quantity": 1,
    "description": "Perame tantito"
    })
    assert response2.status_code == 200
    assert response2.json() == {
      "id": "65516da0d1694e37ed09683f",
      "name": "Pear",
      "buy_price": 999,
      "sell_price": 50,
      "quantity": 1,
      "description": "Perame tantito"
    }
def test_update_item_unsuccessful_404():
    response = client.put("/updateitem/Perita", json = {
    "name": "Perita",
    "buy_price": 1000,
    "sell_price": 50,
    "quantity": 1,
    "description": "Perame tantito plss"
    })
    assert response.status_code == 404
    assert response.json() == {
    "detail": "Item not found"
    }

def test_delete_item():
    response = client.post("/newitem", json={
        "name": "DeleteTestItem",
        "buy_price": 10000,
        "sell_price": 500,
        "description": "Test Description"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "DeleteTestItem"
    assert data["buy_price"] == 10000
    assert data["sell_price"] == 500
    assert data["quantity"] == 1
    assert data["description"] == "Test Description"

    response2 = client.delete("/deleteitem/DeleteTestItem")
    assert response2.status_code == 200
    assert response2.json() == "ok"
def test_delete_item_unsuccessful_404():
    response2 = client.delete("/deleteitem/DeleteTestItem2")
    assert response2.status_code == 404
    assert response2.json() == {
    "detail": "Item not found"
    }

# #  ------------------------------------------------------------------ Items tests

def test_update_user_items():
    response = client.put("/updateuseritems/65516c90d1694e37ed09683d", json=[{
        "id": "65516ccbd1694e37ed09683e",
        "name": "Strawberry",
        "buy_price": 50,
        "sell_price": 10,
        "quantity": 100,
        "description": "Nice and sweet!!"
        }])
    assert response.status_code == 200
    assert response.json() == {
    "id": "65516c90d1694e37ed09683d",
    "name": "Jacinta",
    "gold": 1000,
    "items": [
      {
      "id": "65516ccbd1694e37ed09683e",
      "name": "Strawberry",
      "buy_price": 50,
      "sell_price": 10,
      "quantity": 100,
      "description": "Nice and sweet!!"
    }
    ]
    }
def test_update_user_items_unsuccessful_404():
    response = client.put("/updateuseritems/76516c90d1694e37ed09683d", json=[{
        "id": "65516ccbd1694e37ed09683e",
        "name": "Strawberry",
        "buy_price": 50,
        "sell_price": 10,
        "quantity": 100,
        "description": "Nice and sweet!!"
        }])
    assert response.status_code == 404
    assert response.json() == {
    "detail": "User not found"
    }

def test_add_item_to_user():
    response1 = client.put("/updateuseritems/65522021e80ede849e09d703", json=[])
    response = client.post("/65522021e80ede849e09d703/Strawberry/1?action=1")
    assert response.status_code == 200
    assert response.json() == {
    "id": "65522021e80ede849e09d703",
    "name": "Facundo",
    "gold": 1000,
    "items": [
      {
      "id": "65516ccbd1694e37ed09683e",
      "name": "Strawberry",
      "buy_price": 50,
      "sell_price": 10,
      "quantity": 1,
      "description": "Nice and sweet!!"
      }
    ]
  }
def test_add_item_to_user_unsuccessful_404():
    response = client.post("/76522021e80ede849e09d703/Strawberry/1?action=1")
    assert response.status_code == 404
    assert response.json() == {
    "detail": "User not found"
    }

# #  ------------------------------------------------------------------ User actions tests

def test_buy_successful():
    response = client.post("/buy/655150ba2232f506445756a4/Strawberry/1")
    assert response.status_code == 200
    assert response.json() == 1
def test_buy_unsuccessful_notenoughgold():
    response = client.post("/buy/655150ba2232f506445756a4/Strawberry/1000")
    assert response.status_code == 200
    assert response.json() == 0

def test_sell_successful():
    response = client.post("/sell/655150ba2232f506445756a4/Strawberry/1")
    assert response.status_code == 200
    assert response.json() == 1
def test_sell_unsuccessful():
    response = client.post("/sell/655150ba2232f506445756a4/Strawberry/1000")
    assert response.status_code == 200
    assert response.json() == 0


# #  ------------------------------------------------------------------ Delete testing item remains
def test_delete_item():
    response1 = client.delete("/deleteitem/DeleteTestItem")
    response2 = client.delete("/deleteitem/TestItem")
    response3 = client.delete("/deleteitem/TestItem1")
    response4 = client.delete("/deleteitem/TestItem2")
    response5 = client.delete("/deleteitem/TestItem1")
    response6 = client.delete("/deleteitem/TestItem2")
    assert response3.status_code == 200