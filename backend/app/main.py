"""Main FastAPI Application Entry Point for Quantum FlightPath Optimizer."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("quantum_flightpath")

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Quantum-Assisted Aviation Route and Emissions Optimization Decision-Support System. "
        "Formulates flight path selection into QUBO and executes genuine Qiskit QAOA circuits."
    ),
    version=settings.APP_VERSION,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows development on Vite and external local preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def read_root():
    return {
        "name": settings.APP_NAME,
        "subtitle": settings.APP_SUBTITLE,
        "version": settings.APP_VERSION,
        "disclaimer": settings.AVIATION_DISCLAIMER,
        "docs_url": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Quantum FlightPath Optimizer API"}
