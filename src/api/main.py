from fastapi import FastAPI
from routes import prices, stats, health

app = FastAPI(
    title="USDA ETL API",
    description="API to query processed USDA Quick Stats data",
    version="1.0.0"
)

app.include_router(prices.router, prefix="/prices", tags=["Prices"])
app.include_router(stats.router, prefix="/stats", tags=["Stats"])
app.include_router(health.router, prefix="/health", tags=["Health"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the USDA ETL API"}
