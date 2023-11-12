from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

# Response test
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

#  ------------------------------------------------------------------ User tests
def test_add_user():
    response = client.get("/newuser/{user_name}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
    
def test_get_user():
    response = client.get("/getuser/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_get_userid():
    response = client.get("/getuserid/{user_name}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

#the only important one here
def test_get_all_inventory():
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

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

def test_buy():
    response = client.get("/buy/{user_id}/{item_name}/{quantity}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_sell():
    response = client.get("/sell/{user_id}/{item_name}/{quantity}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}