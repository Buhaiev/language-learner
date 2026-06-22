from fastapi import FastAPI
import uvicorn

from app.routers.learn import router as learn_router
from app.routers.translate import router as translate_router
from app.routers.words import router as words_router
from fastapi.responses import RedirectResponse

app = FastAPI()
app.include_router(translate_router)
app.include_router(learn_router)
app.include_router(words_router)

@app.get("/")
def root():
    return RedirectResponse("/translate")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)