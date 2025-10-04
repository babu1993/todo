from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="ui/build/static"), name="static")

@app.get("/")
async def ui():
    return FileResponse("ui/build/index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0",
        port=8080,
        log_level="debug",
        reload=True,)
