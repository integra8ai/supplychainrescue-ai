"""
Forecasting API routes for SupplyChainRescue AI.
Provides delay prediction and forecasting capabilities based on weather and traffic data.
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.database import get_db
from backend.models.schemas import (
    ForecastPrediction, APIResponse, WeatherForecastRequest
)
from backend.models.sql_models import ForecastPrediction as SQLForecastPrediction

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)


@router.get("/health", response_model=APIResponse)
async def forecast_health_check():
    """Forecast service health check"""
    return APIResponse(
        success=True,
        message="Forecast service is operational",
        data={"status": "active", "model": "rule-based"}
    )


@router.post("/predict", response_model=APIResponse)
async def generate_forecast_prediction(
    road_id: int,
    request: WeatherForecastRequest,
    db: Session = Depends(get_db)
):
    """
    Generate road delay forecast prediction for a specific road and location.
    Uses rule-based logic based on weather conditions.
    """
    try:
        # Simple rule-based prediction logic
        # In reality, this would involve ML models and actual weather data

        base_delay = 0
        weather_factor = 0.0
        traffic_factor = 0.0

        # Mock weather conditions for demonstration
        # In production, would fetch actual weather data
        mock_visibility = 8000  # meters
        mock_wind_speed = 5.5   # m/s
        mock_precipitation = 0.0  # mm
        mock_temp = 20.0  # Celsius

        # Rule-based weather impact
        if mock_visibility < 5000:
            weather_factor += 0.4
            base_delay += 20
        elif mock_visibility < 10000:
            weather_factor += 0.2
            base_delay += 10

        if mock_wind_speed > 10:
            weather_factor += 0.3
            base_delay += 15

        if mock_precipitation > 5:
            weather_factor += 0.5
            base_delay += 30

        if mock_temp < 0:
            weather_factor += 0.3
            base_delay += 25

        # Calculate final prediction
        delay_probability = min(1.0, weather_factor + 0.1)
        estimated_delay = min(180, base_delay + 10)  # cap at 3 hours
        confidence = 0.8  # Base confidence for rule-based system
        traffic_factor = 0.1  # Placeholder for traffic impact

        prediction = ForecastPrediction(
            timestamp=datetime.utcnow(),
            road_id=road_id,
            delay_probability=delay_probability,
            estimated_delay=estimated_delay,
            confidence=confidence,
            weather_factor=weather_factor,
            traffic_factor=traffic_factor
        )

        # Store in database
        db_prediction = SQLForecastPrediction(**prediction.dict())
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)

        return APIResponse(
            success=True,
            message="Forecast prediction generated successfully",
            data={
                "prediction": prediction.dict(),
                "prediction_id": db_prediction.id
            }
        )

    except Exception as e:
        logger.error(f"Error generating forecast prediction: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{road_id}", response_model=APIResponse)
async def get_road_predictions(road_id: int, db: Session = Depends(get_db)):
    """Get all predictions for a specific road"""
    try:
        predictions = db.query(SQLForecastPrediction).filter(
            SQLForecastPrediction.road_id == road_id
        ).all()

        data = []
        for p in predictions:
            d = p.__dict__
            del d['_sa_instance_state']
            data.append(d)

        return APIResponse(
            success=True,
            message=f"Retrieved {len(data)} predictions for road {road_id}",
            data={"predictions": data}
        )

    except Exception as e:
        logger.error(f"Error retrieving predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
