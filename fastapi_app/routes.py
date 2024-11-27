from fastapi import FastAPI, HTTPException, Depends, Query
from tokene import  uri, password, user,token3
import logging
from neo4j import GraphDatabase
from upload2 import create_relationship, create_group, create_user
from fastapi import FastAPI, Depends, HTTPException, Header



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=(
    user, password))

def verify_token(x_token: str = Header(...)):
    if x_token != token3:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/token")
async def login():
    return {"message": "Token authentication is set up. Use the token to access protected routes."}

@app.get("/nodes")
async def get_all_nodes():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN id(n) as id, labels(n) as label")
        return [{"id": record["id"], "label": record["label"][0]} for record in result]  

@app.get("/nodesss/{node_id}")
async def get_node_and_relationships(node_id: str):
 
    node_id = node_id.strip() 
    try:
        node_id_int = int(node_id)  # Преобразуем в целое число
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid node ID")

    with driver.session() as session:

        user_result = session.run("MATCH (u:User {id: $node_id}) RETURN u", node_id=node_id_int)
        group_result = session.run("MATCH (g:Group {id: $node_id}) RETURN g", node_id=node_id_int)

        user = user_result.single()
        group = group_result.single()

        if not user and not group:
            raise HTTPException(status_code=404, detail="Node not found")

        node = user["u"] if user else group["g"]
        
    
        relationships_result = session.run("""
            MATCH (n)-[r]->(m)
            WHERE id(n) = $node_id OR id(m) = $node_id
            RETURN n, r, m
        """, node_id=node_id_int)

        relationships = []
        for record in relationships_result:
            relationships.append({
                "node": dict(record["n"]),  # Узел n
                "relationship": dict(record["r"]),  # Связь r
                "target_node": dict(record["m"])  # Узел m на конце связи
            })

        return {
            "node": dict(node),  # Узел с его атрибутами
            "relationships": relationships  # Все связи с их атрибутами
        }


@app.get("/nodes/{node_id}")
async def get_node_and_relationships(node_id: str):
   
    node_id = node_id.strip()  

    with driver.session() as session:
       
        user_result = session.run("MATCH (u:User {id: $node_id}) RETURN u", node_id=node_id)
        group_result = session.run("MATCH (g:Group {id: $node_id}) RETURN g", node_id=node_id)

        user = user_result.single()
        group = group_result.single()

        if not user and not group:
            raise HTTPException(status_code=404, detail="Node not found")

        node = user["u"] if user else group["g"]
        
      
        relationships_result = session.run("""
            MATCH (n)-[r]->(m)
            WHERE n.id = $node_id OR m.id = $node_id
            RETURN n, r, m
        """, node_id=node_id)

        relationships = []
        for record in relationships_result:
            relationships.append({
                "node": dict(record["n"]),  
                "relationship": dict(record["r"]), 
                "target_node": dict(record["m"]) 
            })

        return {
            "node": dict(node),  
            "relationships": relationships  
        }

    
@app.post("/node",dependencies=[Depends(verify_token)])
async def create_node_and_relationship(data: dict):
    with driver.session() as session:

        if data['label'] == 'User':
            user_info = {
                'id': data['id'],
                'name': data['name'],
                'sex': data['sex'],
                'home_town': data['home_town']
            }
            session.write_transaction(create_user, user_info)
            response_message = "User created"
        
        elif data['label'] == 'Group':
            group_info = {
                'id': data['id'],
                'name': data['name']
            }
            session.write_transaction(create_group, group_info)
            response_message = "Group created"
        
        else:
            raise HTTPException(status_code=400, detail="Invalid label")

    
        if 'user_id' in data and 'group_id' in data:
            session.write_transaction(create_relationship, data['user_id'], data['group_id'])
            response_message += f" and relationship created between User {data['user_id']} and Group {data['group_id']}"

    return {"message": response_message, "id": data['id']}


@app.delete("/node/{node_id}", dependencies=[Depends(verify_token)])
async def delete_node_and_relationship(node_id: str, user_id: str = Query(None), group_id: str = Query(None)):
    with driver.session() as session:
        user = session.run("MATCH (u:User {id: $id}) RETURN u", id=node_id).single()
        group = session.run("MATCH (g:Group {id: $id}) RETURN g", id=node_id).single()

        response_message = None

        if user:
            session.run("MATCH (u:User {id: $id}) DETACH DELETE u", id=node_id)
            response_message = "User deleted"
        elif group:
            session.run("MATCH (g:Group {id: $id}) DETACH DELETE g", id=node_id)
            response_message = "Group deleted"

        if user_id and group_id:
            session.run("""
                MATCH (u:User {id: $user_id})-[r:SUBSCRIBES]->(g:Group {id: $group_id})
                DELETE r
            """, user_id=user_id, group_id=group_id)
            response_message += f" and relationship between User {user_id} and Group {group_id} deleted" if response_message else "Relationship deleted"

        if response_message is None:
            raise HTTPException(status_code=404, detail="Node not found")

    return {"message": response_message}

