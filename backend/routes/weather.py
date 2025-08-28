"""
Weather API routes for SupplyChainRescue AI.
Integrates with weather services to provide forecast and current conditions data.
"""
import asyncio
import logging
import requests
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from backend.config import settings
from backend.models.schemas import (
    WeatherData, WeatherCondition, WeatherForecastRequest, APIResponse
)

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)


@router.get("/health", response_model=APIResponse)
async def weather_health_check():
    """Weather service health check"""
    api_status = "disconnected"
    if settings.openweather_api_key:
        api_status = "connected"
    else:
        api_status = "api_key_missing"

    return APIResponse(
        success=True,
        message="Weather service status check",
        data={"status": api_status, "provider": "OpenWeatherMap"}
    )


@router.get("/current", response_model=APIResponse)
async def get_current_weather(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    units: str = Query("metric", regex="^(metric|imperial)$",
                       description="Units: metric or imperial")
):
    """
    Get current weather conditions for a location.
    Integrates with OpenWeatherMap API.
    """
    try:
        # Mock implementation for now - will integrate with real API
        weather_data = WeatherData(
            temperature=22.5,
            temperature_feels_like=25.2,
            humidity=65,
            pressure=1013,
            visibility=10000,
            wind_speed=3.1,
            wind_direction=180,
            weather_condition=WeatherCondition(
                main="Clear",
                description="clear sky",
                icon="01d"
            ),
            timestamp=datetime.utcnow()
        )

        return APIResponse(
            success=True,
            message="Current weather retrieved successfully",
            data=weather_data.dict()
        )

    except Exception as e:
        logger.error(f"Error retrieving current weather: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast", response_model=APIResponse)
async def get_weather_forecast(request: WeatherForecastRequest):
    """
    Get weather forecast for a location with specified hours ahead.
    """
    try:
        # Mock forecast data for now
        forecast_hours = []
        base_time = datetime.utcnow()

        for i in range(min(request.hours_ahead, 48)):  # OpenWeatherMap API limit
            forecast_time = base_time + timedelta(hours=i)
            weather_data = WeatherData(
                # Temperature variation
                temperature=20.0 + (2.5 * (1 if i < 12 else -1)),
                temperature_feels_like=22.0 + (2.0 * (1 if i < 12 else -1)),
                humidity=60 + (i % 20),  # Humidity variation
                pressure=1010 + (i % 10),
                visibility=9000 if i > 24 else 10000,  # Reduced visibility at night
                wind_speed=2.5 + (i % 3),
                wind_direction=180 + (i * 5),  # Wind direction shift
                weather_condition=WeatherCondition(
                    main="Clouds" if i < 12 else "Clear",
                    description="few clouds" if i < 12 else "clear sky",
                    icon="02d" if i < 12 else "01d"
                ),
                timestamp=forecast_time
            )
            forecast_hours.append(weather_data.dict())

        return APIResponse(
            success=True,
            message=f"Weather forecast for {request.hours_ahead} hours retrieved",
            data={
                "location": {"lat": request.latitude, "lon": request.longitude},
                "forecast": forecast_hours,
                "hours_requested": request.hours_ahead,
                "provider": "OpenWeatherMap"
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving weather forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical", response_model=APIResponse)
async def get_historical_weather(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    start_date: datetime = Query(...,
                                 description="Start date for historical data"),
    end_date: datetime = Query(...,
                               description="End date for historical data"),
    max_records: int = Query(
        100, le=500, description="Maximum number of records to return")
):
    """
    Get historical weather data for analysis and model training.
    """
    try:
        # Mock historical data for now
        historical_data = []
        current_time = start_date

        while current_time < end_date and len(historical_data) < max_records:
            weather_data = WeatherData(
                # Temperature variation by hour
                temperature=15.0 + (10.0 * (current_time.hour / 24)),
                temperature_feels_like=17.0 + (8.0 * (current_time.hour / 24)),
                humidity=70 - (current_time.hour % 30),
                pressure=1010 + (current_time.day % 20),
                visibility=8000 if current_time.hour < 6 or current_time.hour > 18 else 10000,
                wind_speed=1.5 + (current_time.hour % 5),
                wind_direction=200 + (current_time.month * 10),
                weather_condition=WeatherCondition(
                    main="Clear" if current_time.hour > 6 and current_time.hour < 18 else "Clouds",
                    description="clear sky" if current_time.hour > 6 and current_time.hour < 18 else "overcast clouds",
                    icon="01d" if current_time.hour > 6 and current_time.hour < 18 else "04d"
                ),
                timestamp=current_time
            )
            historical_data.append(weather_data.dict())
            # 3-hour intervals for historical data
            current_time += timedelta(hours=3)

        return APIResponse(
            success=True,
            message=f"Historical weather data retrieved ({len(historical_data)} records)",
            data={
                "location": {"lat": lat, "lon": lon},
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "weather_data": historical_data
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving historical weather: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=APIResponse)
async def get_weather_alerts(
    region: Optional[str] = Query(
        "global", description="Region for weather alerts")
):
    """
    Get severe weather alerts that might affect transportation.
    """
    try:
        # Mock alerts for now
        alerts = []  # Start with no active alerts

        return APIResponse(
            success=True,
            message=f"Weather alerts retrieved for {region}",
            data={
                "region": region,
                "active_alerts": alerts,
                "last_checked": datetime.utcnow().isoformat(),
                "alert_count": len(alerts)
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving weather alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/impact/{road_id}", response_model=APIResponse)
async def get_weather_impact_on_road(
    road_id: int,
    hours_ahead: int = Query(24, le=72, description="Hours ahead to consider")
):
    """
    Get weather impact assessment for a specific road segment.
    This helps in route optimization by considering weather factors.
    """
    try:
        # Mock weather impact analysis
        impact_assessment = {
            "road_id": road_id,
            "weather_risk_level": "medium",  # low, medium, high
            "visibility_impact": 0.2,  # 0-1 scale
            # 0-1 scale (1.0 = perfect conditions)
            "road_condition_factor": 0.95,
            "visibility_meters": 8500,
            "precipitation_probability": 0.35,
            "recommendations": [
                "Reduce speed limit by 15%",
                "Increase following distance",
                "Monitor weather updates every 30 minutes"
            ]
        }

        return APIResponse(
            success=True,
            message=f"Weather impact assessment for road {road_id}",
            data=impact_assessment
        )

    except Exception as e:
        logger.error(f"Error assessing weather impact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
