"""
Road network API routes for SupplyChainRescue AI.
Provides endpoints for road network data, closures, and status monitoring.
"""
import asyncio
import logging
import requests
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.config import settings
from backend.db.database import get_db
from backend.models.schemas import (
    RoadNode, RoadEdge, RoadClosure, StatusEnum, APIResponse
)
from backend.models.sql_models import RoadNode as SQLRoadNode, RoadEdge as SQLRoadEdge, RoadClosure as SQLRoadClosure

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)

# Helper functions for converting SQLAlchemy objects to dicts


def road_node_to_dict(db_node):
    return {
        "id": db_node.id,
        "latitude": db_node.latitude,
        "longitude": db_node.longitude,
        "osm_id": db_node.osm_id
    }


def road_edge_to_dict(db_edge):
    return {
        "id": db_edge.id,
        "source_node": db_edge.source_node,
        "target_node": db_edge.target_node,
        "length": db_edge.length,
        "max_speed": db_edge.max_speed,
        "road_type": db_edge.road_type,
        "geometry": db_edge.geometry
    }

# CRUD for RoadNode


@router.post("/nodes", response_model=APIResponse)
async def create_road_node(node_data: RoadNode, db: Session = Depends(get_db)):
    """Create a new road node"""
    try:
        db_node = SQLRoadNode(**node_data.dict())
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        return APIResponse(
            success=True,
            message="Road node created successfully",
            data={"node": road_node_to_dict(db_node)}
        )
    except Exception as e:
        logger.error(f"Error creating road node: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}", response_model=APIResponse)
async def get_road_node(node_id: int, db: Session = Depends(get_db)):
    """Get a road node by ID"""
    try:
        db_node = db.query(SQLRoadNode).filter(
            SQLRoadNode.id == node_id).first()
        if not db_node:
            raise HTTPException(status_code=404, detail="Road node not found")
        return APIResponse(
            success=True,
            message="Road node retrieved successfully",
            data={"node": road_node_to_dict(db_node)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving road node: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/nodes/{node_id}", response_model=APIResponse)
async def update_road_node(node_id: int, node_data: RoadNode, db: Session = Depends(get_db)):
    """Update a road node"""
    try:
        db_node = db.query(SQLRoadNode).filter(
            SQLRoadNode.id == node_id).first()
        if not db_node:
            raise HTTPException(status_code=404, detail="Road node not found")
        for key, value in node_data.dict().items():
            setattr(db_node, key, value)
        db.commit()
        db.refresh(db_node)
        return APIResponse(
            success=True,
            message="Road node updated successfully",
            data={"node": road_node_to_dict(db_node)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating road node: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/nodes/{node_id}", response_model=APIResponse)
async def delete_road_node(node_id: int, db: Session = Depends(get_db)):
    """Delete a road node"""
    try:
        db_node = db.query(SQLRoadNode).filter(
            SQLRoadNode.id == node_id).first()
        if not db_node:
            raise HTTPException(status_code=404, detail="Road node not found")
        db.delete(db_node)
        db.commit()
        return APIResponse(
            success=True,
            message="Road node deleted successfully",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting road node: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=APIResponse)
async def roads_health_check():
    """Road network service health check"""
    return APIResponse(
        success=True,
        message="Road network service is operational",
        data={"status": "connected", "network_nodes": 0}
    )


@router.get("/nodes", response_model=APIResponse)
async def get_road_nodes(
    db: Session = Depends(get_db),
    bbox: Optional[str] = Query(
        None, description="Bounding box as 'min_lon,min_lat,max_lon,max_lat'"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Maximum number of nodes to return")
):
    """
    Retrieve road network nodes within a bounding box or default area.
    """
    try:
        query = db.query(SQLRoadNode)
        if bbox:
            min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(','))
            query = query.filter(
                SQLRoadNode.longitude >= min_lon,
                SQLRoadNode.latitude >= min_lat,
                SQLRoadNode.longitude <= max_lon,
                SQLRoadNode.latitude <= max_lat
            )
        nodes = query.limit(limit).all()

        return APIResponse(
            success=True,
            message=f"Retrieved {len(nodes)} road nodes",
            data={"nodes": [road_node_to_dict(node) for node in nodes]}
        )

    except Exception as e:
        logger.error(f"Error retrieving road nodes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edges", response_model=APIResponse)
async def get_road_edges(
    db: Session = Depends(get_db),
    node_ids: Optional[List[int]] = Query(
        None, description="Filter by node IDs"),
    road_type: Optional[str] = Query(None, description="Filter by road type"),
    max_speed: Optional[int] = Query(None, description="Filter by max speed")
):
    """
    Retrieve road network edges with optional filtering.
    """
    try:
        query = db.query(SQLRoadEdge)
        if node_ids:
            query = query.filter(
                (SQLRoadEdge.source_node.in_(node_ids)) |
                (SQLRoadEdge.target_node.in_(node_ids))
            )
        if road_type:
            query = query.filter(SQLRoadEdge.road_type == road_type)
        if max_speed:
            query = query.filter(SQLRoadEdge.max_speed <= max_speed)

        edges = query.all()

        return APIResponse(
            success=True,
            message=f"Retrieved {len(edges)} road edges",
            data={"edges": [road_edge_to_dict(edge) for edge in edges]}
        )

    except Exception as e:
        logger.error(f"Error retrieving road edges: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/closures", response_model=APIResponse)
async def get_road_closures(
    db: Session = Depends(get_db),
    active_only: bool = Query(True, description="Return only active closures"),
    severity_level: Optional[int] = Query(
        None, ge=1, le=5, description="Filter by severity level"),
    limit: int = Query(
        50, ge=1, le=200, description="Maximum number of closures to return")
):
    """
    Retrieve road closures with filtering options.
    """
    try:
        query = db.query(SQLRoadClosure)
        if active_only:
            query = query.filter(
                SQLRoadClosure.start_time <= func.now(),
                (SQLRoadClosure.estimated_end_time.is_(None) |
                 (SQLRoadClosure.estimated_end_time >= func.now()))
            )
        if severity_level:
            query = query.filter(SQLRoadClosure.severity >= severity_level)

        closures = query.limit(limit).all()

        return APIResponse(
            success=True,
            message=f"Retrieved {len(closures)} road closures",
            data={"closures": [closure.dict() for closure in closures]}
        )

    except Exception as e:
        logger.error(f"Error retrieving road closures: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/closures/report", response_model=APIResponse)
async def report_closure(closure_data: RoadClosure, db: Session = Depends(get_db)):
    """
    Report a new road closure.
    This endpoint will be used by field agents or monitoring systems.
    """
    try:
        db_closure = SQLRoadClosure(**closure_data.dict())
        db.add(db_closure)
        db.commit()
        db.refresh(db_closure)

        return APIResponse(
            success=True,
            message="Closure reported successfully",
            data={"closure_reported": True, "closure_id": db_closure.id}
        )

    except Exception as e:
        logger.error(f"Error reporting closure: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{road_id}", response_model=APIResponse)
async def get_road_status(road_id: int, db: Session = Depends(get_db)):
    """
    Get detailed status information for a specific road segment.
    """
    try:
        road_exists = db.query(SQLRoadEdge).filter(
            SQLRoadEdge.id == road_id).first()
        if not road_exists:
            raise HTTPException(
                status_code=404, detail="Road segment not found")

        # Check for active closures on this road
        active_closures = db.query(SQLRoadClosure).filter(
            SQLRoadClosure.road_id == road_id,
            SQLRoadClosure.start_time <= func.now(),
            (SQLRoadClosure.estimated_end_time.is_(None) |
             (SQLRoadClosure.estimated_end_time >= func.now()))
        ).count()

        status_info = {
            "road_id": road_id,
            "status": StatusEnum.CLOSED.value if active_closures > 0 else StatusEnum.OPEN.value,
            "active_closures_count": active_closures,
            "last_updated": datetime.utcnow().isoformat(),
            "traffic_level": "normal",  # Placeholder
            "weather_impact": "low"  # Placeholder
        }

        return APIResponse(
            success=True,
            message=f"Retrieved status for road {road_id}",
            data=status_info
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving road status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=APIResponse)
async def get_road_statistics(db: Session = Depends(get_db)):
    """
    Get overall road network statistics.
    """
    try:
        total_roads = db.query(SQLRoadEdge).count()
        active_closures = db.query(SQLRoadClosure).filter(
            SQLRoadClosure.start_time <= func.now(),
            (SQLRoadClosure.estimated_end_time.is_(None) |
             (SQLRoadClosure.estimated_end_time >= func.now()))
        ).count()

        # Placeholder for roads by status - would require more complex logic
        roads_by_status = {
            "open": total_roads - active_closures,
            "closed": active_closures,
            "partial": 0
        }

        stats = {
            "total_roads": total_roads,
            "active_closures": active_closures,
            "roads_by_status": roads_by_status,
            "coverage_area_km2": 0,  # TODO: Calculate actual coverage
            "last_updated": datetime.utcnow().isoformat()
        }

        return APIResponse(
            success=True,
            message="Road network statistics retrieved",
            data=stats
        )

    except Exception as e:
        logger.error(f"Error retrieving road statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
