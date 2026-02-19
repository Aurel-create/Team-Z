from fastapi import FastAPI
from backend.api import routes_personal_infos

app = FastAPI(
    title="Portfolio API",
    description="API Data-Driven pour mon portfolio (MongoDB & Neo4j)",
    version="1.0.0"
)

app.include_router(routes_personal_infos.router)

@app.get("/")
def read_root():
    return {"message": "Portfolio API is running!"}