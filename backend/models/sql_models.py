"""
SQLAlchemy models for SupplyChainRescue AI database.
These models correspond to the Pydantic schemas defined in schemas.py.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from backend.models.schemas import StatusEnum  # Import the enum

Base = declarative_base()

class RoadNode(Base):
    __tablename__ = "road_nodes"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    osm_id = Column(String, nullable=True)

    # Relationships
    source_edges = relationship("RoadEdge", foreign_keys="[RoadEdge.source_node]", back_populates="source")
    target_edges = relationship("RoadEdge", foreign_keys="[RoadEdge.target_node]", back_populates="target")


class RoadEdge(Base):
    __tablename__ = "road_edges"

    id = Column(Integer, primary_key=True, index=True)
    source_node = Column(Integer, ForeignKey("road_nodes.id"), nullable=False)
    target_node = Column(Integer, ForeignKey("road_nodes.id"), nullable=False)
    length = Column(Float, nullable=False)
    max_speed = Column(Integer, nullable=True)
    road_type = Column(String, nullable=True)
    geometry = Column(JSON, nullable=True)  # List of [lat, lng] tuples

    # Relationships
    source = relationship("RoadNode", foreign_keys=[source_node], back_populates="source_edges")
    target = relationship("RoadNode", foreign_keys=[target_node], back_populates="target_edges")
    closures = relationship("RoadClosure", back_populates="road")


class RoadClosure(Base):
    __tablename__ = "road_closures"

    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(Integer, ForeignKey("road_edges.id"), nullable=False)
    closure_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    estimated_end_time = Column(DateTime, nullable=True)
    coordinates = Column(JSON, nullable=False)  # List of [lat, lng] dicts

    # Relationships
    road = relationship("RoadEdge", back_populates="closures")


class ReliefCenter(Base):
    __tablename__ = "relief_centers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    available_capacity = Column(Integer, nullable=False)
    contact_info = Column(JSON, nullable=True)


class LogisticsTruck(Base):
    __tablename__ = "logistics_trucks"

    id = Column(String, primary_key=True, index=True)
    capacity = Column(Integer, nullable=False)
    current_location = Column(JSON, nullable=False)  # {"lat": float, "lng": float}
    status = Column(SQLEnum(StatusEnum), nullable=False)
    assigned_route = Column(String, nullable=True)  # Could FK to OptimizationRoute.route_id, but keeping as is


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    temperature_feels_like = Column(Float, nullable=False)
    humidity = Column(Integer, nullable=False)
    pressure = Column(Integer, nullable=False)
    visibility = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=False)
    wind_direction = Column(Integer, nullable=False)
    weather_condition = Column(JSON, nullable=False)  # WeatherCondition as dict
    timestamp = Column(DateTime, nullable=False)


class ForecastPrediction(Base):
    __tablename__ = "forecast_predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    road_id = Column(Integer, ForeignKey("road_edges.id"), nullable=False)
    delay_probability = Column(Float, nullable=False)
    estimated_delay = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    weather_factor = Column(Float, nullable=False)
    traffic_factor = Column(Float, nullable=False)

    # Relationships
    road = relationship("RoadEdge")


class OptimizationRoute(Base):
    __tablename__ = "optimization_routes"

    route_id = Column(String, primary_key=True, index=True)
    truck_id = Column(String, ForeignKey("logistics_trucks.id"), nullable=False)
    nodes = Column(JSON, nullable=False)  # List of [lat, lng] dicts
    total_distance = Column(Float, nullable=False)
    estimated_duration = Column(Float, nullable=False)
    stops = Column(JSON, nullable=False)  # List of stop dicts
    risk_score = Column(Float, nullable=False)

    # Relationships
    truck = relationship("LogisticsTruck")


class SituationReport(Base):
    __tablename__ = "situation_reports"

    report_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    affected_area = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    impacted_roads = Column(Integer, nullable=False)
    active_closures = Column(Integer, nullable=False)
    weather_situation = Column(Text, nullable=False)
    key_recommendations = Column(JSON, nullable=False)  # List of strings
    severity_level = Column(Integer, nullable=False)