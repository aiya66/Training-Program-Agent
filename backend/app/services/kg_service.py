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
    return {
        "entities": [
            {"id": f"major_{major_name}", "name": major_name, "type": "Major", "category": "Core", "x": 0, "y": 0},
            {"id": "cap_coding", "name": "编程能力", "type": "Capability", "category": "Capability", "x": 50, "y": 50},
            {"id": "cap_design", "name": "系统设计", "type": "Capability", "category": "Capability", "x": -50, "y": 50},
            {"id": "job_engineer", "name": "研发工程师", "type": "Job", "category": "Target", "x": 0, "y": 100},
             {"id": "job_pm", "name": "产品经理", "type": "Job", "category": "Target", "x": 20, "y": 120}
        ],
        "relationships": [
            {"head": f"major_{major_name}", "tail": "cap_coding", "type": "REQUIRES"},
            {"head": f"major_{major_name}", "tail": "cap_design", "type": "REQUIRES"},
            {"head": "cap_coding", "tail": "job_engineer", "type": "ENABLES"},
             {"head": "cap_design", "tail": "job_pm", "type": "ENABLES"}
        ]
    }

async def analyze_training_plan(school: str, major: str, graph_data: dict, training_plan_text: str = None):
    """
    Generates a mock analysis report.
    """
    await asyncio.sleep(2) # Simulate LLM thinking
    
    return f"""
# {school} {major} 专业培养方案改进分析报告

## 1. 现状评估
当前 {major} 专业的培养方案在基础理论教学方面较为扎实，涵盖了核心学科知识。
知识图谱分析显示，现有课程体系与 "研发工程师"、"产品经理" 等目标岗位的核心能力匹配度达到 75%。

## 2. 存在的问题
- **实践环节不足**：虽然理论课程丰富，但与企业实际项目结合的实训课程比例偏低。
- **新技术更新滞后**：部分课程内容未及时涵盖行业最新的 AI 与大数据技术应用。
- **跨学科能力培养较弱**：缺乏与管理学、设计学等相关学科的交叉融合课程。

## 3. 改进建议
### 3.1 课程体系优化
- 增设《人工智能应用实战》、《跨平台系统架构》等前沿技术课程。
- 引入企业导师，开展 "校企双导师制" 的项目实训课程。

### 3.2 教学模式改革
- **全面推行项目式学习 (PBL)**：在核心专业课中，以真实项目为驱动，培养学生解决实际问题的能力。
- **强化实习实训**：延长毕业实习时间，建立更稳定的校外实习基地。

## 4. 预期成效
通过上述改进，预计学生在就业市场的竞争力将提升 20%，毕业生起薪有望增长 10%-15%。
"""
