const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchHealth() {
  const resp = await fetch(`${API_BASE_URL}/health`);
  if (!resp.ok) throw new Error('Health check failed');
  return resp.json();
}

export async function triggerIngestion() {
  const resp = await fetch(`${API_BASE_URL}/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!resp.ok) throw new Error('Ingestion failed');
  return resp.json();
}

export async function uploadDocument(file, sessionId) {
  const formData = new FormData();
  formData.append('file', file);
  
  let url = `${API_BASE_URL}/upload`;
  if (sessionId) {
    url += `?session_id=${encodeURIComponent(sessionId)}`;
  }
  
  const resp = await fetch(url, {
    method: 'POST',
    body: formData,
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Upload failed');
  }
  return resp.json();
}

export async function sendQuery(question, sessionId, uploadedOnly = false) {
  const resp = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      question, 
      session_id: sessionId || null,
      uploaded_only: uploadedOnly
    }),
  });
  if (!resp.ok) throw new Error('Query request failed');
  return resp.json();
}

export async function sendResearch(question, sessionId) {
  const resp = await fetch(`${API_BASE_URL}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId || null }),
  });
  if (!resp.ok) throw new Error('Research request failed');
  return resp.json();
}

export async function fetchMemory(sessionId) {
  if (!sessionId) return [];
  const resp = await fetch(`${API_BASE_URL}/memory/${sessionId}`);
  if (!resp.ok) throw new Error('Failed to fetch memory');
  return resp.json();
}

export async function saveMemory(sessionId, type, content) {
  const resp = await fetch(`${API_BASE_URL}/memory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, type, content }),
  });
  if (!resp.ok) throw new Error('Failed to save memory');
  return resp.json();
}

export async function runEvals() {
  const resp = await fetch(`${API_BASE_URL}/evals/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!resp.ok) throw new Error('Evaluation harness failed');
  return resp.json();
}

export async function fetchUploadedDocuments(sessionId) {
  let url = `${API_BASE_URL}/documents/uploaded`;
  if (sessionId) {
    url += `?session_id=${encodeURIComponent(sessionId)}`;
  }
  const resp = await fetch(url);
  if (!resp.ok) throw new Error('Failed to fetch uploaded documents');
  return resp.json();
}
