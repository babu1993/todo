import json
import sqlite3
from datetime import date
from datetime import datetime, UTC
from http import HTTPStatus
from uuid import uuid4
import re

import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from log import setup_json_logger
from pydantic import BaseModel, Field
from starlette.responses import FileResponse
from trimble.id import OpenIdEndpointProvider, ValidatedClaimsetProvider, OpenIdKeySetProvider
from fastmcp import FastMCP

conn = sqlite3.connect('todo.db')
conn.row_factory = sqlite3.Row
logger = setup_json_logger("./log_file.log", 'todo')

class Task(BaseModel):
    id:str =  Field(default_factory=uuid4)
    task_name: str
    description:str = Field(default="")
    status:str = Field(default="pending")
    date_added:date = Field(default_factory=date.today)
    user_id:str = Field(default="")

mcp = FastMCP()
@mcp.tool()
def query_logs(query: str="", _from: str="", to: str="", corr_id: str=""):
    """Adds two number"""
    response_logs = []
    with open("log_file.log", "r") as log:
        for line in log:
            data = json.loads(line)
            if corr_id and data['corr_id'] == corr_id:
                response_logs.append(data)
            if query:
                if re.match(query, data["message"]):
                    response_logs.append(data)
        return response_logs

@mcp.tool()
def reassign_task(task_id: str, from_user_id: str, new_user_id: str):
    update_statement = f"update tasks set user_id='{new_user_id}' where id='{task_id}'"
    logger.info(f"from:{from_user_id} to:{new_user_id} taskid:{task_id}")
    try:
        conn.execute(update_statement)
        conn.commit()
    except Exception:
        logger.info("Reassign error")
    return "True"

mcp_http_app = mcp.http_app(path="/mcp")
api = FastAPI(root_path="/api", lifespan=mcp_http_app.lifespan)
api.mount("/tools", mcp_http_app)

@api.middleware("http")
async def token_verifier(request: Request, call_next):
    auth = request.headers.get('Authorization')
    if auth:
        try:
            token = auth.split(" ")[1]
            endpoint_provider = OpenIdEndpointProvider("https://stage.id.trimblecloud.com/.well-known/openid-configuration")
            keyset_provider = OpenIdKeySetProvider(endpoint_provider)
            claimset_provider = ValidatedClaimsetProvider(keyset_provider)

            # Retrieve claimset using the token
            claimset = await claimset_provider.retrieve_claimset(token)
        except Exception as e:
            logger.info(f"Error in authorization")
            return Response(status_code=HTTPStatus.FORBIDDEN)
    else:
        return Response(status_code=HTTPStatus.BAD_REQUEST)
    request.state.subject = claimset['sub']
    request.state.corr = claimset['jti']
    response = await call_next(request)
    return response

@api.post("/tasks")
async def create_tasks(request: Request, task:Task):
    user_id = request.state.subject
    task.user_id = user_id
    insert_smt = f"INSERT INTO tasks (id, task_name, description, date_added, user_id) VALUES ('{task.id}', '{task.task_name}', '{task.description}', '{datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S")}', '{task.user_id}')"
    try:
        conn.execute(insert_smt)
        conn.commit()
    except Exception as e:
        logger.info(e)
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=json.dumps({}))
    return Response(status_code=HTTPStatus.OK, content=json.dumps({}))

@api.get("/tasks")
async def get_tasks(request: Request):
    user_id = request.state.subject
    # [_ID=GetTasksLog]
    logger.info(f"Get task received for user: {user_id}", extra={"corr_id": request.state.corr})
    curr = conn.execute(f"select * from tasks where user_id='{user_id}'")
    rows = curr.fetchall()
    tasks = [{"id": row["id"], "description": row["description"],
              "status": row["status"], "data": row["date_added"],
              "task_name": row["task_name"]} for row in rows]
    #[_ID=GetTasksSuccess]
    logger.info(f"Successfully retrieved tasks for user:{user_id}", extra={"corr_id": request.state.corr})
    return tasks

def reassign_tasks_job(task_id, user_id, new_user_id, corr):
    try:
        con = sqlite3.connect('todo.db')
        con.execute(f"update tasks set user_id='' where id={task_id}")
        con.commit()
        raise Exception()
    except Exception:
        # [_ID=AssignTaskError]
        logger.info(f"Error occurred while reassigning task: {task_id} from user: {user_id} to new_user:{new_user_id}",
                    extra={"corr_id": corr})

@api.patch("/tasks/{task_id}/reassign")
async def reassign_tasks(task_id: str, new_user_id: str, request: Request, back: BackgroundTasks):
    user_id = request.state.subject
    #[_ID=ReassignRequest]
    logger.info(f"Reassign request received for task:{task_id} from user: {user_id} to new_user:{new_user_id}",
                extra={"corr_id": request.state.corr})
    back.add_task(reassign_tasks_job, task_id, user_id, new_user_id, request.state.corr)
    return Response(status_code=HTTPStatus.ACCEPTED, content=json.dumps({}))

@api.delete("/tasks/{task_id}")
async def delete_task(task_id:str, request:Request):
    user_id = request.state.subject
    delete_smt = f"DELETE FROM tasks where id='{task_id}'"
    logger.info(f"Task Delete requested for task:{task_id} by user:{user_id}", extra={"corr_id": request.state.corr})
    try:
        conn.execute(delete_smt)
        conn.commit()
    except Exception as e:
        logger.info(e)
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=json.dumps({}))
    logger.info(f"Task Deleted:{task_id}", extra={"corr_id": request.state.corr})
    return Response(status_code=HTTPStatus.OK)

# Main APP
app = FastAPI(lifespan=mcp_http_app.lifespan)

app.mount("/static", StaticFiles(directory="ui/build/static"), name="static")
@app.get("/")
async def ui():
    return FileResponse("ui/build/index.html")

app.mount("/api", api)



if __name__ == "__main__":
    conn.execute("DROP TABLE IF EXISTS tasks")
    conn.execute('''CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    task_name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    date_added TEXT,
    user_id TEXT
);''')
    for i in range(1, 5):
        insert = f"INSERT INTO tasks (id, task_name, description, date_added, user_id) VALUES ('{i}', 'TODO_{i}', 'd_{i}', '{datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S")}', '1b492058-2c9b-4593-817d-6b48ac4f1db9')"
        conn.execute(insert)
    conn.commit()
    uvicorn.run("main:app", host="0.0.0.0",
        port=8080,
        log_level="debug",
        reload=True,)
