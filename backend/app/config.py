"""Configuration management for Quantum FlightPath Optimizer."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Quantum FlightPath Optimizer"
    APP_SUBTITLE: str = "Quantum-Assisted Aviation Route and Emissions Optimization"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # IBM Quantum Configuration
    IBM_QUANTUM_TOKEN: Optional[str] = os.getenv("IBM_QUANTUM_TOKEN", None)
    IBM_QUANTUM_INSTANCE: Optional[str] = os.getenv("IBM_QUANTUM_INSTANCE", None)
    DEFAULT_QUANTUM_SHOTS: int = 1024
    
    # Map & External APIs
    MAP_TILE_URL: str = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    MAP_ATTRIBUTION: str = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    
    # Regulatory Disclaimer
    AVIATION_DISCLAIMER: str = (
        "This application provides research and decision-support recommendations based on available "
        "aeronautical information. Its output is not an ATC clearance, certified operational flight plan, "
        "or authorization to operate an aircraft. Actual flight routing remains subject to applicable aviation "
        "regulations, current aeronautical information, weather, aircraft capability, operational constraints, "
        "and ATC authorization."
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
