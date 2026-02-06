from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import asyncio
from app.services import kg_service

router = APIRouter()

class GraphRequest(BaseModel):
    school: str
    college: str
    major: str
    training_plan_text: Optional[str] = None

class ReportRequest(BaseModel):
    school: str
    major: str
    report_content: Optional[dict] = None

@router.get("/schools/{school}/colleges")
async def get_colleges(school: str):
    # Mock data or fetch from DB/File
    # Ideally should scan the data directory
    return ["自动化学院", "计算机学院", "机械工程学院"]

@router.get("/schools/{school}/colleges/{college}/majors")
async def get_majors(school: str, college: str):
    return ["自动化类", "智能车辆工程", "机器人工程"]

@router.get("/stats")
async def get_stats(major: str):
    return {
        "jobs": 1250,
        "companies": 86,
        "reports": 12,
        "policies": 5
    }

@router.post("/agent/stream-build-graph")
async def stream_build_graph(request: GraphRequest):
    return StreamingResponse(
        kg_service.build_knowledge_graph_stream(
            request.school, 
            request.college, 
            request.major,
            request.training_plan_text
        ),
        media_type="application/x-ndjson"
    )

@router.post("/agent/download-report")
async def download_report(request: ReportRequest):
    # Create a temporary file
    file_path = f"report_{request.school}_{request.major}.docx"
    with open(file_path, "w") as f:
        f.write("Analysis Report\n")
        f.write(json.dumps(request.report_content, indent=2))
    
    return FileResponse(
        path=file_path, 
        filename=f"{request.school}_{request.major}_培养方案改进分析报告.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
