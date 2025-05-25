from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from mcp.api.dependencies import get_current_subject
from mcp.db.models.mcp import MCP
from mcp.db.models.review import Review
from mcp.db.session import get_db_session
from mcp.schemas.mcp import MCPListItem

router = APIRouter(prefix="/api/components", tags=["components"])


@router.get("/search")
def search_components(
    type: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    minRating: Optional[int] = None,
    minUsage: Optional[int] = None,
    searchTerm: Optional[str] = None,
    compatibleWith: Optional[str] = Query(
        None,
        description="Component ID to check compatibility with (format: <component_id>:<version>)",
    ),
    requires: Optional[List[str]] = Query(
        None, description="List of component IDs that must be dependencies"
    ),
    author: Optional[str] = None,
    cost: Optional[float] = None,
    compliance: Optional[str] = None,
    sortBy: Optional[str] = Query(None, description="Sort by: rating, usage, newest, name"),
    sortOrder: Optional[str] = Query("desc", description="asc or desc"),
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db_session),
    current_user_sub: str = Depends(get_current_subject),
):
    query = db.query(MCP)
    if type:
        query = query.filter(MCP.type.in_(type))
    if tags:
        for tag in tags:
            query = query.filter(MCP.tags.contains([tag]))
    if minUsage:
        query = query.filter(MCP.usage_count >= minUsage)
    if searchTerm:
        query = query.filter(
            MCP.name.ilike(f"%{searchTerm}%") | MCP.description.ilike(f"%{searchTerm}%")
        )
    if author:
        query = query.filter(MCP.author == author)
    # Advanced filters: cost, compliance (assume in latest_version.definition)
    if cost is not None or compliance:
        filtered_ids = []
        for mcp in query.all():
            latest_version = mcp.current_version or (mcp.versions[-1] if mcp.versions else None)
            if not latest_version:
                continue
            definition = latest_version.definition or {}
            if cost is not None and definition.get("cost", 0) > cost:
                continue
            if compliance and definition.get("compliance") != compliance:
                continue
            filtered_ids.append(mcp.id)
        query = query.filter(MCP.id.in_(filtered_ids))
    # Join with reviews for rating filter
    if minRating:
        subq = (
            db.query(Review.component_id, func.avg(Review.rating).label("avg_rating"))
            .group_by(Review.component_id)
            .subquery()
        )
        query = query.join(subq, MCP.id == subq.c.component_id).filter(
            subq.c.avg_rating >= minRating
        )
    # Compatibility filter
    if compatibleWith:
        try:
            comp_id, comp_version = compatibleWith.split(":")
        except ValueError:
            comp_id, comp_version = compatibleWith, None
        filtered_ids = []
        for mcp in query.all():
            latest_version = mcp.current_version or (mcp.versions[-1] if mcp.versions else None)
            if not latest_version:
                continue
            deps = (latest_version.definition or {}).get("dependencies", [])
            for dep in deps:
                if dep.get("component_id") == comp_id:
                    if not comp_version or dep.get("version") == comp_version:
                        filtered_ids.append(mcp.id)
                        break
        query = query.filter(MCP.id.in_(filtered_ids))
    # Requires filter
    if requires:
        filtered_ids = []
        for mcp in query.all():
            latest_version = mcp.current_version or (mcp.versions[-1] if mcp.versions else None)
            if not latest_version:
                continue
            deps = (latest_version.definition or {}).get("dependencies", [])
            dep_ids = [dep.get("component_id") for dep in deps]
            if all(req in dep_ids for req in requires):
                filtered_ids.append(mcp.id)
        query = query.filter(MCP.id.in_(filtered_ids))
    # Sorting
    if sortBy:
        if sortBy == "usage":
            order_col = MCP.usage_count
        elif sortBy == "name":
            order_col = MCP.name
        elif sortBy == "newest":
            order_col = MCP.updated_at
        elif sortBy == "rating":
            # Sort by average rating (requires join)
            subq = (
                db.query(Review.component_id, func.avg(Review.rating).label("avg_rating"))
                .group_by(Review.component_id)
                .subquery()
            )
            query = query.outerjoin(subq, MCP.id == subq.c.component_id)
            order_col = subq.c.avg_rating
        else:
            order_col = None
        if order_col is not None:
            if sortOrder == "asc":
                query = query.order_by(order_col.asc().nullslast())
            else:
                query = query.order_by(order_col.desc().nullslast())
    total = query.count()
    results = query.offset((page - 1) * pageSize).limit(pageSize).all()
    # Facets
    type_counts = dict(db.query(MCP.type, func.count()).group_by(MCP.type).all())
    tag_counts = {}
    for mcp in db.query(MCP).all():
        for tag in mcp.tags or []:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Format response: include version and dependency info
    def mcp_to_dict(mcp):
        latest_version = mcp.current_version or (mcp.versions[-1] if mcp.versions else None)
        dependencies = []
        version = None
        cost_val = None
        compliance_val = None
        if latest_version:
            definition = latest_version.definition or {}
            dependencies = definition.get("dependencies", [])
            version = latest_version.version
            cost_val = definition.get("cost")
            compliance_val = definition.get("compliance")
        item = MCPListItem.model_validate(mcp).model_dump()
        item["version"] = version
        item["dependencies"] = dependencies
        item["cost"] = cost_val
        item["compliance"] = compliance_val
        return item

    components = [mcp_to_dict(mcp) for mcp in results]
    return {
        "components": components,
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "facets": {
            "types": type_counts,
            "tags": tag_counts,
        },
    }
