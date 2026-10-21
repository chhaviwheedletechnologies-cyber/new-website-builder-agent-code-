import React, { useState, useRef, useEffect } from 'react';

function App() {
  const [view, setView] = useState('landing'); // 'landing', 'building', 'preview'
  const [logs, setLogs] = useState([]);
  const [previewUrl, setPreviewUrl] = useState('');
  const [runId, setRunId] = useState('');

  const [showSettings, setShowSettings] = useState(false);

  // Form State
  const [objective, setObjective] = useState("");
  const [industry, setIndustry] = useState("");
  const [audience, setAudience] = useState("");
  const [brandCtx, setBrandCtx] = useState("");
  const [primaryColor, setPrimaryColor] = useState("#6C63FF");
  const [secondaryColor, setSecondaryColor] = useState("#FF6584");
  const [targetPages, setTargetPages] = useState("Home, Our Story, Contact Us");
  const [logoFile, setLogoFile] = useState(null);
  const [logoData, setLogoData] = useState("");

  const handleLogoUpload = (e) => {
    const file = e.target.files?.[0] || e.dataTransfer?.files?.[0];
    if (file) {
      setLogoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setLogoData(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleGenerate = async () => {
    if (!objective.trim()) return;

    setView('building');
    setLogs([]);
    setPreviewUrl('');
    setRunId('');

    const payload = {
      objective: objective,
      budget: 1500,
      industry: industry,
      target_audience: audience,
      website_url: "",
      brand_context: brandCtx,
      brand_color: primaryColor,
      secondary_color: secondaryColor,
      logo_data: logoData,
      target_pages: targetPages.split(',').map(s => s.trim())
    };

    const interval_id = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8001/output/status.txt?t=${Date.now()}`);
        if (res.ok) {
          const text = await res.text();
          if (text.length > 5) {
            setLogs(text.split('\n').filter(l => l.trim().length > 0));
          }
        }
      } catch (e) {
        // silent
      }
    }, 500);

    try {
      const response = await fetch('http://localhost:8001/api/v1/run-campaign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      clearInterval(interval_id);

      if (data && data.execution_results && data.execution_results.run_id) {
        const rid = data.execution_results.run_id;
        setRunId(rid);
        setPreviewUrl(`http://localhost:8001/output/templates/template_${rid}/index.html`);
        setView('preview');
      } else {
        setLogs(prev => [...prev, "❌ Failed to retrieve preview URL from backend."]);
      }
    } catch (err) {
      clearInterval(interval_id);
      setLogs(prev => [...prev, `❌ Error reaching backend: ${err.message}`]);
    }
  };

  if (view === 'preview') {
    return (
      <div className="preview-view">
        <div className="preview-header">
          <div className="nav-brand" style={{ cursor: 'pointer' }} onClick={() => setView('landing')}>
            <h1><span style={{ color: '#3b82f6' }}>W</span> HEEDLE <span>AI</span></h1>
          </div>
          <div className="nav-actions">
            <a href={`http://localhost:8001/api/v1/download/${runId}.zip`} download>
              <button style={{ background: '#27C93F', color: '#000' }}>📦 Download Source Code (.zip)</button>
            </a>
            <button onClick={() => setView('landing')}>Create New</button>
          </div>
        </div>
        <iframe
          key={previewUrl}
          src={previewUrl}
          className="preview-iframe"
          title="Website Preview"
        ></iframe>
      </div>
    );
  }

  if (view === 'building') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
        <nav className="top-nav" style={{ position: 'relative', background: '#0a0a0c', borderBottom: '1px solid rgba(255,255,255,0.08)', padding: '20px 24px', height: '64px' }}>
          <div className="nav-brand">
            <h1><span style={{ color: '#ffffffff' }}>W</span> HEEDLE <span>AI</span></h1>
          </div>
        </nav>

        <div className="building-viewport">
          {/* Left Side: Execution Logs */}
          <div className="build-logs-sidebar">
            <div className="build-logs-header">
              Execution Trace
            </div>
            <div className="build-logs-container">
              {logs.map((log, index) => {
                const isSuccess = log.includes('✓') || log.includes('✅');
                return (
                  <div key={index} className={`log-line ${isSuccess ? 'success' : ''}`}>
                    <span style={{ color: '#444', marginRight: '12px' }}>{new Date().toISOString().split('T')[1].substring(0, 8)}</span>
                    {log}
                  </div>
                );
              })}
              <div style={{ display: 'flex', alignItems: 'center', marginTop: '24px' }}>
                <div style={{ width: '8px', height: '8px', background: '#00FF41', borderRadius: '50%', marginRight: '12px', animation: 'blink 1s infinite' }}></div>
                <span style={{ opacity: 0.7 }}>Awaiting Next Operation...</span>
              </div>
              <style>{`@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }`}</style>
            </div>
          </div>

          {/* Right Side: Generative Canvas */}
          <div className="generative-canvas">
            <div className="canvas-overlay"></div>
            <div className="scanning-bar"></div>

            <div className="building-indicator">
              <div className="spinner"></div>
              <div>
                <h2 style={{ fontSize: '1.4rem', marginBottom: '8px', color: '#fff', letterSpacing: '-0.5px' }}>Synthesizing interface...</h2>
                <p style={{ color: '#888899', fontSize: '0.95rem' }}>Assembling components, optimizing layout, and generating CSS.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <nav className="top-nav">
        <div className="nav-brand">
          <h1><span style={{ color: '#ffffffff' }}>W</span> HEEDLE <span>AI</span></h1>
        </div>
      </nav>

      <div className="landing-view">
        <div className="hero-text">
          <h1>Build stunning websites<br />in seconds with AI.</h1>
          <p style={{ maxWidth: '800px', margin: '16px auto 0' }}>Describe your vision, and our intelligent engine will autonomously generate a complete, high-performance website tailored exactly to your brand.</p>
        </div>

        <div className="generator-console">
          <div className="prompt-area">
            <div className="prompt-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>
            </div>
            <textarea
              className="main-prompt"
              placeholder="what you want to build............."
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleGenerate(); } }}
            ></textarea>
          </div>

          <div className="settings-panel">
            <div className="setting-group">
              <label>Industry</label>
              <input type="text" placeholder="e.g. Retail Shoe Shop" value={industry} onChange={e => setIndustry(e.target.value)} />
            </div>
            <div className="setting-group">
              <label>Audience</label>
              <input type="text" placeholder="e.g. Athletes" value={audience} onChange={e => setAudience(e.target.value)} />
            </div>
            <div className="setting-group">
              <label>Target Pages</label>
              <input type="text" placeholder="Home, About, Contact" value={targetPages} onChange={e => setTargetPages(e.target.value)} />
            </div>
            <div className="setting-group" style={{ display: 'flex', flexDirection: 'row', gap: '8px' }}>
              <div style={{ flex: 1 }}>
                <label>Primary</label>
                <input type="color" value={primaryColor} onChange={e => setPrimaryColor(e.target.value)} />
              </div>
              <div style={{ flex: 1 }}>
                <label>Secondary</label>
                <input type="color" value={secondaryColor} onChange={e => setSecondaryColor(e.target.value)} />
              </div>
            </div>
            <div className="setting-group" style={{ gridColumn: 'span 2' }}>
              <label>Brand Context & Vibes</label>
              <textarea placeholder="e.g. Modern, sleek, athletic..." value={brandCtx} onChange={e => setBrandCtx(e.target.value)}></textarea>
            </div>
          </div>

          <div className="console-actions">
            <div className="action-chips">

              <div style={{ position: 'relative' }}>
                <input id="logo-upload" type="file" hidden accept="image/*" onChange={handleLogoUpload} />
                <button onClick={() => document.getElementById('logo-upload').click()} style={{ background: logoFile ? 'rgba(0, 255, 65, 0.15)' : '', color: logoFile ? '#00FF41' : '' }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
                  {logoFile ? `✅ ${logoFile.name}` : 'Upload Logo'}
                </button>
              </div>

              <button onClick={() => { setObjective("I want a sleek dark-mode landing page for my new AI crypto startup."); }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><line x1="9" y1="3" x2="9" y2="21" /></svg>
                Use a template
              </button>
            </div>

            <button className="submit-btn" onClick={handleGenerate} disabled={!objective.trim()}>
              ↑
            </button>
          </div>
        </div>

      </div>
    </>
  );
}

export default App;
