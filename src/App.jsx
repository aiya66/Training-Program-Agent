import React, { useState, useEffect, useRef } from 'react';
import {
  School,
  BookOpen,
  GraduationCap,
  ChevronRight,
  ChevronDown,
  Brain,
  Download,
  User,
  Projector, // for ProjectDiagram replacement
  Activity,  // for ChartLine replacement
  AlertTriangle,
  ArrowUp,
  Clock,
  Database,
  Upload,
  Play,
  RefreshCw,
  Maximize2,
  X
} from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';
import RadarChart from './components/RadarChart';
import ProcessFlow from './components/ProcessFlow';
import AnalysisReport from './components/AnalysisReport';
import ProcessLog from './components/ProcessLog';
import logo from '../zhinan_logo_v1.png';

// Helper for ForceGraph resizing
const GraphContainer = ({ data, ...props }) => {
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };

    updateDimensions();
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) resizeObserver.observe(containerRef.current);

    return () => resizeObserver.disconnect();
  }, []);

  const nodes = data?.entities?.map(e => ({ ...e })) || [];
  const links = data?.relationships?.map(r => ({ source: r.head, target: r.tail, ...r })) || [];

  return (
    <div ref={containerRef} className="w-full h-full min-h-[300px]">
      {dimensions.width > 0 && (
        <ForceGraph2D
          width={dimensions.width}
          height={dimensions.height}
          graphData={{ nodes, links }}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name || node.id;
            const fontSize = 12/globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            
            const color = node.type === 'Major' ? '#3b82f6' : (node.category === 'Capability' ? '#8b5cf6' : '#64748b');

            ctx.beginPath();
            ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
            ctx.fillStyle = color;
            ctx.fill();
            
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            
            ctx.lineWidth = 2/globalScale;
            ctx.strokeStyle = 'rgba(0,0,0,0.8)';
            ctx.strokeText(label, node.x, node.y + 7);
            ctx.fillText(label, node.x, node.y + 7);
          }}
          linkColor={() => 'rgba(255,255,255,0.2)'}
          backgroundColor="rgba(0,0,0,0)"
          {...props}
        />
      )}
    </div>
  );
};

const LargeGraphModal = ({ data, onClose }) => {
    // Calculate counts
    const counts = React.useMemo(() => {
        let majorCount = 0;
        let capabilityCount = 0;
        let otherCount = 0;

        if (data && data.entities) {
            data.entities.forEach(node => {
                if (node.type === 'Major') {
                    majorCount++;
                } else if (node.category === 'Capability') {
                    capabilityCount++;
                } else {
                    otherCount++;
                }
            });
        }
        return { major: majorCount, capability: capabilityCount, other: otherCount };
    }, [data]);

    // Handle ESC key
    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [onClose]);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-6 animate-in fade-in duration-200">
            <div className="w-full h-full bg-slate-900 rounded-2xl border border-white/10 flex flex-col overflow-hidden relative shadow-2xl ring-1 ring-white/10">
                <div className="absolute top-4 right-4 z-10 flex gap-2">
                    <div className="px-4 py-2 bg-black/40 backdrop-blur rounded-lg text-white/70 text-sm border border-white/5 flex items-center">
                        按 ESC 关闭
                    </div>
                    <button 
                        onClick={onClose}
                        className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors border border-white/10 hover:border-white/20"
                    >
                        <X size={20} />
                    </button>
                </div>
                <div className="flex-1 bg-gradient-to-br from-slate-900 to-slate-800 relative">
                     {/* Legend for Modal */}
                     <div className="absolute top-4 left-4 z-10 p-4 bg-black/40 backdrop-blur-md rounded-xl border border-white/5 space-y-2">
                        <div className="text-sm font-medium text-white mb-2">图谱图例</div>
                        <div className="flex items-center gap-2 text-xs text-gray-300">
                            <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                            <span>专业/核心 ({counts.major})</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-300">
                            <span className="w-3 h-3 rounded-full bg-violet-500"></span>
                            <span>能力/素质 ({counts.capability})</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-300">
                            <span className="w-3 h-3 rounded-full bg-slate-500"></span>
                            <span>课程/其他 ({counts.other})</span>
                        </div>
                    </div>

                    <GraphContainer 
                        data={data}
                        nodeRelSize={8}
                        nodeCanvasObject={(node, ctx, globalScale) => {
                            const label = node.name || node.id;
                            const fontSize = 14/globalScale; // Scale font size
                            ctx.font = `${fontSize}px Sans-Serif`;
                            
                            // Determine color
                            const color = node.type === 'Major' ? '#3b82f6' : (node.category === 'Capability' ? '#8b5cf6' : '#64748b');

                            // Draw Node
                            ctx.beginPath();
                            ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
                            ctx.fillStyle = color;
                            ctx.fill();
                            
                            // Glow effect for node
                            ctx.shadowColor = color;
                            ctx.shadowBlur = 10;
                            ctx.stroke();
                            ctx.shadowBlur = 0;

                            // Draw Label
                            if (globalScale > 0.5) { // Optimization: only draw text when zoomed in a bit or always? User asked for always.
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'top';
                                ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                                
                                // Text outline for readability
                                ctx.lineWidth = 2/globalScale;
                                ctx.strokeStyle = 'rgba(0,0,0,0.8)';
                                ctx.strokeText(label, node.x, node.y + 8);
                                
                                ctx.fillText(label, node.x, node.y + 8);
                            }
                        }}
                        linkColor={() => 'rgba(255,255,255,0.15)'}
                    />
                </div>
            </div>
        </div>
    );
};

function App() {
  // --- Original State & Logic ---
  const [loading, setLoading] = useState(false);
  const [thoughts, setThoughts] = useState([]); // Kept for logic preservation, though UI might differ

  const [selectedSchool, setSelectedSchool] = useState('');
  const [selectedCollege, setSelectedCollege] = useState('');
  const [selectedMajor, setSelectedMajor] = useState('');
  
  // Expanded state for Sidebar Tree
  const [expandedSchool, setExpandedSchool] = useState('');
  const [expandedCollege, setExpandedCollege] = useState('');

  const [schoolOptions, setSchoolOptions] = useState([]);
  const [collegeOptions, setCollegeOptions] = useState([]);
  const [majorOptions, setMajorOptions] = useState([]);

  const [graphData, setGraphData] = useState(null);
  const [showGraphModal, setShowGraphModal] = useState(false);
  const [analysisReport, setAnalysisReport] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0); // For ProcessFlow
  const [processLogs, setProcessLogs] = useState([]); // For ProcessLog component
  const [hasUploadedPlan, setHasUploadedPlan] = useState(false);
  const [uploadedPlanContext, setUploadedPlanContext] = useState(null); // Store info about uploaded plan
  const [isGraphReady, setIsGraphReady] = useState(false);

  const [stats, setStats] = useState([
    "相关就业岗位 0万个",
    "相关企业家 0家",
    "行业发展报告 0个",
    "政策文件 0个"
  ]);

  // Fetch Schools
  useEffect(() => {
    fetch('/api/v1/schools')
      .then(res => res.json())
      .then(data => setSchoolOptions(data))
      .catch(err => console.error("Failed to fetch schools", err));
  }, []);

  const generateReport = async (major, graphData) => {
    setIsAnalyzing(true);
    setCurrentStep(5); // Advance to Analysis step
    try {
        const res = await fetch('/api/v1/agent/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                school: selectedSchool,
                college: selectedCollege,
                major: major,
                graph_data: graphData,
                training_plan_text: uploadedPlanContext ? uploadedPlanContext.content : null
            })
        });
        if (res.ok) {
            const data = await res.json();
            setAnalysisReport(data.report);
        }
    } catch (e) {
        console.error("Analysis failed", e);
    } finally {
        setIsAnalyzing(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!analysisReport) {
      alert("请先生成分析报告后再导出");
      return;
    }

    setIsDownloading(true);
    try {
      const res = await fetch('/api/v1/agent/download-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          school: selectedSchool,
          major: selectedMajor,
          report_content: analysisReport
        })
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedSchool}_${selectedMajor}_培养方案改进分析报告.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert("下载失败，请稍后重试");
      }
    } catch (e) {
      console.error("Download failed", e);
      alert("下载失败，请稍后重试");
    } finally {
      setIsDownloading(false);
    }
  };

  // Selection Handlers (Modified for Sidebar)
  const handleSchoolClick = (school) => {
    if (expandedSchool === school) {
        setExpandedSchool('');
    } else {
        setExpandedSchool(school);
        setSelectedSchool(school);
        // Fetch Colleges
        if (selectedSchool !== school) {
            setCollegeOptions([]); 
            setMajorOptions([]);
            fetch(`/api/v1/schools/${encodeURIComponent(school)}/colleges`)
                .then(res => res.json())
                .then(data => setCollegeOptions(data))
                .catch(err => console.error("Failed to fetch colleges", err));
        }
    }
  };

  const handleCollegeClick = (e, college) => {
    e.stopPropagation();
    if (expandedCollege === college) {
        setExpandedCollege('');
    } else {
        setExpandedCollege(college);
        setSelectedCollege(college);
        // Fetch Majors
        if (selectedCollege !== college) {
            setMajorOptions([]);
            fetch(`/api/v1/schools/${encodeURIComponent(selectedSchool)}/colleges/${encodeURIComponent(college)}/majors`)
                .then(res => res.json())
                .then(data => setMajorOptions(data))
                .catch(err => console.error("Failed to fetch majors", err));
        }
    }
  };

  const handleMajorClick = async (e, major) => {
    e.stopPropagation();
    setSelectedMajor(major);
    // Reset states when changing major
    setGraphData(null);
    setAnalysisReport(null);
    setProcessLogs([]);
    setCurrentStep(0);
    setIsGraphReady(false);
  };

  const startGraphGeneration = async () => {
    if (!selectedMajor || !hasUploadedPlan) {
        alert("请先上传培养方案并选择学校/专业");
        return;
    }

    const major = selectedMajor;
    setLoading(true);
    setCurrentStep(1); // Start with step 1 (Data Collection)
    setGraphData(null); // Reset graph
    setAnalysisReport(null); // Reset report
    setProcessLogs([]); // Reset logs
    setIsGraphReady(false);

    try {
      // 1. Fetch Stats
      const statsRes = await fetch(`/api/v1/stats?major=${encodeURIComponent(major)}`);
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats([
          statsData.jobs,
          statsData.companies,
          statsData.reports,
          statsData.policies
        ]);
      }
      
      setCurrentStep(2); // Move to step 2 (Knowledge Extraction)

      // 2. Stream Graph
      const streamUrl = `/api/v1/agent/stream-build-graph?school=${encodeURIComponent(selectedSchool)}&college=${encodeURIComponent(selectedCollege)}&major=${encodeURIComponent(major)}`;
      const response = await fetch(streamUrl);
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            
            // Map backend step_id to frontend steps (1-4)
            // Assuming backend steps:
            // 1-2: Data Collection (already set initially)
            // 3-4: Knowledge Extraction
            // 5-6: Graph Construction
            // 7: Analysis/Final
            
            // Add to log
            if (data.message) {
                 setProcessLogs(prev => [...prev, {
                     ...data,
                     timestamp: new Date().toLocaleTimeString()
                 }]);
            }

            if (data.step_id) {
                 if (data.step_id <= 2) setCurrentStep(1);
                 else if (data.step_id <= 4) setCurrentStep(2);
                 else if (data.step_id <= 6) setCurrentStep(3);
                 else setCurrentStep(4);
            }

            if (data.data && data.step_id === 7) {
                setGraphData(data.data);
                setCurrentStep(4); // Ensure final step is reached
                setIsGraphReady(true);
                // generateReport(major, data.data); // Removed automatic generation
            }
          } catch (e) { console.error(e); }
        }
      }
    } catch (error) {
      console.error("Error:", error);
      setCurrentStep(0); // Reset on error
    } finally {
      setLoading(false);
    }
  };

  // Dimensions
  const dimensions = [
    { icon: <Activity size={14} className="text-blue-400" />, text: "培养目标" },
    { icon: <GraduationCap size={14} className="text-purple-400" />, text: "毕业要求" },
    { icon: <BookOpen size={14} className="text-indigo-400" />, text: "主干学科" },
    { icon: <Database size={14} className="text-cyan-400" />, text: "课程设置" },
    { icon: <Brain size={14} className="text-pink-400" />, text: "课程体系" },
    { icon: <Clock size={14} className="text-orange-400" />, text: "教学计划" },
    { icon: <AlertTriangle size={14} className="text-green-400" />, text: "质量评估" },
  ];

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-slate-900 text-slate-200 font-sans selection:bg-blue-500/30">
      
      {/* --- Sidebar --- */}
      <aside className="w-80 glass-panel flex flex-col border-r border-white/10 z-20">
        {/* Logo */}
        <div className="p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20 overflow-hidden">
                    <img src={logo} alt="Logo" className="w-full h-full object-cover" />
                </div>
                <div>
                    <h1 className="text-lg font-bold text-white tracking-wide">智南大模型</h1>
                    <p className="text-xs text-gray-400">培养方案智能分析系统</p>
                </div>
            </div>
        </div>

        {/* Upload Section - New Addition */}
        <div className="p-4 border-b border-white/10 bg-white/5">
            <button 
                onClick={() => document.getElementById('upload-plan').click()}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600/20 to-purple-600/20 hover:from-blue-600/30 hover:to-purple-600/30 border border-blue-500/30 flex items-center justify-center gap-3 group transition-all duration-300 relative overflow-hidden"
            >
                <div className="absolute inset-0 bg-blue-500/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform relative z-10">
                     <Upload size={18} className="text-blue-400 group-hover:text-blue-300" />
                </div>
                <div className="flex flex-col items-start relative z-10">
                    <span className="text-sm font-medium text-blue-100 group-hover:text-white">上传培养方案</span>
                    <span className="text-[10px] text-blue-300/60 group-hover:text-blue-200/80">第一步：导入本地文件</span>
                </div>
            </button>
            <input 
                type="file" 
                id="upload-plan" 
                className="hidden" 
                accept=".pdf,.doc,.docx" 
                onChange={async (e) => {
                    if(e.target.files[0]) {
                        const file = e.target.files[0];
                        
                        try {
                            // Show loading state if possible, or just alert start
                            const formData = new FormData();
                            formData.append('file', file);
                            
                            const res = await fetch('/api/v1/parse-file', {
                                method: 'POST',
                                body: formData
                            });
                            
                            if (res.ok) {
                                const data = await res.json();
                                setHasUploadedPlan(true);
                                setUploadedPlanContext({
                                    fileName: data.filename,
                                    content: data.content
                                });
                                alert(`文件 "${file.name}" 解析成功！\n已提取文本内容 ${data.content.length} 字符。\n请继续选择下方学校组合，并点击生成图谱按钮。`);
                            } else {
                                const err = await res.json();
                                alert(`文件解析失败: ${err.detail}`);
                            }
                        } catch (error) {
                            console.error("Upload error:", error);
                            alert("文件上传失败，请重试");
                        }
                    }
                }}
            />
        </div>

        {/* Navigation Tree */}
        <div className="flex-1 overflow-y-auto py-4 scrollbar-thin">
            {/* School Level */}
            <div className="mb-2">
                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">学校层级</div>
                {schoolOptions.map(school => (
                    <div key={school}>
                        <div 
                            className={`nav-item px-6 py-3 flex items-center justify-between ${selectedSchool === school ? 'active' : ''}`}
                            onClick={() => handleSchoolClick(school)}
                        >
                            <div className="flex items-center gap-3">
                                <School size={16} className={selectedSchool === school ? "text-blue-400" : "text-gray-400"} />
                                <span className={`text-sm ${selectedSchool === school ? "font-medium text-white" : "text-gray-300"}`}>{school}</span>
                            </div>
                            {expandedSchool === school ? <ChevronDown size={14} className="text-gray-500"/> : <ChevronRight size={14} className="text-gray-600"/>}
                        </div>

                        {/* College Level (Nested) */}
                        {expandedSchool === school && (
                            <div className="bg-black/20 pb-2">
                                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider mt-2">学院层级</div>
                                {collegeOptions.length === 0 && <div className="px-6 py-2 text-xs text-gray-500">加载中...</div>}
                                {collegeOptions.map(college => (
                                    <div key={college}>
                                        <div 
                                            className={`nav-item pl-10 pr-6 py-2 flex items-center justify-between ${selectedCollege === college ? 'bg-blue-500/10' : ''}`}
                                            onClick={(e) => handleCollegeClick(e, college)}
                                        >
                                            <div className="flex items-center gap-3">
                                                <BookOpen size={14} className={selectedCollege === college ? "text-purple-400" : "text-gray-500"} />
                                                <span className={`text-sm ${selectedCollege === college ? "text-blue-200" : "text-gray-400"}`}>{college}</span>
                                            </div>
                                            {expandedCollege === college ? <ChevronDown size={12} className="text-gray-600"/> : <ChevronRight size={12} className="text-gray-700"/>}
                                        </div>

                                        {/* Major Level (Nested) */}
                                        {expandedCollege === college && (
                                            <div className="bg-black/20">
                                                {majorOptions.length === 0 && <div className="pl-16 py-2 text-xs text-gray-500">加载中...</div>}
                                                {majorOptions.map(major => (
                                                    <div 
                                                        key={major}
                                                        className={`nav-item pl-16 pr-6 py-2 flex items-center gap-3 ${selectedMajor === major ? 'bg-blue-500/20 border-l-2 border-blue-400' : ''}`}
                                                        onClick={(e) => handleMajorClick(e, major)}
                                                    >
                                                        <span className={`w-1.5 h-1.5 rounded-full ${selectedMajor === major ? 'bg-blue-400' : 'bg-gray-600'}`}></span>
                                                        <span className={`text-sm ${selectedMajor === major ? 'text-blue-300' : 'text-gray-400'}`}>{major}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>

        {/* Bottom Actions & Dimensions */}
        <div className="border-t border-white/10 p-4 bg-black/20">
             {/* Action Button - Moved here */}
             <div className="mb-4">
                <div className="flex gap-3">
                    <button 
                        onClick={startGraphGeneration}
                        disabled={!selectedMajor || !hasUploadedPlan || loading}
                        className={`flex-1 py-2.5 px-2 rounded-xl flex items-center justify-center gap-2 font-bold transition-all shadow-lg ${
                            loading 
                            ? 'bg-blue-600/20 text-blue-400 cursor-wait' 
                            : (!selectedMajor || !hasUploadedPlan)
                                ? 'bg-gray-700/50 text-gray-500 cursor-not-allowed'
                                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-500/25'
                        }`}
                    >
                        {loading ? (
                            <>
                                <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                <span className="text-xs">生成中...</span>
                            </>
                        ) : (
                            <>
                                <Play size={14} fill="currentColor" />
                                <span className="text-xs">开始思考</span>
                            </>
                        )}
                    </button>

                    <button 
                        onClick={() => {
                            if(window.confirm("确定要重置当前分析结果吗？")) {
                                setGraphData(null);
                                setAnalysisReport(null);
                                setProcessLogs([]);
                                setCurrentStep(0);
                                setIsGraphReady(false);
                            }
                        }}
                        disabled={!selectedMajor || !hasUploadedPlan || loading}
                        className={`flex-1 py-2.5 px-2 rounded-xl flex items-center justify-center gap-2 font-bold transition-all shadow-lg border border-white/10 ${
                            (!selectedMajor || !hasUploadedPlan || loading)
                                ? 'bg-gray-700/50 text-gray-500 cursor-not-allowed'
                                : 'bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white'
                        }`}
                    >
                        <RefreshCw size={14} />
                        <span className="text-xs">重置</span>
                    </button>
                </div>
                 
                 {/* Status Indicator */}
                 <div className="mt-2 flex items-center justify-center gap-2 text-xs text-gray-400">
                    <span className={`w-2 h-2 rounded-full ${loading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></span>
                    {loading ? '正在构建图谱...' : '系统就绪'}
                 </div>
             </div>

            <div className="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">对标维度</div>
            <div className="grid grid-cols-2 gap-2">
                {dimensions.map((d, i) => (
                    <div key={i} className="dimension-tag px-2 py-1.5 rounded-lg flex items-center gap-2 cursor-pointer group bg-white/5 hover:bg-white/10 border border-white/5 transition-colors">
                        {d.icon}
                        <span className="text-[10px] font-medium text-gray-300 group-hover:text-white transition-colors truncate">{d.text}</span>
                    </div>
                ))}
            </div>
        </div>
      </aside>

      {/* --- Main Content --- */}
      <main className="flex-1 flex flex-col overflow-hidden relative z-10">
         {/* Background Decoration */}
         <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[100px] pointer-events-none"></div>
         <div className="absolute bottom-[-20%] left-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>

        {/* Header */}
        <header className="glass-panel border-b border-white/10 px-8 py-4 flex items-center justify-between z-20">
            <div className="flex items-center gap-4">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    {selectedSchool || '请选择学校'} 
                    {selectedCollege && <span className="text-gray-500">/</span>} 
                    {selectedCollege}
                    {selectedMajor && <span className="text-gray-500">/</span>}
                    <span className="text-blue-400">{selectedMajor}</span>
                </h2>
                {selectedMajor && (
                    <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs border border-blue-500/30">2024版培养方案</span>
                )}
            </div>
            <div className="flex items-center gap-4">
                <button 
                    onClick={handleDownloadReport}
                    disabled={isDownloading}
                    className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm text-gray-300 transition-colors border border-white/10 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Download size={14} className={`mr-2 ${isDownloading ? 'animate-bounce' : ''}`}/> 
                    {isDownloading ? '导出中...' : '导出报告'}
                </button>
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                    <User size={14} className="text-white" />
                </div>
            </div>
        </header>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-8 scrollbar-thin">
            <div className="grid grid-cols-12 gap-6 h-full min-h-[800px]">
                
                {/* Left Column (7/12) */}
                <div className="col-span-7 flex flex-col gap-6">
                    {/* Process Flow */}
                    <div className="glass-card rounded-2xl p-6 h-[420px]">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                <Activity className="text-purple-400" size={18} />
                                多智能体协作
                            </h3>
                        </div>
                        <ProcessFlow currentStep={currentStep} />
                    </div>

                    {/* Mind Map Agent */}
                    <div className="glass-card rounded-2xl p-6 flex-1 flex flex-col min-h-[400px]">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                <Projector className="text-blue-400" size={18}/>
                                知识、素质、能力图谱
                            </h3>
                            <div className="flex items-center gap-2">
                                {loading && (
                                    <button 
                                        disabled
                                        className="py-1.5 px-3 rounded-lg flex items-center justify-center gap-2 font-medium transition-all shadow-lg bg-blue-600/20 text-blue-400 cursor-wait text-xs"
                                    >
                                        <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                        <span>正在生成...</span>
                                    </button>
                                )}
                                {graphData && !loading && (
                                    <>
                                        <button 
                                            onClick={() => setShowGraphModal(true)}
                                            className="py-1.5 px-3 rounded-lg flex items-center justify-center gap-2 font-medium transition-all shadow-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-500/25 text-xs"
                                        >
                                            <Maximize2 size={12} />
                                            <span>查看详情</span>
                                        </button>
                                        <button 
                                            onClick={startGraphGeneration}
                                            className="py-1.5 px-3 rounded-lg flex items-center justify-center gap-2 font-medium transition-all shadow-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 text-xs"
                                        >
                                            <RefreshCw size={12} />
                                            <span>重新生成</span>
                                        </button>
                                    </>
                                )}
                            </div>
                        </div>
                        <div className="flex-1 relative bg-black/20 rounded-xl border border-white/5 overflow-hidden">
                             {/* Force Graph Container */}
                             {graphData ? (
                                 <GraphContainer data={graphData} />
                             ) : (
                                 <div className="w-full h-full flex items-center justify-center text-gray-500 text-sm">
                                     等待数据加载...
                                 </div>
                             )}
                        </div>
                        <div className="mt-4 flex gap-2 overflow-x-auto pb-2 scrollbar-none">
                            {['知识图谱', '能力图谱', '素质图谱'].map(t => (
                                <button key={t} className="px-3 py-1 rounded-full bg-white/5 hover:bg-white/10 text-gray-400 text-xs border border-white/10 whitespace-nowrap transition-colors">
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column (5/12) */}
                <div className="col-span-5 flex flex-col gap-6">
                    {/* Top: Process Log (New) - Fill remaining height */}
                    <div className="glass-card rounded-2xl p-6 flex-1 min-h-[200px]">
                        <ProcessLog logs={processLogs} currentStep={currentStep} />
                    </div>

                    {/* Bottom: Analysis Report - Fixed Height */}
                    <div className="glass-card rounded-2xl p-6 h-[500px] w-full">
                        <AnalysisReport 
                            report={analysisReport} 
                            loading={isAnalyzing}
                            onRefresh={() => graphData && generateReport(selectedMajor, graphData)}
                            actionLabel={analysisReport ? "重新生成" : "生成分析报告"}
                            disabled={!graphData}
                        />
                    </div>
                </div>

            </div>
        </div>
      </main>

      {/* Large Graph Modal */}
      {showGraphModal && graphData && (
        <LargeGraphModal 
            data={graphData} 
            onClose={() => setShowGraphModal(false)} 
        />
      )}
    </div>
  );
}

export default App;
