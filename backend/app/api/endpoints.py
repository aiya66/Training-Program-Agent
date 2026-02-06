from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import asyncio
import tempfile
import re
from urllib.parse import quote
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
    return ["自动化学院", "计算机学院", "机械工程学院", "招生与就业工作处"]

@router.get("/schools/{school}/colleges/{college}/majors")
async def get_majors(school: str, college: str):
    return ["自动化类", "智能车辆工程", "机器人工程", "中药学", "信息与通信工程", "软件工程"]

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

def sanitize_filename(name: str) -> str:
    # Replace invalid filename characters with underscore
    return re.sub(r'[<>:"/\\|?*]', '_', name)

@router.post("/agent/download-report")
async def download_report(request: ReportRequest):
    try:
        # Sanitize filenames
        safe_school = sanitize_filename(request.school)
        safe_major = sanitize_filename(request.major)
        
        # Create a temporary file
        # delete=False is required for Windows to allow opening the file again in FileResponse
        # We rely on BackgroundTask or OS cleanup, but here we just leave it for simplicity
        # Ideally, use a custom cleanup or BackgroundTask
        
        fd, file_path = tempfile.mkstemp(suffix=".docx", prefix=f"report_{safe_school}_{safe_major}_")
        os.close(fd)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Analysis Report\n")
                f.write("================\n\n")
                if request.report_content:
                    f.write(json.dumps(request.report_content, indent=2, ensure_ascii=False))
                else:
                    f.write("No report content available.")
        except Exception as e:
            os.unlink(file_path)
            raise e

        filename = f"{safe_school}_{safe_major}_培养方案改进分析报告.docx"
        
        # Use quote to handle non-ASCII characters in filename header
        encoded_filename = quote(filename)
        
        return FileResponse(
            path=file_path, 
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"
            }
        )
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Failed to generate report: {str(e)}"}
        )
