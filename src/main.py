from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/ui/")
def get_ui():
    return "hi"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0",
        port=8080,
        log_level="debug",
        reload=True,)
