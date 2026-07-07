import React, { useState, useEffect, useRef } from 'react';
import { 
  Database, 
  MessageSquare, 
  FileText, 
  Settings, 
  Send, 
  ChevronRight, 
  Cpu, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw,
  Search,
  BookOpen,
  Brain,
  TrendingUp,
  X,
  Sun,
  Moon,
  Upload
} from 'lucide-react';
import { 
  fetchHealth, 
  triggerIngestion, 
  sendQuery, 
  sendResearch, 
  fetchMemory, 
  saveMemory, 
  runEvals,
  uploadDocument,
  fetchUploadedDocuments
} from './api';
import './App.css';

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [activeTab, setActiveTab] = useState('chat');
  const [sessionId, setSessionId] = useState(() => 'session_' + Math.random().toString(36).substring(2, 9));
  const [dbHealth, setDbHealth] = useState({ status: 'ok', sqlite: 'ok', chromadb: 'ok' });
  const [isIngesting, setIsIngesting] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [isResearching, setIsResearching] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadedOnly, setUploadedOnly] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState([]);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    if (nextTheme === 'light') {
      document.documentElement.classList.add('light-theme');
    } else {
      document.documentElement.classList.remove('light-theme');
    }
  };
  
  // Chat States
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hello! I am your Product Intelligence Analyst. I can query our SaaS knowledge base (PRDs, support tickets, meeting notes, release notes) and compile research reports. Ask me anything!',
      citations: []
    }
  ]);
  const messagesEndRef = useRef(null);

  // Research States
  const [researchQuery, setResearchQuery] = useState('');
  const [researchReport, setResearchReport] = useState('');
  const [researchCitations, setResearchCitations] = useState([]);
  const [activeStep, setActiveStep] = useState(0); // 0 = idle, 1 = planning, 2 = retrieving, 3 = analyzing, 4 = validating, 5 = writing, 6 = complete

  // Memory States
  const [memories, setMemories] = useState([]);
  const [newMemoryText, setNewMemoryText] = useState('');
  const [newMemoryType, setNewMemoryType] = useState('insight');

  // Evaluation States
  const [evalResults, setEvalResults] = useState(null);

  // Citation Detail Panel
  const [activeDoc, setActiveDoc] = useState(null);

  // Fetch Health & Memory on Load
  useEffect(() => {
    loadHealth();
    loadMemories();
    loadUploadedDocs();
    const interval = setInterval(loadHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    loadMemories();
    loadUploadedDocs();
  }, [sessionId]);

  useEffect(() => {
    // Scroll chat to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadUploadedDocs = async () => {
    try {
      const docs = await fetchUploadedDocuments(sessionId);
      setUploadedDocs(docs);
    } catch (e) {
      console.error("Failed to load uploaded documents", e);
    }
  };

  const loadHealth = async () => {
    try {
      const health = await fetchHealth();
      setDbHealth(health);
    } catch (e) {
      setDbHealth({ status: 'error', sqlite: 'error', chromadb: 'error' });
    }
  };

  const loadMemories = async () => {
    if (!sessionId) return;
    try {
      const mems = await fetchMemory(sessionId);
      setMemories(mems);
    } catch (e) {
      console.error("Failed to load memory", e);
    }
  };

  const handleIngest = async () => {
    setIsIngesting(true);
    try {
      await triggerIngestion();
      await loadHealth();
      alert("Successfully ingested 1,000 synthetic documents into SQLite and ChromaDB!");
    } catch (e) {
      alert("Ingestion failed: " + e.message);
    } finally {
      setIsIngesting(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setIsUploading(true);
    setUploadStatus({ type: 'info', message: `Uploading ${file.name}...` });
    
    try {
      const res = await uploadDocument(file, sessionId);
      setUploadStatus({ 
        type: 'success', 
        message: `Successfully ingested ${res.filename}!` 
      });
      loadHealth();
      loadUploadedDocs();
    } catch (err) {
      console.error(err);
      setUploadStatus({ type: 'error', message: err.message || 'Upload failed.' });
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadStatus(null), 5000);
      e.target.value = null; // Reset input
    }
  };

  const handleSendQuery = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userText = chatInput;
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setChatInput('');
    setIsQuerying(true);

    try {
      const resp = await sendQuery(userText, sessionId, uploadedOnly);
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: resp.answer,
        citations: resp.citations || []
      }]);
      // Reload memories in case new insights were appended
      loadMemories();
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: 'Error generating response: ' + err.message,
        citations: []
      }]);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleSendResearch = async (e) => {
    e.preventDefault();
    if (!researchQuery.trim()) return;

    setIsResearching(true);
    setResearchReport('');
    setResearchCitations([]);
    setActiveStep(1); // Stage 1: Planning

    // Fake agent visual progress indicator interval while API executes
    const stepInterval = setInterval(() => {
      setActiveStep(prev => {
        if (prev < 5) return prev + 1;
        return prev;
      });
    }, 4500);

    try {
      const resp = await sendResearch(researchQuery, sessionId);
      clearInterval(stepInterval);
      setActiveStep(6); // Step 6: Complete
      setResearchReport(resp.summary);
      setResearchCitations(resp.citations || []);
      loadMemories();
    } catch (err) {
      clearInterval(stepInterval);
      setActiveStep(0);
      alert("Research orchestration failed: " + err.message);
    } finally {
      setIsResearching(false);
    }
  };

  const handleAddMemory = async (e) => {
    e.preventDefault();
    if (!newMemoryText.trim() || !sessionId) return;
    try {
      await saveMemory(sessionId, newMemoryType, newMemoryText);
      setNewMemoryText('');
      loadMemories();
    } catch (e) {
      alert("Failed to save memory: " + e.message);
    }
  };

  const handleRunEvals = async () => {
    setIsEvaluating(true);
    try {
      const results = await runEvals();
      setEvalResults(results);
    } catch (e) {
      alert("Failed to run evaluation harness: " + e.message);
    } finally {
      setIsEvaluating(false);
    }
  };

  // Simple parser to render markdown formatting safely in Vanilla HTML
  const renderMarkdown = (text) => {
    if (!text) return '';
    let html = text
      .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
      .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
      .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^\- (.*?)$/gm, '<li>$1</li>');
    
    // Wrap consecutive list items in <ul>
    html = html.replace(/(<li>.*?<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`);
    
    // Convert remaining lines (excluding headings, tags, dividers) to paragraphs
    html = html.split('\n').map(line => {
      line = line.trim();
      if (!line) return '';
      if (line.startsWith('<h') || line.startsWith('<l') || line.startsWith('<u') || line.startsWith('---')) return line;
      return `<p>${line}</p>`;
    }).join('\n');

    return { __html: html };
  };

  return (
    <div className="app-container">
      {/* Sidebar Control Panel */}
      <aside className="sidebar">
        <div className="logo-container">
          <Brain className="logo-icon-animate text-primary" size={28} />
          <h1 className="logo-text">ProdIntel Analyst</h1>
        </div>

        {/* Health Panel */}
        <div className="glass-card">
          <h2 className="section-title">System Status</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>SQLite Metadata</span>
              <span className={`status-pill ${dbHealth.sqlite === 'ok' ? 'ok' : 'error'}`}>
                <span className="status-dot"></span>
                {dbHealth.sqlite === 'ok' ? 'OK' : 'Error'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>ChromaDB Index</span>
              <span className={`status-pill ${dbHealth.chromadb === 'ok' ? 'ok' : 'error'}`}>
                <span className="status-dot"></span>
                {dbHealth.chromadb === 'ok' ? 'OK' : 'Error'}
              </span>
            </div>
          </div>
        </div>

        {/* Session Selector */}
        <div className="glass-card">
          <h2 className="section-title">Session Manager</h2>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Active Session ID</label>
          <input 
            type="text" 
            value={sessionId} 
            onChange={(e) => setSessionId(e.target.value)} 
            className="input-field"
            placeholder="e.g. session_001"
          />
        </div>

        {/* Ingestion control */}
        <div className="glass-card" style={{ marginTop: 'auto' }}>
          <h2 className="section-title">Knowledge Base</h2>
          
          <button onClick={handleIngest} disabled={isIngesting || isUploading} className="btn-primary" style={{ marginBottom: '12px', width: '100%' }}>
            {isIngesting ? (
              <RefreshCw className="animate-spin" size={16} />
            ) : (
              <Database size={16} />
            )}
            {isIngesting ? "Ingesting..." : "Re-Ingest 1K Docs"}
          </button>

          <div style={{ borderTop: '1px solid var(--glass-border)', margin: '12px 0' }}></div>

          <label className="btn-primary" style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            gap: '8px', 
            cursor: isUploading ? 'not-allowed' : 'pointer',
            background: 'transparent',
            border: '1px dashed var(--primary)',
            color: 'var(--primary)',
            padding: '10px',
            opacity: isUploading ? 0.6 : 1
          }}>
            {isUploading ? <RefreshCw className="animate-spin" size={16} /> : <Upload size={16} />}
            {isUploading ? "Uploading..." : "Upload Document"}
            <input 
              type="file" 
              accept=".txt,.json,.docx,.pdf" 
              onChange={handleFileUpload} 
              disabled={isUploading}
              style={{ display: 'none' }} 
            />
          </label>

          {uploadStatus && (
            <div style={{ 
              marginTop: '10px', 
              padding: '8px', 
              borderRadius: '4px', 
              fontSize: '0.75rem',
              background: uploadStatus.type === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(0, 237, 100, 0.1)',
              border: uploadStatus.type === 'error' ? '1px solid rgba(239, 68, 68, 0.2)' : '1px solid rgba(0, 237, 100, 0.2)',
              color: uploadStatus.type === 'error' ? '#ef4444' : 'var(--primary)',
              wordBreak: 'break-all'
            }}>
              {uploadStatus.message}
            </div>
          )}

          {uploadedDocs.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <div style={{ 
                fontSize: '0.7rem', 
                fontWeight: 700, 
                color: 'var(--text-muted)', 
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Uploaded files ({uploadedDocs.length})
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '150px', overflowY: 'auto' }}>
                {uploadedDocs.map((doc) => {
                  const docExt = doc.source_type.split('_')[1]?.toUpperCase() || 'TXT';
                  return (
                    <div 
                      key={doc.id} 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '8px', 
                        padding: '6px 8px', 
                        background: 'rgba(255,255,255,0.02)', 
                        border: '1px solid var(--glass-border)',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        color: 'var(--text-primary)'
                      }}
                      title={doc.title}
                    >
                      <FileText size={12} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                      <span style={{ 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis', 
                        whiteSpace: 'nowrap',
                        flex: 1
                      }}>
                        {doc.title}
                      </span>
                      <span style={{ 
                        fontSize: '0.65rem', 
                        background: 'rgba(0, 237, 100, 0.1)', 
                        color: 'var(--primary)', 
                        padding: '1px 4px', 
                        borderRadius: '3px',
                        fontWeight: 600
                      }}>
                        {docExt}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Workspace */}
      <main className="main-content">
        <header className="header">
          <div className="tab-nav">
            <button 
              onClick={() => setActiveTab('chat')} 
              className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            >
              <MessageSquare size={16} />
              Q&A Chat
            </button>
            <button 
              onClick={() => setActiveTab('research')} 
              className={`tab-btn ${activeTab === 'research' ? 'active' : ''}`}
            >
              <FileText size={16} />
              Deep Research Board
            </button>
            <button 
              onClick={() => setActiveTab('evals')} 
              className={`tab-btn ${activeTab === 'evals' ? 'active' : ''}`}
            >
              <TrendingUp size={16} />
              Evaluations
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Session:</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--primary)' }}>{sessionId}</span>
            </div>
            <button 
              onClick={toggleTheme} 
              className="tab-btn theme-transition-all"
              style={{ border: '1px solid var(--glass-border)', padding: '6px 12px', borderRadius: '8px' }}
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            >
              {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
              <span style={{ fontSize: '0.8rem' }}>{theme === 'dark' ? 'Light' : 'Dark'}</span>
            </button>
          </div>
        </header>

        {/* Dynamic Workspace Container */}
        <div className="tab-content">
          
          {/* 1. CHAT WORKSPACE */}
          {activeTab === 'chat' && (
            <div className="chat-layout">
              {/* Messages Viewport */}
              <div className="messages-viewport">
                {messages.map((m, idx) => (
                  <div key={idx} className={`message-card ${m.role}`}>
                    <span className="message-author">{m.role === 'user' ? 'User' : 'Llama Analyst'}</span>
                    <div className="message-bubble">
                      <div dangerouslySetInnerHTML={renderMarkdown(m.text)} />
                      
                      {/* Citations block */}
                      {m.citations && m.citations.length > 0 && (
                        <div className="citation-container">
                          <span className="citation-header">Evidence Citations</span>
                          <div className="citation-chips">
                            {m.citations.map((c, cIdx) => (
                              <button 
                                key={cIdx} 
                                onClick={() => setActiveDoc(c)}
                                className="citation-chip"
                              >
                                <BookOpen size={12} />
                                {c.id}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isQuerying && (
                  <div className="message-card assistant">
                    <span className="message-author">Llama Analyst</span>
                    <div className="message-bubble" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <RefreshCw className="animate-spin text-primary" size={16} />
                      Thinking...
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Composer */}
              <div className="input-composer">
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px', 
                  marginBottom: '10px',
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)'
                }}>
                  <input 
                    type="checkbox" 
                    id="uploaded-only-toggle"
                    checked={uploadedOnly}
                    onChange={(e) => setUploadedOnly(e.target.checked)}
                    style={{ 
                      accentColor: 'var(--primary)',
                      cursor: 'pointer',
                      width: '14px',
                      height: '14px'
                    }}
                  />
                  <label htmlFor="uploaded-only-toggle" style={{ cursor: 'pointer', userSelect: 'none' }}>
                    Search / Chat with uploaded documents only
                  </label>
                </div>
                <form onSubmit={handleSendQuery} className="composer-form">
                  <input 
                    type="text" 
                    value={chatInput} 
                    onChange={(e) => setChatInput(e.target.value)} 
                    placeholder="Ask a question about SaaS telemetry, latency, billing or tickets..." 
                    className="input-field"
                    disabled={isQuerying}
                  />
                  <button type="submit" className="btn-primary" style={{ width: 'auto' }} disabled={isQuerying}>
                    <Send size={16} />
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* 2. DEEP RESEARCH WORKSPACE */}
          {activeTab === 'research' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div className="glass-card">
                <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', fontFamily: 'Outfit' }}>Multi-Agent Deep Research</h2>
                <form onSubmit={handleSendResearch} style={{ display: 'flex', gap: '12px' }}>
                  <input 
                    type="text" 
                    value={researchQuery} 
                    onChange={(e) => setResearchQuery(e.target.value)} 
                    placeholder="Input a query to trigger sequential research (e.g. 'Analyze search ticket complaints')" 
                    className="input-field"
                    disabled={isResearching}
                  />
                  <button type="submit" className="btn-primary" style={{ width: '160px' }} disabled={isResearching}>
                    {isResearching ? <RefreshCw className="animate-spin" size={16} /> : <Cpu size={16} />}
                    {isResearching ? "Running..." : "Start Research"}
                  </button>
                </form>
              </div>

              {/* Agent Pipeline Stepper */}
              {activeStep > 0 && (
                <div className="glass-card">
                  <div className="pipeline-container">
                    <h3 className="section-title">Agent Workflow Status</h3>
                    <div className="pipeline-steps">
                      <div className="pipeline-line"></div>
                      {[
                        { num: 1, label: 'Planner' },
                        { num: 2, label: 'Retrieval' },
                        { num: 3, label: 'Analysis' },
                        { num: 4, label: 'Validation' },
                        { num: 5, label: 'Report Writer' }
                      ].map((step) => {
                        let status = '';
                        if (activeStep > step.num) status = 'completed';
                        else if (activeStep === step.num) status = 'active';
                        
                        return (
                          <div key={step.num} className={`pipeline-step-node ${status}`}>
                            <div className="step-indicator">
                              {status === 'completed' ? <CheckCircle size={14} /> : step.num}
                            </div>
                            <span className="step-label">{step.label}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* Final Report Output */}
              {researchReport && (
                <div className="report-view">
                  <div dangerouslySetInnerHTML={renderMarkdown(researchReport)} />
                  
                  {/* Research Citations */}
                  {researchCitations.length > 0 && (
                    <div style={{ marginTop: '32px', borderTop: '1px solid var(--glass-border)', paddingTop: '16px' }}>
                      <h3 style={{ fontSize: '1rem', marginBottom: '12px', fontWeight: 600 }}>Validated Sources</h3>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        {researchCitations.map((c, idx) => (
                          <button 
                            key={idx} 
                            onClick={() => setActiveDoc(c)}
                            className="citation-chip"
                          >
                            <BookOpen size={12} />
                            {c.id}: {c.title}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* 3. EVALUATION WORKSPACE */}
          {activeTab === 'evals' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', marginBottom: '8px' }}>Benchmark Performance Evaluations</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    Runs 3 gold-standard verification checks covering search, billing, and latency to measure RAG retrieval and answer groundedness.
                  </p>
                </div>
                <button 
                  onClick={handleRunEvals} 
                  disabled={isEvaluating} 
                  className="btn-primary" 
                  style={{ width: '180px' }}
                >
                  {isEvaluating ? <RefreshCw className="animate-spin" size={16} /> : <Settings size={16} />}
                  {isEvaluating ? "Evaluating..." : "Run Evals"}
                </button>
              </div>

              {evalResults && (
                <>
                  {/* Metrics Cards Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                    {[
                      { title: 'Average Retrieval Precision', val: evalResults.average_precision, desc: 'Relevance of retrieved chunks' },
                      { title: 'Average Retrieval Recall', val: evalResults.average_recall, desc: 'Coverage of gold documents' },
                      { title: 'Average Answer Groundedness', val: evalResults.average_groundedness, desc: 'Presence of expected facts' }
                    ].map((metric, idx) => (
                      <div key={idx} className="glass-card" style={{ textAlign: 'center', padding: '24px' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                          {metric.title}
                        </span>
                        <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary)', margin: '8px 0' }}>
                          {Math.round(metric.val * 100)}%
                        </div>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{metric.desc}</p>
                      </div>
                    ))}
                  </div>

                  {/* Detailed Evals Table */}
                  <div className="glass-card">
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px' }}>Detailed Query Performance</h3>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                          <th style={{ padding: '12px' }}>Query</th>
                          <th style={{ padding: '12px' }}>Precision</th>
                          <th style={{ padding: '12px' }}>Recall</th>
                          <th style={{ padding: '12px' }}>Groundedness</th>
                        </tr>
                      </thead>
                      <tbody>
                        {evalResults.results.map((res, idx) => (
                          <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.02)' }}>
                            <td style={{ padding: '12px', fontWeight: 500 }}>"{res.query}"</td>
                            <td style={{ padding: '12px', color: 'var(--primary)' }}>{Math.round(res.precision * 100)}%</td>
                            <td style={{ padding: '12px', color: 'var(--secondary)' }}>{Math.round(res.recall * 100)}%</td>
                            <td style={{ padding: '12px', color: 'var(--success)' }}>{Math.round(res.groundedness * 100)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          )}

        </div>
      </main>

      {/* Floating Citation Document Drawer */}
      {activeDoc && (
        <>
          <div className="drawer-backdrop" onClick={() => setActiveDoc(null)}></div>
          <div className="drawer">
            <div className="drawer-header">
              <span className="status-pill ok" style={{ textTransform: 'uppercase' }}>
                {activeDoc.source_type || 'document'}
              </span>
              <button className="drawer-close" onClick={() => setActiveDoc(null)}>
                <X size={20} />
              </button>
            </div>
            
            <div className="drawer-content">
              <h2 className="drawer-title">{activeDoc.title || 'Source Citation'}</h2>
              
              <div className="drawer-meta-grid">
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Document ID</span>
                  <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>{activeDoc.id || activeDoc.doc_id}</p>
                </div>
              </div>

              <div className="drawer-body">
                {activeDoc.text || activeDoc.body}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
