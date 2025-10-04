from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import uvicorn
import sqlite3
from datetime import datetime, UTC
from log import setup_json_logger
from trimble.id import OpenIdEndpointProvider, ValidatedClaimsetProvider, OpenIdKeySetProvider
from http import HTTPStatus
conn = sqlite3.connect('todo.db')
conn.row_factory = sqlite3.Row
app = FastAPI()

logger = setup_json_logger("./log_file.json", 'todo')
app.mount("/static", StaticFiles(directory="ui/build/static"), name="static")

@app.get("/")
async def ui():
    return FileResponse("ui/build/index.html")

api = FastAPI(root_path="/api")

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
    response = await call_next(request)
    return response

@api.get("/tasks")
async def get_tasks(request: Request):
    user_id = request.state.subject
    logger.info(f"Get task received for user: {user_id}")
    curr = conn.execute(f"select * from tasks where user_id='{user_id}'")
    rows = curr.fetchall()
    tasks = [{"id": row["id"], "description": row["description"],
              "status": row["status"], "data": row["date_added"],
              "task_name": row["task_name"]} for row in rows]
    return tasks


app.mount("/api", api)

if __name__ == "__main__":
    conn.execute("DROP TABLE IF EXISTS tasks")
    conn.execute('''CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    task_name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    date_added TEXT,
    user_id TEXT
);''')
    for i in range(1, 5):
        insert = f"INSERT INTO tasks (id, task_name, description, date_added, user_id) VALUES ({i}, 'TODO_{i}', 'd_{i}', '{datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S")}', '1b492058-2c9b-4593-817d-6b48ac4f1db9')"
        conn.execute(insert)
    conn.commit()
    uvicorn.run("main:app", host="0.0.0.0",
        port=8080,
        log_level="debug",
        reload=True,)
