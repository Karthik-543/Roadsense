import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  Send, 
  Bot, 
  User as UserIcon, 
  Sparkles, 
  BookOpen, 
  Clock, 
  AlertCircle, 
  FileText, 
  ChevronDown, 
  ChevronUp, 
  Cpu, 
  Lightbulb, 
  RefreshCw,
  Info
} from 'lucide-react';
import { askRoadSense } from '../services/api';
import { ChatMessage, CitationItem } from '../types';

export const AskRoadSensePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialAssessmentId = searchParams.get('assessmentId') || '';

  const [assessmentId, setAssessmentId] = useState(initialAssessmentId);
  const [ragMode, setRagMode] = useState<string>('EVIDENCE_AWARE_ADAPTIVE_RAG');
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'assistant',
      text: 'Hello! I am RoadSense AI Assistant powered by Evidence-Aware Adaptive RAG. Ask me anything about pavement engineering standards, structural defect analysis, weather/traffic impacts, or repair strategies.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const suggestedQuestions = [
    'What standard repair procedure applies to severe alligator cracking?',
    'How does 20mm rainfall impact structural degradation of potholes?',
    'When should a road defect require full-depth patching vs cold mix?',
    'What safety protocols apply to highway lane closures during crack sealing?'
  ];

  const handleSend = async (queryToSend?: string) => {
    const query = queryToSend || inputQuery;
    if (!query.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryToSend) setInputQuery('');
    setLoading(true);
    setError(null);

    try {
      const response = await askRoadSense(query, assessmentId || undefined, ragMode);
      
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: response.answer || 'No response text available.',
        citations: response.citations?.map((c: any) => ({
          sourceId: c.source_id || c.sourceId || 'SRC',
          title: c.title || c.document || 'Engineering Manual',
          page: c.page || 1,
          chunkId: c.chunk_id || c.chunkId || ''
        })),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message || 'Failed to reach RoadSense RAG service');
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: '⚠️ An error occurred while retrieving information from the Evidence-Aware RAG service. Please ensure the backend and RAG engine are running.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleCitations = (msgId: string) => {
    setExpandedCitations((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-blue-600" />
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              Ask RoadSense AI Assistant
            </h1>
          </div>
          <p className="mt-1 text-sm text-slate-600">
            Query verified civil engineering standards, pavement distress manuals, and assessment context.
          </p>
        </div>

        {/* Model Selector & Assessment Context Control */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-200">
            <Cpu className="w-4 h-4 text-slate-500" />
            <span className="text-xs font-semibold text-slate-600">RAG System:</span>
            <select
              value={ragMode}
              onChange={(e) => setRagMode(e.target.value)}
              className="bg-white border border-slate-200 text-xs rounded font-medium text-slate-800 p-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="EVIDENCE_AWARE_ADAPTIVE_RAG">
                Evidence-Aware Adaptive RAG (Recommended)
              </option>
              <option value="EVIDENCE_AWARE_RAG">
                Evidence-Aware RAG
              </option>
              <option value="STANDARD_RAG">
                Standard RAG Baseline
              </option>
            </select>
          </div>

          {initialAssessmentId && (
            <div className="bg-blue-50 border border-blue-200 text-blue-800 text-xs px-3 py-2 rounded-lg font-mono flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-blue-600" />
              Context: #{initialAssessmentId}
            </div>
          )}
        </div>
      </div>

      {/* RAG System Disclaimer Banner */}
      <div className="bg-blue-50/70 border border-blue-200 rounded-lg p-3 text-xs text-blue-900 flex items-start gap-2.5">
        <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Official Research RAG Comparison Subsystem:</span> Responses are retrieved strictly from verified civil engineering literature with exact page/chunk citations to ensure high precision and zero hallucination.
        </div>
      </div>

      {/* Chat Messages Window */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[520px]">
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            const hasCitations = msg.citations && msg.citations.length > 0;
            const isExpanded = expandedCitations[msg.id];

            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 text-white shadow-sm ${
                    isUser ? 'bg-slate-800' : 'bg-gradient-to-br from-blue-600 to-indigo-700'
                  }`}
                >
                  {isUser ? <UserIcon className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                </div>

                {/* Message Box */}
                <div className="space-y-2 flex-1">
                  <div
                    className={`p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${
                      isUser
                        ? 'bg-blue-600 text-white rounded-tr-none'
                        : 'bg-slate-50 text-slate-800 border border-slate-200 rounded-tl-none'
                    }`}
                  >
                    <div className="whitespace-pre-line">{msg.text}</div>
                    <div
                      className={`text-[10px] mt-2 font-mono flex items-center justify-end gap-1 ${
                        isUser ? 'text-blue-100' : 'text-slate-400'
                      }`}
                    >
                      <Clock className="w-3 h-3" />
                      {msg.timestamp}
                    </div>
                  </div>

                  {/* Citations Card (for assistant) */}
                  {!isUser && hasCitations && (
                    <div className="bg-purple-50/70 border border-purple-200 rounded-xl p-3 space-y-2">
                      <button
                        onClick={() => toggleCitations(msg.id)}
                        className="flex items-center justify-between w-full text-xs font-semibold text-purple-900 hover:text-purple-700"
                      >
                        <span className="flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5 text-purple-600" />
                          Verified Citations & Literature Sources ({msg.citations!.length})
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-purple-600" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-purple-600" />
                        )}
                      </button>

                      {isExpanded && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-purple-200">
                          {msg.citations!.map((cit, idx) => (
                            <div
                              key={idx}
                              className="bg-white p-2.5 rounded-lg border border-purple-100 shadow-2xs text-xs space-y-0.5"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-purple-700 font-mono text-[11px]">
                                  [{cit.sourceId || idx + 1}]
                                </span>
                                <span className="text-[10px] text-slate-400 font-mono">
                                  Page {cit.page || 1}
                                </span>
                              </div>
                              <div className="font-medium text-slate-900 line-clamp-1">{cit.title}</div>
                              <div className="text-[10px] text-slate-400 font-mono truncate">
                                Chunk: {cit.chunkId}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex gap-3 max-w-3xl">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 text-white flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5 animate-pulse" />
              </div>
              <div className="bg-slate-50 p-4 rounded-2xl rounded-tl-none border border-slate-200 text-sm text-slate-500 flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                <span>Executing Evidence-Aware RAG retrieval & verification...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Question Chips */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500">
            <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
            <span>Suggested Questions:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                disabled={loading}
                className="text-xs bg-white border border-slate-200 text-slate-700 hover:border-blue-400 hover:text-blue-700 px-3 py-1.5 rounded-full transition text-left"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-white border-t border-slate-200">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-3"
          >
            <input
              type="text"
              placeholder="Ask a question about road damage, standards, or repair options..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              disabled={loading}
              className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900"
            />
            <button
              type="submit"
              disabled={loading || !inputQuery.trim()}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium text-sm rounded-xl transition flex items-center gap-2 shadow-sm"
            >
              <span>Send</span>
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
