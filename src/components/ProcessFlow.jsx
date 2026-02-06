import React from 'react';
import { 
  Database, FileText, CheckCircle2, 
  Network, Share2,
  Briefcase, Award, TrendingUp, CheckSquare,
  Brain, Zap, UserCheck, Layout
} from 'lucide-react';

const ProcessFlow = ({ currentStep = 0 }) => {
  // Custom Node Configuration based on user's flowchart
  const nodes = [
    // Step 1: Start / Data Elements
    { id: 'start', x: 5, y: 50, label: "数据要素", icon: Database, color: "red", stepThreshold: 1, description: "初始化数据采集任务，确立数据要素基础" },

    // Step 1.5: Data Sources (Parallel)
    { id: 'src-1', x: 25, y: 20, label: "海量岗位", icon: Briefcase, color: "red", stepThreshold: 1, description: "采集全网海量招聘岗位数据" },
    { id: 'src-2', x: 25, y: 40, label: "高质量岗位", icon: Award, color: "red", stepThreshold: 1, description: "筛选重点企业高质量岗位需求" },
    { id: 'src-3', x: 25, y: 60, label: "行业发展", icon: TrendingUp, color: "red", stepThreshold: 1, description: "分析行业发展趋势报告" },
    { id: 'src-4', x: 25, y: 80, label: "政策文件", icon: FileText, color: "red", stepThreshold: 1, description: "解析国家及地方相关政策文件" },

    // Step 2: Verification & Summary
    { id: 'verify', x: 45, y: 50, label: "验证汇总", icon: CheckSquare, color: "red", stepThreshold: 2, description: "多源数据交叉验证与清洗汇总" },

    // Step 3: Graph Construction
    { id: 'build', x: 60, y: 50, label: "构建图谱", icon: Network, color: "red", stepThreshold: 3, description: "基于汇总数据构建实体关系网络" },

    // Step 3.5: Graph Types (Parallel)
    { id: 'graph-1', x: 78, y: 30, label: "知识图谱", icon: Brain, color: "red", stepThreshold: 3, description: "构建专业知识体系图谱" },
    { id: 'graph-2', x: 78, y: 50, label: "能力图谱", icon: Zap, color: "red", stepThreshold: 3, description: "构建岗位核心能力图谱" },
    { id: 'graph-3', x: 78, y: 70, label: "素质图谱", icon: UserCheck, color: "red", stepThreshold: 3, description: "构建综合素质要求图谱" },

    // Step 4: Display Page
    { id: 'end', x: 95, y: 50, label: "构建展示页面", icon: Layout, color: "green", stepThreshold: 4, description: "生成可视化交互展示页面" },
  ];

  // Manual Edge Definitions to match the flowchart
  const edges = [
    // One to Many: Start -> Sources
    { from: 'start', to: 'src-1' },
    { from: 'start', to: 'src-2' },
    { from: 'start', to: 'src-3' },
    { from: 'start', to: 'src-4' },

    // Many to One: Sources -> Verify
    { from: 'src-1', to: 'verify' },
    { from: 'src-2', to: 'verify' },
    { from: 'src-3', to: 'verify' },
    { from: 'src-4', to: 'verify' },

    // Linear: Verify -> Build
    { from: 'verify', to: 'build' },

    // One to Many: Build -> Graphs
    { from: 'build', to: 'graph-1' },
    { from: 'build', to: 'graph-2' },
    { from: 'build', to: 'graph-3' },

    // Many to One: Graphs -> End
    { from: 'graph-1', to: 'end' },
    { from: 'graph-2', to: 'end' },
    { from: 'graph-3', to: 'end' },
  ];

  const getNode = (id) => nodes.find(n => n.id === id);

  const getPath = (start, end) => {
    const sX = start.x;
    const sY = start.y;
    const eX = end.x;
    const eY = end.y;
    const midX = (sX + eX) / 2;
    return `M ${sX} ${sY} C ${midX} ${sY}, ${midX} ${eY}, ${eX} ${eY}`;
  };

  return (
    <div className="relative w-full h-full min-h-[280px] select-none">
      {/* SVG Layer for Edges */}
      <svg 
        className="absolute inset-0 w-full h-full pointer-events-none overflow-visible"
        viewBox="0 0 100 100" 
        preserveAspectRatio="none"
      >
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="0.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <marker id="arrowhead-sm" markerWidth="4" markerHeight="4" refX="2" refY="2" orient="auto">
             <path d="M0,0 L4,2 L0,4" fill="none" stroke="#64748b" strokeWidth="0.5" />
          </marker>
        </defs>

        {edges.map((edge, idx) => {
          const startNode = getNode(edge.from);
          const endNode = getNode(edge.to);
          
          // Edge logic: Active if the SOURCE node is completed/passed threshold
          // OR if we are currently working towards the target?
          // Let's stick to: Edge is active if we are AT LEAST at the stepThreshold of the target node
          const isActive = currentStep >= endNode.stepThreshold;
          const isCompleted = currentStep > endNode.stepThreshold;

          return (
            <g key={`${edge.from}-${edge.to}`}>
              {/* Background Path */}
              <path
                d={getPath(startNode, endNode)}
                fill="none"
                stroke="#94a3b8"
                strokeWidth={1}
                vectorEffect="non-scaling-stroke"
                markerEnd="url(#arrowhead-sm)"
                style={{ opacity: 0.3 }}
              />
              
              {/* Active Path */}
              {isActive && (
                <path
                  d={getPath(startNode, endNode)}
                  fill="none"
                  stroke={isCompleted ? "#3b82f6" : "#60a5fa"}
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  className="animate-flow-fast"
                  vectorEffect="non-scaling-stroke"
                  style={{
                    filter: 'url(#glow)',
                    opacity: isCompleted ? 0.4 : 0.8
                  }}
                />
              )}
            </g>
          );
        })}
      </svg>

      {/* Nodes Layer */}
      {nodes.map((node) => {
        const isActive = currentStep >= node.stepThreshold;
        
        // Color mapping
        const colorMap = {
          blue: 'text-blue-400 border-blue-500/50 shadow-blue-500/30',
          purple: 'text-purple-400 border-purple-500/50 shadow-purple-500/30',
          orange: 'text-orange-400 border-orange-500/50 shadow-orange-500/30',
          green: 'text-green-400 border-green-500/50 shadow-green-500/30',
          red: 'text-red-400 border-red-500/50 shadow-red-500/30',
        };
        
        const baseStyle = "w-8 h-8 rounded-lg flex items-center justify-center border transition-all duration-500 z-10 bg-slate-900";
        const activeStyle = isActive 
          ? `${colorMap[node.color]} scale-110 shadow-[0_0_10px_rgba(0,0,0,0.4)]` 
          : "border-slate-700 text-slate-600 scale-100 opacity-60 grayscale";
        
        // Staggered animation delay based on x position
        const delay = node.x * 10;

        return (
          <div
            key={node.id}
            className="absolute flex flex-col items-center gap-1.5 transform -translate-x-1/2 -translate-y-1/2 transition-all duration-500 group cursor-help z-10 hover:z-50"
            style={{ 
                left: `${node.x}%`, 
                top: `${node.y}%`,
                transitionDelay: `${delay}ms`
            }}
          >
            {/* Tooltip */}
            <div className="absolute bottom-full mb-2 w-48 p-3 bg-slate-900/90 backdrop-blur-xl border border-slate-700/50 rounded-xl text-xs text-slate-300 opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none translate-y-2 group-hover:translate-y-0 shadow-2xl shadow-black/50 z-50">
              <div className="font-semibold text-blue-300 mb-1 flex items-center gap-2">
                <node.icon size={12} />
                {node.label}
              </div>
              <div className="leading-relaxed text-slate-400">
                {node.description}
              </div>
              {/* Arrow */}
              <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-[1px] border-4 border-transparent border-t-slate-900/90"></div>
            </div>

            {/* Label - Moved to top as requested */}
            <div className={`text-[10px] font-medium tracking-tight whitespace-nowrap transition-colors duration-300 ${isActive ? 'text-blue-100' : 'text-slate-600'}`}>
              {node.label}
            </div>

            {/* Icon Container */}
            <div className={`${baseStyle} ${activeStyle} relative`}>
               <node.icon size={14} strokeWidth={2.5} />
               
               {/* Status Indicator for Active Phase - Moved inside icon container */}
               {currentStep === node.stepThreshold && (
                <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-white rounded-full flex items-center justify-center animate-pulse shadow-lg shadow-white/50">
                </div>
               )}
            </div>
            
            {/* Status Indicator was here */}
          </div>
        );
      })}
      
      <style jsx>{`
        @keyframes flow-fast {
          from { stroke-dashoffset: 16; }
          to { stroke-dashoffset: 0; }
        }
        .animate-flow-fast {
          animation: flow-fast 1s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default ProcessFlow;
