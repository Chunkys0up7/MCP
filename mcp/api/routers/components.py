from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from mcp.db.session import get_db_session
from mcp.db.models.mcp import MCP
from mcp.db.models.review import Review
from mcp.schemas.mcp import MCPListItem
from mcp.api.dependencies import get_current_subject
from sqlalchemy import func

router = APIRouter(prefix="/api/components", tags=["components"])

@router.get("/search")
def search_components(
    type: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    minRating: Optional[int] = None,
    minUsage: Optional[int] = None,
    searchTerm: Optional[str] = None,
    compatibleWith: Optional[str] = Query(None, description="Component ID to check compatibility with (format: <component_id>:<version>)"),
    requires: Optional[List[str]] = Query(None, description="List of component IDs that must be dependencies"),
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
        query = query.filter(MCP.name.ilike(f"%{searchTerm}%") | MCP.description.ilike(f"%{searchTerm}%"))
    # Join with reviews for rating filter
    if minRating:
        subq = db.query(Review.component_id, func.avg(Review.rating).label("avg_rating")).group_by(Review.component_id).subquery()
        query = query.join(subq, MCP.id == subq.c.component_id).filter(subq.c.avg_rating >= minRating)
    # Compatibility filter
    if compatibleWith:
        # Format: <component_id>:<version>
        try:
            comp_id, comp_version = compatibleWith.split(":")
        except ValueError:
            comp_id, comp_version = compatibleWith, None
        # Only include MCPs whose latest version's dependencies include the given component_id (and version if specified)
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
    total = query.count()
    results = query.offset((page-1)*pageSize).limit(pageSize).all()
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
        if latest_version:
            dependencies = (latest_version.definition or {}).get("dependencies", [])
            version = latest_version.version
        item = MCPListItem.model_validate(mcp).model_dump()
        item["version"] = version
        item["dependencies"] = dependencies
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