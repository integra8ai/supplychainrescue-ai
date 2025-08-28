"""
Pydantic models/schemas for SupplyChainRescue AI API.
Defines request/response structures for all endpoints.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class StatusEnum(str, Enum):
    """Status enumeration for various components"""
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class WeatherCondition(BaseModel):
    """Weather condition model"""
    main: str = Field(..., description="Main weather condition")
    description: str = Field(..., description="Detailed weather description")
    icon: str = Field(..., description="Weather icon code")


class WeatherData(BaseModel):
    """Weather data model"""
    temperature: float = Field(..., description="Temperature in Celsius")
    temperature_feels_like: float = Field(...,
                                          description="Feels like temperature")
    humidity: int = Field(..., description="Humidity percentage")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    visibility: Optional[int] = Field(None, description="Visibility in meters")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_direction: int = Field(..., description="Wind direction in degrees")
    weather_condition: WeatherCondition
    timestamp: datetime = Field(..., description="Weather data timestamp")


class RoadNode(BaseModel):
    """Road network node model"""
    id: int = Field(..., description="Node ID")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    osm_id: Optional[str] = Field(None, description="OpenStreetMap node ID")


class RoadEdge(BaseModel):
    """Road network edge model"""
    id: int = Field(..., description="Edge ID")
    source_node: int = Field(..., description="Source node ID")
    target_node: int = Field(..., description="Target node ID")
    length: float = Field(..., description="Edge length in meters")
    max_speed: Optional[int] = Field(None, description="Maximum speed limit")
    road_type: Optional[str] = Field(
        None, description="Road type classification")
    geometry: Optional[List[Dict[str, float]]] = Field(
        None, description="Road geometry coordinates")


class RoadClosure(BaseModel):
    """Road closure model"""
    id: int = Field(..., description="Closure ID")
    road_id: int = Field(..., description="Associated road edge ID")
    closure_type: str = Field(...,
                              description="Type of closure (accident, natural_disaster, etc.)")
    description: Optional[str] = Field(None, description="Closure description")
    severity: int = Field(...,
                          description="Severity level (1-5, 5 being most severe)")
    start_time: datetime = Field(..., description="Closure start time")
    estimated_end_time: Optional[datetime] = Field(
        None, description="Estimated resolution time")
    coordinates: List[Dict[str, float]
                      ] = Field(..., description="Closure location coordinates")


class ReliefCenter(BaseModel):
    """Relief center model"""
    id: str = Field(..., description="Center ID")
    name: str = Field(..., description="Center name")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    capacity: int = Field(..., description="Storage capacity")
    available_capacity: int = Field(...,
                                    description="Current available capacity")
    contact_info: Optional[Dict[str, str]] = Field(
        None, description="Contact information")


class LogisticsTruck(BaseModel):
    """Logistics truck model"""
    id: str = Field(..., description="Truck ID")
    capacity: int = Field(..., description="Truck cargo capacity")
    current_location: Dict[str,
                           float] = Field(..., description="Current location (lat, lng)")
    status: StatusEnum = Field(
        StatusEnum.OPEN, description="Truck operational status")
    assigned_route: Optional[str] = Field(
        None, description="Current assigned route ID")


class ForecastPrediction(BaseModel):
    """Weather/delay forecast prediction model"""
    timestamp: datetime = Field(..., description="Prediction timestamp")
    road_id: int = Field(..., description="Road segment ID")
    delay_probability: float = Field(...,
                                     description="Probability of delay (0-1)")
    estimated_delay: float = Field(...,
                                   description="Estimated delay in minutes")
    confidence: float = Field(...,
                              description="Prediction confidence score (0-1)")
    weather_factor: float = Field(..., description="Weather impact factor")
    traffic_factor: float = Field(..., description="Traffic impact factor")


class OptimizationRoute(BaseModel):
    """Optimized route model"""
    route_id: str = Field(..., description="Unique route identifier")
    truck_id: str = Field(..., description="Assigned truck ID")
    nodes: List[Dict[str, float]] = Field(..., description="Route waypoints")
    total_distance: float = Field(...,
                                  description="Total route distance in km")
    estimated_duration: float = Field(...,
                                      description="Estimated travel time in minutes")
    stops: List[Dict[str, Any]] = Field(..., description="Scheduled stops")
    risk_score: float = Field(..., description="Overall route risk score")


class SituationReport(BaseModel):
    """Natural language situation report model"""
    report_id: str = Field(..., description="Report unique identifier")
    timestamp: datetime = Field(..., description="Report generation time")
    affected_area: str = Field(..., description="Geographic area description")
    summary: str = Field(..., description="Executive summary")
    impacted_roads: int = Field(..., description="Number of impacted roads")
    active_closures: int = Field(..., description="Number of active closures")
    weather_situation: str = Field(...,
                                   description="Weather situation description")
    key_recommendations: List[str] = Field(...,
                                           description="Actionable recommendations")
    severity_level: int = Field(...,
                                description="Overall situation severity (1-5)")


# Request Models
class RouteOptimizationRequest(BaseModel):
    """Request model for route optimization"""
    origin: Dict[str, float] = Field(...,
                                     description="Starting point coordinates")
    destinations: List[Dict[str, float]
                       ] = Field(..., description="Destination coordinates")
    trucks: List[LogisticsTruck] = Field(..., description="Available trucks")
    avoid_closures: bool = Field(
        True, description="Whether to avoid road closures")
    optimize_for_weather: bool = Field(
        True, description="Consider weather in optimization")


class WeatherForecastRequest(BaseModel):
    """Request model for weather forecast"""
    latitude: float = Field(..., description="Location latitude")
    longitude: float = Field(..., description="Location longitude")
    hours_ahead: int = Field(24, description="Forecast hours ahead (max 48)")


# Response Models
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field("", description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp")


class PaginatedResponse(APIResponse):
    """Paginated API response"""
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
