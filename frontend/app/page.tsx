'use client';

import { useState, useEffect, useRef } from 'react';

export default function CommandCenter() {
  const [prompt, setPrompt] = useState('');
  const [chatHistory, setChatHistory] = useState<{role: string, text: string}[]>([]);
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const [isWorking, setIsWorking] = useState(false);
  
  const ws = useRef<WebSocket | null>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll terminal
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [terminalLogs]);

  useEffect(() => {
    // Connect to the Python FastAPI backend
ws.current = new WebSocket('ws://187.77.185.252:8000/ws/session-1');
    
    ws.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      
      // Manage the "Stop Agent" button state
      if (msg.type === 'status' && msg.data.includes("Agent analyzing task")) {
        setIsWorking(true);
      } else if (msg.type === 'agent_msg' || msg.type === 'error') {
        setIsWorking(false);
      }

      if (msg.type === 'thought') {
        setChatHistory(prev => [...prev, { role: 'ai-thought', text: msg.data }]);
      } else if (msg.type === 'agent_msg') {
        setChatHistory(prev => [...prev, { role: 'ai', text: msg.data }]);
      } else if (msg.type === 'terminal_cmd') {
        setTerminalLogs(prev => [...prev, `<span class="text-blue-400">${msg.data}</span>`]);
      } else if (msg.type === 'terminal_out') {
        setTerminalLogs(prev => [...prev, msg.data]);
      } else if (msg.type === 'status' || msg.type === 'error') {
        setTerminalLogs(prev => [...prev, `<span class="text-yellow-400">[SYSTEM]: ${msg.data}</span>`]);
      }
    };

    return () => ws.current?.close();
  }, []);

  const sendPrompt = () => {
    if (!prompt.trim()) return;
    
    setChatHistory(prev => [...prev, { role: 'user', text: prompt }]);
    
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ prompt }));
    }
    setPrompt('');
  };

  const triggerKillSwitch = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'kill' }));
      setIsWorking(false);
    }
  };

  return (
    <div className="flex h-screen bg-neutral-900 text-white font-sans overflow-hidden">
      
      {/* LEFT: Sidebar */}
      <div className="w-64 border-r border-neutral-700 bg-neutral-950 p-4 flex flex-col">
        <button className="bg-blue-600 hover:bg-blue-500 text-white rounded-lg py-2 px-4 mb-6 transition">
          + New Task
        </button>
        <div className="text-sm text-neutral-400 font-semibold mb-2">ACTIVE SESSIONS</div>
        <div className="bg-neutral-800 p-2 rounded cursor-pointer border-l-2 border-blue-500 text-sm">
          VPS Setup Task
        </div>
      </div>

      {/* MIDDLE: Chat Interface */}
      <div className="flex-1 flex flex-col border-r border-neutral-700">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {chatHistory.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-xl p-4 ${
                msg.role === 'user' ? 'bg-blue-600 text-white' : 
                msg.role === 'ai-thought' ? 'bg-neutral-800 text-neutral-300 italic border border-neutral-700' :
                'bg-neutral-800 text-white'
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>
        
        {/* Input Area */}
        <div className="p-4 bg-neutral-900">
          <div className="flex bg-neutral-800 rounded-full border border-neutral-700 p-2 focus-within:border-blue-500 transition">
            <input 
              className="flex-1 bg-transparent border-none outline-none px-4 text-white placeholder-neutral-500 disabled:opacity-50"
              placeholder="Tell Super Hands what to build..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !isWorking && sendPrompt()}
              disabled={isWorking}
            />
            {isWorking ? (
              <button onClick={triggerKillSwitch} className="bg-red-600 text-white rounded-full px-6 py-2 font-bold hover:bg-red-500 animate-pulse">
                STOP AGENT
              </button>
            ) : (
              <button onClick={sendPrompt} className="bg-white text-black rounded-full px-6 py-2 font-medium hover:bg-neutral-200">
                Send
              </button>
            )}
          </div>
        </div>
      </div>

      {/* RIGHT: Live Terminal */}
      <div className="w-[500px] bg-black p-4 flex flex-col font-mono text-sm shadow-2xl border-l border-neutral-800">
        <div className="text-neutral-500 mb-2 border-b border-neutral-800 pb-2 flex justify-between">
          <span>TERMINAL // SUPER-HANDS-OS</span>
          <span className="text-green-500">● LIVE</span>
        </div>
        <div className="flex-1 overflow-y-auto whitespace-pre-wrap">
          {terminalLogs.map((log, idx) => (
            <div key={idx} className="mb-1" dangerouslySetInnerHTML={{ __html: log }} />
          ))}
          <div ref={terminalEndRef} />
        </div>
      </div>

    </div>
  );
}
