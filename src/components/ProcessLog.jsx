import React, { useEffect, useRef } from 'react';
import { Terminal, CheckCircle2, Circle, Loader2, BookOpen } from 'lucide-react';

const ProcessLog = ({ logs = [], currentStep = 0 }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <BookOpen className="text-emerald-400" size={18} />
          实时思维过程
        </h3>
        <div className="flex items-center gap-2">
           <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
             <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
             Live Demo
           </span>
        </div>
      </div>

      <div className="flex-1 bg-black/40 rounded-xl border border-white/5 p-4 overflow-hidden relative font-mono text-sm shadow-inner">
        {/* Decorative header for terminal look */}
        <div className="absolute top-0 left-0 right-0 h-8 bg-white/5 border-b border-white/5 flex items-center px-4 gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/50"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-green-500/50"></div>
            <div className="ml-auto text-xs text-gray-500">process_monitor.exe</div>
        </div>

        <div 
          ref={scrollRef}
          className="absolute top-8 left-0 right-0 bottom-0 overflow-y-auto p-4 scrollbar-thin space-y-4"
        >
          {logs.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-2">
              <Terminal size={32} opacity={0.5} />
              <p>等待任务启动...</p>
            </div>
          ) : (
            logs.map((log, index) => {
              // Logic: A step is considered finished if it's explicitly 'completed' 
              // OR if it was 'running' but is no longer the last step (implied completion of previous step)
              const isFinished = log.status === 'completed' || (log.status === 'running' && index < logs.length - 1);
              const isRunning = log.status === 'running' && index === logs.length - 1;

              return (
                <div key={index} className="flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <div className="flex-shrink-0 mt-0.5">
                    {isFinished ? (
                      <CheckCircle2 size={14} className="text-emerald-500" />
                    ) : isRunning ? (
                      <Loader2 size={14} className="text-blue-400 animate-spin" />
                    ) : (
                      <Circle size={14} className="text-gray-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className={`text-xs mb-0.5 ${
                      isFinished ? 'text-gray-400' : 
                      isRunning ? 'text-blue-300' : 'text-gray-500'
                    }`}>
                      {String(index + 1).padStart(2, '0')} {log.step_name || 'System Process'}
                    </div>
                    <div className={`${
                      isFinished ? 'text-gray-300' : 
                      isRunning ? 'text-white font-medium' : 'text-gray-500'
                    }`}>
                      {log.message}
                    </div>
                    {isFinished && (
                      <div className="text-[10px] text-emerald-500/50 mt-1">Completed</div>
                    )}
                  </div>
                </div>
              );
            })
          )}
          
          {/* Cursor effect at the end */}
          {logs.length > 0 && (
             <div className="flex gap-3 pl-0.5">
                <div className="w-3.5 flex justify-center">
                    <div className="w-1.5 h-4 bg-blue-500/50 animate-pulse"></div>
                </div>
                <div className="text-gray-500 italic text-xs">等待下一步指令...</div>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProcessLog;
