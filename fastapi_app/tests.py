import pytest
from fastapi.testclient import TestClient
from tokene import token3
from fastapi_app.app import app
import json
from neo4j import GraphDatabase
from tokene import  uri, password, user



uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=(
    user, password))

client = TestClient(app)

@pytest.fixture
def token():
    return token3

#для проверки использовать:  pytest -s fastapi_app/tests.py::test_get_all_nodes
def test_get_all_nodes():
    response = client.get("/nodes")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)  
    assert len(data) > 0  

def test_get_node():
    response = client.get("/nodesss/some_user_id")  #  путь на /nodesss/
    assert response.status_code in {200, 404, 400}

def test_create_user(token):
    response = client.post("/node", json={
        "label": "User", 
        "id": "3", 
        "name": "John", 
        "sex": "male", 
        "home_town": "City"
    }, headers={"x-token": token})  #  x-token вместо Authorization
    assert response.status_code == 200
    assert response.json()["message"] == "User created"

def test_delete_user(token, user_id: str = "3", group_id: str = None):

    response = client.delete(f"/node/{user_id}?user_id={user_id}&group_id={group_id}", headers={"x-token": token})

 
    assert response.status_code in (200, 404)

   
    response_data = response.json()
    assert "message" in response_data


    with driver.session() as session:
        user_exists = session.run("MATCH (u:User {id: $id}) RETURN u", id=user_id).single()
        assert user_exists is None

        
        if group_id:
            relationship_exists = session.run("""
                MATCH (u:User {id: $user_id})-[r:SUBSCRIBES]->(g:Group {id: $group_id})
                RETURN r
            """, user_id=user_id, group_id=group_id).single()
            assert relationship_exists is None
