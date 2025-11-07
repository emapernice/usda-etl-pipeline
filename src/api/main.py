from fastapi import FastAPI
from routes import prices

app = FastAPI(
    title="USDA ETL API",
    description="API to query processed data from the USDA Quick Stats",
    version="1.0.0"
)

app.include_router(prices.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the USDA ETL API"}

