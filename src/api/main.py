from fastapi import FastAPI
from src.api.routes import price, production, yield_report, health

app = FastAPI(
    title="USDA ETL API",
    description="API to query USDA Quick Stats processed data",
    version="1.0.0"
)

# Register report routes
app.include_router(price.router, prefix="/reports/price", tags=["Price"])
app.include_router(production.router, prefix="/reports/production", tags=["Production"])
app.include_router(yield_report.router, prefix="/reports/yield", tags=["Yield"])

# Healthcheck
app.include_router(health.router, prefix="/health", tags=["Health"])

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the USDA ETL API"}
