from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Any, Union
import json
import os
import asyncio
import tempfile
from app.services import kg_service
from docx import Document
from starlette.background import BackgroundTask

router = APIRouter()

class GraphRequest(BaseModel):
    school: str
    college: str
    major: str
    training_plan_text: Optional[str] = None

class AnalyzeRequest(BaseModel):
    school: str
    college: str
    major: str
    graph_data: Optional[dict] = None
    training_plan_text: Optional[str] = None
    stats_data: Optional[dict] = None

class ReportRequest(BaseModel):
    school: str
    major: str
    report_content: Optional[Union[str, dict]] = None

@router.get("/schools/{school}/colleges")
async def get_colleges(school: str):
    return ["自动化学院", "计算机学院", "机械工程学院", "经济管理学院"]

@router.get("/schools/{school}/colleges/{college}/majors")
async def get_majors(school: str, college: str):
    return ["自动化类", "智能车辆工程", "机器人工程", "软件工程", "计算机科学与技术"]

@router.get("/stats")
async def get_stats(major: str):
    return {
        "jobs": "1250+",
        "companies": "86家",
        "reports": "12份",
        "policies": "5份"
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

@router.post("/agent/analyze")
async def analyze_training_plan(request: AnalyzeRequest):
    report = await kg_service.analyze_training_plan(
        request.school,
        request.major,
        request.graph_data,
        request.training_plan_text
    )
    return {"report": report}

@router.post("/agent/download-report")
async def download_report(request: ReportRequest):
    try:
        # Create a real DOCX file
        document = Document()
        document.add_heading(f'{request.school} - {request.major} 培养方案改进分析报告', 0)
        
        content = request.report_content
        if isinstance(content, str):
            # Parse markdown-like string to paragraphs
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('### '):
                    document.add_heading(line.replace('### ', ''), level=3)
                elif line.startswith('## '):
                    document.add_heading(line.replace('## ', ''), level=2)
                elif line.startswith('# '):
                    document.add_heading(line.replace('# ', ''), level=1)
                elif line.startswith('**') and line.endswith('**'):
                    p = document.add_paragraph()
                    run = p.add_run(line.replace('**', ''))
                    run.bold = True
                elif line.startswith('- '):
                    document.add_paragraph(line.replace('- ', ''), style='List Bullet')
                else:
                    document.add_paragraph(line)
        elif isinstance(content, dict):
             document.add_paragraph(json.dumps(content, indent=2, ensure_ascii=False))
        else:
             document.add_paragraph("暂无分析内容")

        # Save to a temporary file
        # Use tempfile to create a unique file in the system temp directory
        fd, file_path = tempfile.mkstemp(suffix=".docx")
        os.close(fd) # Close the file descriptor, we'll write via Document.save
        
        document.save(file_path)
        
        # Clean up file after sending
        def cleanup_file():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up file {file_path}: {e}")

        return FileResponse(
            path=file_path, 
            filename=f"{request.school}_{request.major}_培养方案改进分析报告.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            background=BackgroundTask(cleanup_file)
        )
    except Exception as e:
        print(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
