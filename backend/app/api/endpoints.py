from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Dict
import asyncio
import random
import os
import io
import docx
from app.services.kg_service import kg_service
from app.services.data_loader import data_loader

router = APIRouter()

# Load real hierarchy data from CSVs
try:
    HIERARCHY_DATA = data_loader.get_hierarchy()
    print(f"Loaded {len(HIERARCHY_DATA)} schools from data.")
except Exception as e:
    print(f"Error loading hierarchy data: {e}")
    HIERARCHY_DATA = {}

# Fallback Mock Data if data loading fails or is empty
CQUPT_DATA = {
    "通信与信息工程学院": ["通信工程", "电子信息工程", "广播电视工程", "数字媒体技术", "智能电网信息工程", "物联网工程"],
    "计算机科学与技术学院": ["计算机科学与技术", "数据科学与大数据技术", "信息安全", "智能科学与技术", "空间信息与数字技术", "地理空间信息工程"],
    "自动化学院": ["自动化", "测控技术与仪器", "电气工程及其自动化", "机械设计制造及其自动化", "智能车辆工程", "机器人工程"],
    "光电工程学院": ["光电信息科学与工程", "电子科学与技术", "电磁场与无线技术", "微电子科学与工程", "集成电路设计与集成系统"],
    "软件工程学院": ["软件工程"],
    "生物信息学院": ["生物医学工程", "生物信息学"],
    "理学院": ["信息与计算科学", "应用物理学", "数学与应用数学"],
    "经济管理学院": ["信息管理与信息系统", "工程管理", "工商管理", "会计学", "市场营销", "经济学", "电子商务"],
    "传媒艺术学院": ["广播电视编导", "动画", "数字媒体艺术", "网络与新媒体"],
    "外国语学院": ["英语", "翻译"],
    "国际半导体学院": ["微电子科学与工程", "集成电路设计与集成系统"],
    "先进制造工程学院": ["机械设计制造及其自动化", "智能制造工程"],
    "网络空间安全与信息法学院": ["信息安全", "网络空间安全", "法学", "知识产权"],
    "体育学院": ["社会体育指导与管理"],
    "马克思主义学院": [] 
}
# Merge fallback if empty
if "重庆邮电大学" not in HIERARCHY_DATA:
    HIERARCHY_DATA["重庆邮电大学"] = {}

# Update with the new data
HIERARCHY_DATA["重庆邮电大学"].update(CQUPT_DATA)

@router.get("/schools", response_model=List[str])
async def get_schools():
    """
    Get list of available schools.
    """
    return sorted(list(HIERARCHY_DATA.keys()))

@router.get("/schools/{school_name}/colleges", response_model=List[str])
async def get_colleges(school_name: str):
    """
    Get list of colleges for a specific school.
    """
    if school_name not in HIERARCHY_DATA:
        raise HTTPException(status_code=404, detail="School not found")
    return sorted(list(HIERARCHY_DATA[school_name].keys()))

@router.get("/schools/{school_name}/colleges/{college_name}/majors", response_model=List[str])
async def get_majors(school_name: str, college_name: str):
    """
    Get list of majors for a specific college in a school.
    """
    if school_name not in HIERARCHY_DATA:
        raise HTTPException(status_code=404, detail="School not found")
    if college_name not in HIERARCHY_DATA[school_name]:
        raise HTTPException(status_code=404, detail="College not found")
    return sorted(HIERARCHY_DATA[school_name][college_name])

@router.get("/stats")
async def get_stats(major: str = Query(..., description="Major name to generate stats for")):
    """
    Get generated stats for a specific major (Using real data from DataLoader where possible).
    """
    # 1. Get Real Job & Company Data
    jobs = data_loader.search_jobs_by_major(major, limit=None)
    job_count = len(jobs)
    
    unique_companies = set()
    for j in jobs:
        if j.get('单位名称'):
            unique_companies.add(j['单位名称'])
    company_count = len(unique_companies)

    # 2. Mock Reports & Policies (Since we don't have a real doc store for these yet)
    # But we make them stable based on major hash
    base_hash = sum(ord(char) for char in major)
    report_count = int((base_hash * 7) % 30) + 5
    policy_count = int((base_hash * 3) % 20) + 5
    
    return {
        "jobs": f"相关就业岗位{job_count}个",
        "companies": f"相关企业{company_count}家",
        "reports": f"行业发展报告{report_count}个",
        "policies": f"政策文件{policy_count}个"
    }

@router.post("/agent/build-graph")
async def build_knowledge_graph(
    school: str = Body(..., embed=True), 
    college: str = Body(..., embed=True), 
    major: str = Body(..., embed=True)
):
    """
    Trigger the Knowledge Graph construction process.
    """
    # 1. Start the KG extraction process (Simulated async task)
    kg_data = await kg_service.build_graph_for_major(school, college, major)
    
    # 2. Return the execution plan (Frontend visualization)
    return {
        "status": "started",
        "message": f"Started building knowledge graph for {school} - {college} - {major}",
        "kg_preview": kg_data, # Return the extracted data for preview
        "initial_plan": [
            {"id": 1, "content": f"用户选择专业: {major}", "status": "completed", "time": "10ms"},
            {"id": 2, "content": f"启动 {school} 知识图谱构建任务...", "status": "running", "time": "50ms"},
            {"id": 3, "content": f"读取人才培养方案文本...", "status": "pending", "time": "..."},
            {"id": 4, "content": f"LLM 实体抽取 (Prompt: training_plan_kg_prompt.yaml)...", "status": "pending", "time": "..."},
            {"id": 5, "content": f"识别实体: {len(kg_data['entities'])} 个 (课程, 技能, 岗位)...", "status": "pending", "time": "..."},
            {"id": 6, "content": f"构建关系: {len(kg_data['relationships'])} 条...", "status": "pending", "time": "..."},
            {"id": 7, "content": "生成能力素质图谱节点...", "status": "pending", "time": "..."},
            {"id": 8, "content": "写入图数据库 (Neo4j)...", "status": "pending", "time": "..."},
            {"id": 9, "content": "可视化渲染准备就绪。", "status": "pending", "time": "..."}
        ]
    }

@router.post("/agent/stream-build-graph")
async def stream_build_graph(
    school: str = Body(..., embed=True), 
    college: str = Body(..., embed=True), 
    major: str = Body(..., embed=True)
):
    """
    Stream the KG construction process with real-time updates using Server-Sent Events (SSE) compatible format.
    """
    return StreamingResponse(
        kg_service.build_graph_for_major_stream(school, college, major),
        media_type="application/x-ndjson"
    )

@router.post("/agent/analyze")
async def analyze_graph(
    school: str = Body(..., embed=True),
    college: str = Body(..., embed=True),
    major: str = Body(..., embed=True),
    graph_data: Dict = Body(..., embed=True),
    training_plan_text: str = Body(None, embed=True),
    stats_data: Dict = Body(None, embed=True)
):
    """
    Generate an improvement analysis report based on the knowledge graph.
    """
    report = await kg_service.analyze_graph_improvement(school, college, major, graph_data, training_plan_text, stats_data)
    return {"report": report}

@router.post("/agent/download-report")
async def download_report(
    school: str = Body(..., embed=True),
    major: str = Body(..., embed=True),
    report_content: str = Body(..., embed=True)
):
    """
    Generate and download the DOCX report.
    """
    file_path = kg_service.generate_improvement_docx(school, major, report_content)
    
    # Ensure file exists
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Failed to generate report file")
        
    return FileResponse(
        path=file_path, 
        filename=os.path.basename(file_path),
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

@router.post("/agent/upload/parse")
async def parse_training_plan(file: UploadFile = File(...)):
    """
    Parse uploaded training plan file (docx, txt, md) and return text content.
    """
    content = ""
    filename = file.filename.lower()
    
    try:
        if filename.endswith(".docx"):
            # Read file into memory
            file_content = await file.read()
            doc = docx.Document(io.BytesIO(file_content))
            # Extract text from paragraphs
            content = "\n".join([para.text for para in doc.paragraphs])
            
        elif filename.endswith(".txt") or filename.endswith(".md"):
            content_bytes = await file.read()
            try:
                content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = content_bytes.decode("gbk", errors="ignore")
                
        else:
            # Fallback for other files (PDF not supported yet without extra libs)
            return {"filename": file.filename, "content": f"[System] 文件 {file.filename} 上传成功，但目前仅支持 .docx/.txt/.md 文本内容提取。"}
            
        if not content.strip():
             return {"filename": file.filename, "content": f"[System] 文件 {file.filename} 上传成功，但内容似乎为空或无法提取。"}

        return {"filename": file.filename, "content": content}
        
    except Exception as e:
        print(f"Error parsing file: {e}")
        return {"filename": file.filename, "content": f"[System] 文件解析失败: {str(e)}", "error": str(e)}
