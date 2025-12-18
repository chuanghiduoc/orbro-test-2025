"""API - FastAPI REST endpoints for Tag management."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from db import db

app = FastAPI(title="RTLS Tag Management API", version="1.0.0")


class TagRegisterRequest(BaseModel):
    id: str
    description: str


class TagResponse(BaseModel):
    id: str
    description: str
    last_cnt: Optional[int] = None
    last_seen: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str


@app.post("/tags", response_model=TagResponse)
def register_tag(request: TagRegisterRequest):
    """Đăng ký Tag mới."""
    if db.is_tag_registered(request.id):
        raise HTTPException(status_code=400, detail="Tag already registered")

    db.register_tag(request.id, request.description)

    return TagResponse(
        id=request.id,
        description=request.description,
        last_cnt=None,
        last_seen=None
    )


@app.get("/tags", response_model=List[TagResponse])
def get_all_tags():
    """Lấy danh sách tất cả Tag đã đăng ký."""
    tags = db.get_all_tags()
    return [TagResponse(**tag) for tag in tags]


@app.get("/tag/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: str):
    """Tra cứu thông tin chi tiết của một Tag."""
    tag = db.get_tag_status(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagResponse(**tag)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Kiểm tra trạng thái hệ thống."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )
