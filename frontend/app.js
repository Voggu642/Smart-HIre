const API_BASE = 'http://127.0.0.1:8000';

async function fetchJobs() {
  const res = await fetch(`${API_BASE}/jobs`);
  return res.json();
}

function el(tag, attrs = {}, children = []) {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v]) => {
    if (k === 'class') e.className = v;
    else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.substring(2), v);
    else e.setAttribute(k, v);
  });
  children.forEach(c => e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c));
  return e;
}

async function populateJobs() {
  const jobs = await fetchJobs();
  const sel = document.getElementById('jobSelect');
  sel.innerHTML = '';
  sel.appendChild(el('option', {value:''}, ['Select target job (optional)']));
  jobs.forEach(j => {
    sel.appendChild(el('option', {value: j.id}, [`${j.id} — ${j.title}`]));
  });
}

async function recommend() {
  const resumeText = document.getElementById('resumeText').value;
  const skillsRaw = document.getElementById('skillsInput').value;
  const skills = skillsRaw.split(',').map(s => s.trim()).filter(Boolean);

  const payload = {
    candidate: { resume_text: resumeText, skills },
    top_k: 5
  };

  const res = await fetch(`${API_BASE}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  const list = document.getElementById('recoList');
  list.innerHTML = '';
  data.results.forEach(r => {
    list.appendChild(el('li', {class:'border rounded-xl p-3'}, [
      el('div', {class:'font-medium'}, [`${r.title} (${r.job_id}) — score ${r.score}`]),
      el('div', {class:'text-sm text-gray-700'}, [`Why: ${r.why}`]),
      el('div', {class:'text-xs text-gray-500'}, [`Matched skills: ${r.matched_skills.join(', ')}`])
    ]));
  });
}

async function analyze() {
  const resumeText = document.getElementById('resumeText').value;
  const target_job_id = document.getElementById('jobSelect').value || null;
  const payload = { resume_text: resumeText, target_job_id };

  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  const list = document.getElementById('analyzeList');
  list.innerHTML = '';

  data.suggestions.forEach(s => {
    list.appendChild(el('li', {class:'border rounded-xl p-3 text-sm'}, [
      el('div', {class:'font-medium'}, [s.type.toUpperCase()]),
      el('div', {}, [s.message])
    ]));
  });

  if (data.missing_keywords?.length) {
    list.appendChild(el('li', {class:'border rounded-xl p-3 text-sm bg-yellow-50'}, [
      el('div', {class:'font-medium'}, ['Missing Keywords']),
      el('div', {}, [data.missing_keywords.join(', ')])
    ]));
  }
}

document.getElementById('btnRecommend').addEventListener('click', recommend);
document.getElementById('btnAnalyze').addEventListener('click', analyze);
populateJobs();
