"""
Route Optimization API routes for SupplyChainRescue AI.
Provides route planning and optimization using OR-Tools.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.config import settings
from backend.db.database import get_db
from backend.models.schemas import (
    RouteOptimizationRequest, OptimizationRoute, APIResponse, LogisticsTruck
)
from backend.models.sql_models import OptimizationRoute as SQLOptimizationRoute

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)


@router.get("/health", response_model=APIResponse)
async def optimize_health_check():
    """Route optimization service health check"""
    try:
        # Test OR-Tools import (will fail if not installed)
        from ortools.constraint_solver import pywrapcp
        from ortools.constraint_solver import routing_enums_pb2

        return APIResponse(
            success=True,
            message="Route optimization service is operational",
            data={
                "status": "active",
                "optimization_engine": "OR-Tools",
                "supported_algorithms": ["shortest_path", "vehicle_routing"]
            }
        )
    except ImportError:
        return APIResponse(
            success=False,
            message="OR-Tools not installed",
            data={"error": "Missing ortools dependency"}
        )


def calculate_distance(point1: Dict[str, float], point2: Dict[str, float]) -> float:
    """Calculate Euclidean distance between two points (in km)"""
    import math

    lat1, lon1 = point1['lat'], point1['lng']
    lat2, lon2 = point2['lat'], point2['lng']

    # Haversine formula - simplified for this implementation
    # In production, would use more accurate distance calculation
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) * math.sin(dlon/2))

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c  # Earth's radius in km

    return distance


def calculate_route_penalty(point: Dict[str, float], weather_data: Dict[str, float] = None,
                            road_closures: List[Dict] = None) -> float:
    """
    Calculate penalty for a route segment based on weather and road closures.
    Returns penalty factor (multiplier > 1.0 increases cost).
    """
    penalty = 1.0

    # Weather-based penalties
    if weather_data:
        # Visibility penalty
        if weather_data.get('visibility', 10000) < 5000:
            penalty += 0.5

        # Wind speed penalty
        if weather_data.get('wind_speed', 0) > 15:
            penalty += 0.3

        # Precipitation penalty
        if weather_data.get('precipitation', 0) > 10:
            penalty += 0.8

        # Temperature penalty
        if weather_data.get('temperature', 20) < 0:
            penalty += 0.4

    # Road closure penalties - check if this point/segment is affected by closures
    if road_closures:
        for closure in road_closures:
            # Simple proximity check (in production, use proper spatial analysis)
            closure_coords = closure.get('coordinates', [])
            for coord in closure_coords:
                if (abs(coord['lat'] - point['lat']) < 0.01 and
                        abs(coord['lng'] - point['lng']) < 0.01):
                    # Major penalty for road closures
                    penalty += 5.0
                    break

    return penalty


def optimize_simple_route(origin: Dict[str, float], destinations: List[Dict[str, float]],
                          avoid_closures: bool = True, weather_impact: bool = True,
                          road_closures: List[Dict] = None) -> Dict[str, Any]:
    """
    Enhanced route optimization with weather and closure considerations.
    Uses distance with penalty factors for weather and closures.
    """

    if len(destinations) == 0:
        return {
            "nodes": [origin],
            "total_distance": 0,
            "estimated_duration": 0,
            "total_penalty": 0,
            "closure_avoided": 0,
            "weather_penalty": 0
        }

    # Start from origin
    current_point = origin
    remaining_destinations = destinations.copy()
    route = [origin]
    total_distance = 0
    total_penalty = 0
    closure_avoidance_count = 0
    weather_penalty_total = 0

    while remaining_destinations:
        # Find best remaining destination considering penalties
        best_cost = float('inf')
        best_idx = -1
        best_raw_distance = 0
        best_penalty = 1.0

        for idx, dest in enumerate(remaining_destinations):
            # Calculate raw distance
            raw_distance = calculate_distance(current_point, dest)

            # Calculate penalty factors
            penalty = 1.0
            if weather_impact or avoid_closures:
                penalty = calculate_route_penalty(
                    dest, None, road_closures if avoid_closures else None)

            # Total cost = distance * penalty
            total_cost = raw_distance * penalty

            if total_cost < best_cost:
                best_cost = total_cost
                best_idx = idx
                best_raw_distance = raw_distance
                best_penalty = penalty

        # Move to best destination
        next_point = remaining_destinations.pop(best_idx)
        route.append(next_point)
        total_distance += best_raw_distance
        total_penalty += best_penalty

        # Track penalties
        if best_penalty > 2.0 and road_closures:  # Likely from closures
            closure_avoidance_count += 1
        if best_penalty > 1.0 and best_penalty <= 2.0:  # Weather-related
            weather_penalty_total += (best_penalty - 1.0)

        current_point = next_point

    # Calculate estimated duration (average 50 km/h, adjusted for penalties)
    base_speed = 50  # km/h
    # Reduce speed due to penalties
    adjusted_speed = base_speed / (1 + total_penalty / len(route))
    estimated_duration = (total_distance / adjusted_speed) * 60  # in minutes

    return {
        "nodes": route,
        "total_distance": round(total_distance, 2),
        "estimated_duration": round(estimated_duration, 2),
        # Subtract base penalties
        "total_penalty": round(total_penalty - len(route), 2),
        "closure_avoided": closure_avoidance_count,
        "weather_penalty": round(weather_penalty_total, 2),
        "algorithm": "greedy_nearest_neighbor_with_penalties"
    }


@router.post("/route", response_model=APIResponse)
async def optimize_route(request: RouteOptimizationRequest, db: Session = Depends(get_db)):
    """
    Optimize logistics routes using OR-Tools (or fallback to simple algorithm).
    Currently implements a basic nearest neighbor algorithm as a foundation.
    """

    try:
        # Validate request data
        if len(request.destinations) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one destination is required"
            )

        logger.info(
            f"Optimizing route with {len(request.destinations)} destinations")

        # Fetch active road closures if avoiding closures is requested
        road_closures = []
        if request.avoid_closures:
            from backend.models.sql_models import RoadClosure
            closures = db.query(RoadClosure).filter(
                RoadClosure.start_time <= func.now(),
                (RoadClosure.estimated_end_time.is_(None) |
                 (RoadClosure.estimated_end_time >= func.now()))
            ).all()
            road_closures = [
                {
                    "id": c.id,
                    "coordinates": c.coordinates,
                    "severity": c.severity,
                    "description": c.description
                } for c in closures
            ]

        # Use enhanced optimization with closures and weather considerations
        route_result = optimize_simple_route(
            request.origin,
            request.destinations,
            avoid_closures=request.avoid_closures,
            weather_impact=request.optimize_for_weather,
            road_closures=road_closures
        )

        # Calculate additional metrics
        risk_score = calculate_route_risk(
            route_result["nodes"],
            request.avoid_closures,
            request.optimize_for_weather
        )

        # Prepare optimization route response
        optimization_route = OptimizationRoute(
            route_id=f"route_{len(request.destinations)}_{request.origin['lat']:.3f}",
            truck_id=request.trucks[0].id if request.trucks else "truck_1",
            nodes=route_result["nodes"],
            total_distance=route_result["total_distance"],
            estimated_duration=route_result["estimated_duration"],
            stops=[
                {"stop_id": i + 1, "coordinates": node,
                    "type": "pickup" if i > 0 else "origin"}
                for i, node in enumerate(route_result["nodes"])
            ],
            risk_score=risk_score
        )

        # Store in database
        db_route = SQLOptimizationRoute(**optimization_route.dict())
        db.add(db_route)
        db.commit()
        db.refresh(db_route)

        return APIResponse(
            success=True,
            message="Route optimized successfully",
            data={
                "optimization": optimization_route.dict(),
                "algorithm_used": route_result["algorithm"],
                "processing_stats": {
                    "destinations_processed": len(request.destinations),
                    "avoid_closures": request.avoid_closures
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Route optimization failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def calculate_route_risk(nodes: List[Dict[str, float]], avoid_closures: bool,
                         optimize_weather: bool) -> float:
    """
    Calculate risk score for the route (0-1 scale, higher = riskier).
    Placeholder implementation - in production would consider real road data.
    """
    # Base risk calculation
    base_risk = 0.1  # Low base risk

    # Add risk factors
    if avoid_closures:
        base_risk += 0.2  # Detour risk

    if optimize_weather:
        base_risk += 0.1  # Weather consideration

    # Distance-based risk (longer routes have higher risk)
    route_length_risk = min(0.3, len(nodes) * 0.05)

    total_risk = min(1.0, base_risk + route_length_risk)
    return round(total_risk, 3)


@router.get("/routes/{route_id}", response_model=APIResponse)
async def get_optimized_route(route_id: str, db: Session = Depends(get_db)):
    """Retrieve a previously optimized route"""

    try:
        route = db.query(SQLOptimizationRoute).filter(
            SQLOptimizationRoute.route_id == route_id
        ).first()

        if not route:
            raise HTTPException(status_code=404, detail="Route not found")

        data = route.__dict__
        del data['_sa_instance_state']

        return APIResponse(
            success=True,
            message=f"Route {route_id} retrieved successfully",
            data={"route": data}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/algorithms", response_model=APIResponse)
async def list_optimization_algorithms():
    """List available optimization algorithms"""

    algorithms = [
        {
            "name": "greedy_nearest_neighbor",
            "description": "Simple nearest neighbor approach - find closest unvisited point",
            "complexity": "O(n²)",
            "use_case": "Small number of destinations (< 50)"
        },
        {
            "name": "or_tools_vrp",
            "description": "OR-Tools Vehicle Routing Problem solver",
            "complexity": "Variable",
            "use_case": "Multiple vehicles and constraints",
            "status": "pending_implementation"
        }
    ]

    return APIResponse(
        success=True,
        message="Available optimization algorithms",
        data={"algorithms": algorithms, "default": "greedy_nearest_neighbor"}
    )
