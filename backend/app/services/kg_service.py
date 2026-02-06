import json
import asyncio
import random
import os

async def build_knowledge_graph_stream(school: str, college: str, major: str, plan_text: str = None):
    """
    Simulates the graph building process with streaming updates.
    """
    
    # Step 1: Data Collection
    yield json.dumps({"step_id": 1, "message": f"正在从 {school} - {college} 获取数据..."}) + "\n"
    await asyncio.sleep(0.5)
    yield json.dumps({"step_id": 2, "message": "已获取就业市场数据与行业趋势报告"}) + "\n"
    await asyncio.sleep(0.5)

    # Step 2: Knowledge Extraction
    yield json.dumps({"step_id": 3, "message": "正在分析培养方案与岗位需求..."}) + "\n"
    await asyncio.sleep(0.8)
    yield json.dumps({"step_id": 4, "message": "提取关键能力实体与关系..."}) + "\n"
    await asyncio.sleep(0.8)

    # Step 3: Graph Construction
    yield json.dumps({"step_id": 5, "message": "构建知识图谱节点..."}) + "\n"
    await asyncio.sleep(0.5)
    yield json.dumps({"step_id": 6, "message": "生成实体关系连接..."}) + "\n"
    await asyncio.sleep(0.5)

    # Step 4: Finalize
    yield json.dumps({"step_id": 7, "message": "图谱生成完毕"}) + "\n"
    
    # Load mock graph or generate one
    graph_data = generate_mock_graph(major)
    yield json.dumps({"step_id": 7, "data": graph_data}) + "\n"

def generate_mock_graph(major_name):
    # This is a fallback if the actual file isn't found
    return {
        "entities": [
            {"id": f"major_{major_name}", "name": major_name, "type": "Major", "category": "Core", "x": 0, "y": 0},
            {"id": "cap_coding", "name": "编程能力", "type": "Capability", "category": "Capability", "x": 50, "y": 50},
            {"id": "cap_design", "name": "系统设计", "type": "Capability", "category": "Capability", "x": -50, "y": 50},
            {"id": "job_engineer", "name": "研发工程师", "type": "Job", "category": "Target", "x": 0, "y": 100}
        ],
        "relationships": [
            {"head": f"major_{major_name}", "tail": "cap_coding", "type": "REQUIRES"},
            {"head": f"major_{major_name}", "tail": "cap_design", "type": "REQUIRES"},
            {"head": "cap_coding", "tail": "job_engineer", "type": "ENABLES"}
        ]
    }
