"""
Forecasting API routes for SupplyChainRescue AI.
Provides delay prediction and forecasting capabilities based on weather and traffic data.
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.database import get_db
from backend.models.schemas import (
    ForecastPrediction, APIResponse, WeatherForecastRequest
)
from backend.models.sql_models import ForecastPrediction as SQLForecastPrediction
from backend.ml_models.delay_predictor import get_delays_predictor

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)


@router.get("/health", response_model=APIResponse)
async def forecast_health_check():
    """Forecast service health check"""
    try:
        predictor = get_delays_predictor()
        ml_status = "trained" if predictor.weights is not None else "fallback"
        return APIResponse(
            success=True,
            message="Forecast service is operational",
            data={
                "status": "active",
                "ml_model": ml_status,
                "features": predictor.feature_names if predictor.weights is not None else []
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return APIResponse(
            success=False,
            message="Forecast service health check failed",
            data={"error": str(e)}
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
        # Get ML model predictor
        predictor = get_delays_predictor()

        # Prepare features for ML model - in production, fetch actual weather data
        # For now, use mock weather conditions that would come from API
        features = {
            'visibility': 8000,  # meters - good visibility
            'wind_speed': 5.5,   # m/s - moderate wind
            'precipitation': 0.0,  # mm - no precipitation
            'temperature': 20.0,  # Celsius - moderate temperature
            'traffic_load': 0.3,  # normalized 0-1 (low traffic)
            'road_type_factor': 1.0  # highway = 1.0
        }

        # Use ML model to predict delay
        estimated_delay = predictor.predict(features)

        # Calculate weather factor based on conditions
        weather_factor = 0.0
        if features['visibility'] < 5000:
            weather_factor += 0.4
        elif features['visibility'] < 10000:
            weather_factor += 0.2

        if features['wind_speed'] > 10:
            weather_factor += 0.3

        if features['precipitation'] > 5:
            weather_factor += 0.5

        if features['temperature'] < 0:
            weather_factor += 0.3

        # Calculate probability based on delay magnitude
        # 60min delay = 100% prob
        delay_probability = min(1.0, estimated_delay / 60 + 0.1)

        # Set confidence based on model type and data
        confidence = 0.95 if predictor.weights is not None else 0.8
        traffic_factor = features['traffic_load']

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
