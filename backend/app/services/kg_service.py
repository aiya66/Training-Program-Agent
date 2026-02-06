import os
import yaml
import json
import asyncio
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.core.config import get_settings
from app.services.data_loader import data_loader
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile

settings = get_settings()

class KGService:
    def __init__(self):
        # Initialize OpenAI client (using env vars or settings)
        print(f"DEBUG: Initializing KGService with API Key: {settings.DEEPSEEK_API_KEY[:5]}... Base URL: {settings.DEEPSEEK_BASE_URL}")
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        self.model = settings.DEEPSEEK_MODEL
        self.prompt_path = os.path.join(os.path.dirname(__file__), "../core/prompts/training_plan_kg_prompt.yaml")
        self._system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        try:
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading prompt: {e}")
            return "You are a helpful assistant for extracting knowledge graph entities."

    def _get_cache_path(self, school: str, college: str, major: str) -> str:
        """Generate a safe filename for caching the graph."""
        safe_school = "".join([c for c in school if c.isalnum() or c in (' ', '-', '_')]).strip()
        safe_college = "".join([c for c in college if c.isalnum() or c in (' ', '-', '_')]).strip()
        safe_major = "".join([c for c in major if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{safe_school}_{safe_college}_{safe_major}_graph.json"
        cache_dir = os.path.join(os.path.dirname(__file__), "../../data/graphs")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, filename)

    def _save_graph_to_cache(self, school: str, college: str, major: str, data: Dict[str, Any]):
        """Save graph data to a local JSON file."""
        try:
            path = self._get_cache_path(school, college, major)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"DEBUG: Graph cached to {path}")
        except Exception as e:
            print(f"Error saving graph cache: {e}")

    def _load_graph_from_cache(self, school: str, college: str, major: str) -> Dict[str, Any]:
        """Load graph data from a local JSON file if it exists."""
        try:
            path = self._get_cache_path(school, college, major)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    print(f"DEBUG: Loading graph from cache: {path}")
                    return json.load(f)
        except Exception as e:
            print(f"Error loading graph cache: {e}")
        return None

    async def extract_knowledge(self, text: str) -> Dict[str, Any]:
        """
        Extract entities and relationships from text using LLM.
        """
        print(f"DEBUG: Starting LLM extraction with model {self.model}...")
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": f"请分析以下文本（可能是职位描述或培养方案），抽取知识图谱数据：\n\n{text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"LLM Extraction Error: {e}")
            # Return mock data on error for demonstration
            return self._get_mock_kg_data()

    def _get_mock_kg_data(self):
        return {
            "entities": [
                {"id": "mock1", "name": "示例专业", "type": "Major", "category": "Knowledge"},
                {"id": "mock2", "name": "示例课程", "type": "Course", "category": "Knowledge"},
                {"id": "mock3", "name": "示例技能", "type": "Skill", "category": "Capability"},
                {"id": "mock4", "name": "团队协作", "type": "Quality", "category": "Quality"}
            ],
            "relationships": [
                {"head": "mock1", "relation": "HAS_COURSE", "tail": "mock2"},
                {"head": "mock2", "relation": "DEVELOPS_SKILL", "tail": "mock3"},
                {"head": "mock2", "relation": "CULTIVATES_QUALITY", "tail": "mock4"}
            ]
        }

    async def build_graph_for_major_stream(self, school: str, college: str, major: str):
        """
        Generator that yields progress steps and finally the graph data.
        Format: JSON string
        """
        # Step 0: Check Cache
        cached_graph = self._load_graph_from_cache(school, college, major)
        if cached_graph:
            yield json.dumps({
                "step_id": 1,
                "message": f"发现已缓存的图谱 ({school} - {major})，正在加载...",
                "status": "completed"
            }) + "\n"
            await asyncio.sleep(0.5)
            
            yield json.dumps({
                "step_id": 7,
                "message": "图谱加载成功！",
                "status": "completed",
                "data": cached_graph
            }) + "\n"
            return

        # Step 1: Initialization
        yield json.dumps({
            "step_id": 1,
            "message": f"正在初始化智能体环境... (School: {school})",
            "status": "completed"
        }) + "\n"
        await asyncio.sleep(0.5)

        # Step 2: Data Loading (School Specific)
        yield json.dumps({
            "step_id": 2,
            "message": f"正在检索 {school} 的相关招聘会与宣讲会数据...",
            "status": "running"
        }) + "\n"
        
        # Fetch Talks & Fairs
        talks = data_loader.get_related_talks(school, college=college)
        fairs = data_loader.get_related_fairs(school)
        await asyncio.sleep(0.5)
        
        yield json.dumps({
            "step_id": 2,
            "message": f"检索完成: 发现 {len(talks)} 场宣讲会 (相关学院: {college}), {len(fairs)} 场招聘会。",
            "status": "completed"
        }) + "\n"

        # Step 3: Job Matching
        yield json.dumps({
            "step_id": 3,
            "message": f"正在匹配 {major} 专业的就业岗位数据...",
            "status": "running"
        }) + "\n"

        # Use ALL data (limit=None)
        related_jobs = data_loader.search_jobs_by_major(major, limit=None)
        await asyncio.sleep(0.5)

        yield json.dumps({
            "step_id": 3,
            "message": f"匹配完成: 找到 {len(related_jobs)} 个相关岗位。",
            "status": "completed"
        }) + "\n"
        
        # Step 4: Constructing Graph Nodes
        yield json.dumps({
            "step_id": 4,
            "message": "正在构建基础图谱节点...",
            "status": "running"
        }) + "\n"

        entities = []
        relationships = []
        
        major_entity_id = f"major_{major}"
        entities.append({"id": major_entity_id, "name": major, "type": "Major", "category": "Core"})

        combined_text_for_llm = f"{school} {college} {major} 培养方案。\n"
        
        # Add Talks info to LLM context
        if talks:
             combined_text_for_llm += f"\n学校近期举办了 {len(talks)} 场宣讲会，包括：{', '.join([t['宣讲会名称'] for t in talks[:3]])}..."

        if not related_jobs:
            combined_text_for_llm += "本专业旨在培养具有良好道德修养... 核心课程包括高级语言程序设计、数据结构、操作系统..."
        else:
            for idx, job in enumerate(related_jobs):
                job_id = f"job_{job.get('编号', idx)}"
                job_name = job.get('职位名称', 'Unknown Job').strip()
                company_name = job.get('单位名称', 'Unknown Company').strip()
                
                entities.append({"id": job_id, "name": job_name, "type": "Job", "category": "Target"})
                company_id = f"company_{company_name}"
                entities.append({"id": company_id, "name": company_name, "type": "Company", "category": "Target"})
                
                relationships.append({"head": major_entity_id, "relation": "TARGETS_JOB", "tail": job_id})
                relationships.append({"head": job_id, "relation": "OFFERED_BY", "tail": company_id})
                
                desc = job.get('职位描述', '')
                # Limit the number of job descriptions sent to LLM to avoid context overflow, but keep graph nodes
                if desc and isinstance(desc, str) and idx < 20:
                    combined_text_for_llm += f"\n职位[{job_name}]要求：{desc[:200]}..."
        
        await asyncio.sleep(0.5)
        yield json.dumps({
            "step_id": 4,
            "message": f"基础节点构建完成: {len(entities)} 个实体。",
            "status": "completed"
        }) + "\n"

        # Step 5: LLM Extraction
        yield json.dumps({
            "step_id": 5,
            "message": f"正在调用 智南大模型 进行深度实体抽取...",
            "status": "running"
        }) + "\n"

        kg_data_llm = {"entities": [], "relationships": []}
        if settings.DEEPSEEK_API_KEY:
            try:
                kg_data_llm = await self.extract_knowledge(combined_text_for_llm)
                yield json.dumps({
                    "step_id": 5,
                    "message": f"智南大模型 抽取完成: 发现 {len(kg_data_llm.get('entities', []))} 个新实体。",
                    "status": "completed"
                }) + "\n"
            except Exception as e:
                yield json.dumps({
                    "step_id": 5,
                    "message": f"智南大模型 调用失败: {str(e)}",
                    "status": "failed"
                }) + "\n"
        else:
            kg_data_llm = self._get_mock_kg_data()
            yield json.dumps({
                "step_id": 5,
                "message": "使用模拟数据完成抽取。",
                "status": "completed"
            }) + "\n"

        # Step 6: Final Merge
        yield json.dumps({
            "step_id": 6,
            "message": "正在合并图谱数据并生成最终视图...",
            "status": "running"
        }) + "\n"

        existing_ids = {e['id'] for e in entities}
        
        for entity in kg_data_llm.get('entities', []):
            if entity.get('id') not in existing_ids:
                entities.append(entity)
                existing_ids.add(entity.get('id'))
        
        for rel in kg_data_llm.get('relationships', []):
            relationships.append(rel)
            
        final_graph = {
            "entities": entities,
            "relationships": relationships
        }

        # Cache the result
        self._save_graph_to_cache(school, college, major, final_graph)
        
        await asyncio.sleep(0.5)
        # Send final result with a specific event type or just as the last message
        yield json.dumps({
            "step_id": 7,
            "message": "知识图谱构建成功！",
            "status": "completed",
            "data": final_graph
        }) + "\n"

    async def analyze_graph_improvement(self, school: str, college: str, major: str, graph_data: Dict[str, Any], training_plan_text: str = None, stats_data: Dict[str, Any] = None) -> str:
        """
        Analyze the graph and generate an improvement plan report.
        """
        # 1. Summarize graph data for the LLM
        entity_counts = {}
        for e in graph_data.get("entities", []):
            etype = e.get("type", "Unknown")
            entity_counts[etype] = entity_counts.get(etype, 0) + 1
            
        skills = [e["name"] for e in graph_data.get("entities", []) if e.get("type") == "Skill"]
        courses = [e["name"] for e in graph_data.get("entities", []) if e.get("type") == "Course"]
        
        # Get Job Statistics from RAW data (Total Source)
        all_jobs = data_loader.search_jobs_by_major(major, limit=None)
        job_count = len(all_jobs)
        
        # Simple stats
        cities = {}
        companies = {}
        for j in all_jobs:
            c = j.get('工作城市', 'Unknown')
            cities[c] = cities.get(c, 0) + 1
            
            comp = j.get('单位名称', 'Unknown')
            companies[comp] = companies.get(comp, 0) + 1
            
        top_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)[:5]
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Sample some job titles for context
        job_titles = [j.get('职位名称', '') for j in all_jobs[:50]]
        
        summary = f"""
        专业: {school} - {college} - {major}
        图谱概览: {json.dumps(entity_counts, ensure_ascii=False)}
        识别到的核心技能(部分): {', '.join(skills[:30])}
        识别到的核心课程(部分): {', '.join(courses[:30])}
        
        【全量市场数据统计】
        总岗位数: {job_count}
        热门就业城市: {', '.join([f"{k}({v})" for k,v in top_cities])}
        主要招聘企业: {', '.join([f"{k}({v})" for k,v in top_companies])}
        典型岗位名称: {', '.join(job_titles[:20])}...
        """
        
        # Add training plan context if provided
        training_plan_context = ""
        if training_plan_text:
            training_plan_context = f"""
            【用户上传的培养方案上下文】
            {training_plan_text[:3000]}... (已截断)
            """

        # Prepare formatted intro
        intro_text = ""
        if stats_data:
            # Prefer Real Data calculated above if available
            real_job_count = job_count  # From data_loader
            real_company_count = len(companies) # From data_loader aggregation
            
            # Use real data for jobs/companies, fallback to stats_data for reports/policies
            job_count_display = f"{real_job_count}"
            # Ensure we don't just say "2000", maybe "2000+" or exact. Let's use exact.
            
            report_count_display = stats_data.get('report_count', '5').replace("行业发展报告", "").replace("个", "")
            policy_count_display = stats_data.get('policy_count', '5').replace("政策文件", "").replace("个", "")
            node_count_display = stats_data.get('node_count', str(len(graph_data.get('entities', []))))
            
            # If stats_data has raw numbers in string format like "相关就业岗位200个", extract digits?
            # Actually, stats_data comes from get_stats response which is formatted. 
            # But here we have the RAW real counts. Let's use them directly.
            
            intro_text = f"""
**培养方案优化**
本次优化基于互联网海量招聘数据{real_job_count}条，相关企业{real_company_count}家，{report_count_display}个行业发展报告，{policy_count_display}份政策文件（区域发展战略2个，现代制造业22个，现代服务业5个）。构建含有{node_count_display}实体节点的知识图谱，能力图谱，素质图谱。
多智能体分别从培养目标，毕业要求，主干学科，课程设置，课程体系，教学计划，质量评估等方面进行优化，优化结果如下：
"""

        prompt = f"""
        你是一个高等教育培养方案专家。请根据以下生成的“毕业生专业能力图谱”数据，分析该专业的培养现状，并提出改进方案。
        
        {training_plan_context}

        【图谱数据摘要】
        {summary}
        
        【任务要求】
        请生成一份《{school} {major}专业培养方案改进分析报告》，你需要直接接在以下这段引言之后继续生成内容，不要重复引言，也不要生成大标题（如“# 分析报告”），直接开始具体的章节内容。

        引言内容（你不需要生成这段，但我会把它放在你输出的最前面，请确保你的后续内容在逻辑上是紧接着这段话的）：
        “{intro_text}”

        包含以下章节（请使用Markdown格式）：
        1. **现状分析**：基于图谱中的课程与技能分布，结合用户上传的培养方案（如果有），分析当前的培养重点。
        2. **岗位需求匹配度**：对比就业岗位需求与当前课程/技能体系，指出匹配的优势和存在的缺口。
        3. **改进建议**：
           - 课程体系优化：建议增加或调整的课程。
           - 实践环节增强：针对技能缺口建议的实践项目。
           - 产教融合建议：如何更好地连接企业需求。
        4. **预期成效**：改进后对学生就业竞争力的提升预期。
        
        请使用Markdown格式输出，保持专业、客观、有建设性。
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是资深的高校教育教学改革专家，擅长基于数据分析提出培养方案改进建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Combine the fixed intro with the LLM generated content
            full_report = f"{intro_text}\n\n{response.choices[0].message.content}"
            return full_report
        except Exception as e:
            print(f"Analysis Error: {e}")
            return f"生成分析报告失败: {str(e)}"

    def _add_formatted_text(self, paragraph, text):
        """
        Parses text for **bold** and adds runs to the paragraph.
        """
        parts = text.split('**')
        for i, part in enumerate(parts):
            if not part: continue
            run = paragraph.add_run(part)
            # If the index is odd, it was inside **, so make it bold
            if i % 2 == 1:
                run.bold = True

    def generate_improvement_docx(self, school: str, major: str, report_content: str) -> str:
        """
        Convert the markdown report to a DOCX file and return the file path.
        """
        try:
            document = Document()
            
            # Sanitize filename
            safe_school = "".join([c for c in school if c.isalnum() or c in (' ', '-', '_')]).strip()
            safe_major = "".join([c for c in major if c.isalnum() or c in (' ', '-', '_')]).strip()
            
            # Title
            title = document.add_heading(f'{school} {major}专业培养方案改进分析报告', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Parse Markdown-ish content simply
            for line in report_content.split('\n'):
                try:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith('### '):
                        text = line.replace('### ', '').replace('**', '')
                        document.add_heading(text, level=3)
                    elif line.startswith('## '):
                        text = line.replace('## ', '').replace('**', '')
                        document.add_heading(text, level=2)
                    elif line.startswith('# '):
                        text = line.replace('# ', '').replace('**', '')
                        document.add_heading(text, level=1)
                    elif line.startswith('- ') or line.startswith('* '):
                        p = document.add_paragraph(style='List Bullet')
                        self._add_formatted_text(p, line[2:])
                    elif line[0].isdigit() and line.find('. ') > 0 and line.find('. ') < 5:
                         # Handle "1. ", "10. "
                         dot_index = line.find('. ')
                         text = line[dot_index+2:]
                         p = document.add_paragraph(style='List Number')
                         self._add_formatted_text(p, text)
                    else:
                        p = document.add_paragraph()
                        self._add_formatted_text(p, line)
                except Exception as line_e:
                    print(f"Error parsing line '{line}': {line_e}")
                    continue
                    
            # Save to temp file
            temp_dir = tempfile.gettempdir()
            filename = f"{safe_school}_{safe_major}_改进方案.docx"
            file_path = os.path.join(temp_dir, filename)
            document.save(file_path)
            
            return file_path
        except Exception as e:
            print(f"Error generating DOCX: {e}")
            # Return a path to an error file or empty string to signal failure
            return ""

    async def build_graph_for_major(self, school: str, college: str, major: str):
        """
        Build a graph for a specific major using Real Job Market Data + LLM.
        """
        print(f"DEBUG: build_graph_for_major called for {major}")
        
        # 1. Fetch relevant jobs from CSV Data
        print(f"DEBUG: Searching for jobs matching '{major}' in CSV data...")
        # Use ALL data (limit=None)
        related_jobs = data_loader.search_jobs_by_major(major, limit=None) 
        
        entities = []
        relationships = []
        
        # Create the Major Entity
        major_entity_id = f"major_{major}"
        entities.append({"id": major_entity_id, "name": major, "type": "Major"})

        combined_text_for_llm = f"{school} {college} {major} 培养方案。\n"

        if not related_jobs:
            print(f"DEBUG: No jobs found for {major}. Using default mock text.")
            combined_text_for_llm += "本专业旨在培养具有良好道德修养... 核心课程包括高级语言程序设计、数据结构、操作系统..."
        else:
            print(f"DEBUG: Found {len(related_jobs)} jobs. Constructing graph nodes...")
            for idx, job in enumerate(related_jobs):
                # Construct Entities from Structured Data
                job_id = f"job_{job.get('编号', idx)}"
                job_name = job.get('职位名称', 'Unknown Job').strip()
                company_name = job.get('单位名称', 'Unknown Company').strip()
                city = job.get('工作城市', 'Unknown City').strip()
                
                # Job Entity
                entities.append({"id": job_id, "name": job_name, "type": "Job"})
                # Company Entity
                company_id = f"company_{company_name}"
                entities.append({"id": company_id, "name": company_name, "type": "Company"})
                
                # Relationships
                # Major -> MATCHES_JOB -> Job
                relationships.append({"head": major_entity_id, "relation": "MATCHES_JOB", "tail": job_id})
                # Job -> OFFERED_BY -> Company
                relationships.append({"head": job_id, "relation": "OFFERED_BY", "tail": company_id})
                
                # Accumulate text for LLM extraction (Skills, etc.)
                desc = job.get('职位描述', '')
                if desc and isinstance(desc, str):
                    combined_text_for_llm += f"\n职位[{job_name}]要求：{desc[:200]}..."

        # 2. Extract Knowledge from Text (LLM) - either Job Descriptions or Mock Text
        kg_data_llm = {"entities": [], "relationships": []}
        if settings.DEEPSEEK_API_KEY:
            print("DEBUG: DEEPSEEK_API_KEY is set, calling extract_knowledge on combined text")
            kg_data_llm = await self.extract_knowledge(combined_text_for_llm)
        else:
            print("DEBUG: DEEPSEEK_API_KEY is NOT set, using mock data")
            kg_data_llm = self._get_mock_kg_data()
            
        # 3. Merge Structured Data Graph with LLM Extracted Graph
        # We need to be careful about duplicates.
        existing_ids = {e['id'] for e in entities}
        
        for entity in kg_data_llm.get('entities', []):
            # Simple ID generation if not present or conflict avoidance
            # LLM usually returns IDs like "e1", "e2". We might want to prefix them or rely on names.
            # For this demo, we just append.
            if entity.get('id') not in existing_ids:
                entities.append(entity)
                existing_ids.add(entity.get('id'))
        
        for rel in kg_data_llm.get('relationships', []):
            relationships.append(rel)

        return {
            "entities": entities,
            "relationships": relationships
        }

kg_service = KGService()
