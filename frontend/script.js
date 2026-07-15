const BACKEND_URL='http://127.0.0.1:8000';
const API_URL=`${BACKEND_URL}/generate`;
const CONFIG_URL=`${BACKEND_URL}/config`;
let runtimeConfig={use_ai:false,provider:'local'};
let loadingTimer=null;
function escapeHtml(value){return String(value??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;')}
function setStatus(message,isError=false,isLoading=false){const s=document.getElementById('status');s.textContent=message;s.style.color=isError?'#dc2626':'#0f766e';s.classList.toggle('loading',isLoading)}
function startLoadingStatus(baseMessage){const s=document.getElementById('status');let step=0;clearInterval(loadingTimer);setStatus(baseMessage,false,true);loadingTimer=setInterval(()=>{step=(step+1)%4;s.textContent=`${baseMessage}${'.'.repeat(step)}`},400)}
function stopLoadingStatus(){clearInterval(loadingTimer);loadingTimer=null;document.getElementById('status').classList.remove('loading')}
function formatProviderName(provider){if(provider==='openai')return 'OpenAI';if(provider==='azure')return 'Azure';return 'Local'}
function updateProviderBadge(){const badge=document.getElementById('providerBadge');const provider=runtimeConfig.use_ai?runtimeConfig.provider:'local';badge.textContent=`Provider: ${formatProviderName(provider)}`;badge.className=`provider-badge provider-${provider}`}
async function loadRuntimeConfig(){try{const response=await fetch(CONFIG_URL);if(!response.ok)throw new Error(`Config error: ${response.status}`);runtimeConfig=await response.json()}catch(error){runtimeConfig={use_ai:false,provider:'local'}}updateProviderBadge()}
function bulletList(items){return items.map(i=>`- ${i}`).join('\n')}
function renderList(items){return `<ul class="output-list">${items.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul>`}
function renderTestCases(testCases){return `<div class="test-case-grid">${testCases.map(tc=>`<article class="test-case-card"><div class="test-case-head"><div><h4>${escapeHtml(tc.id)}: ${escapeHtml(tc.title)}</h4><p>${escapeHtml(tc.type)} test case</p></div><div class="test-case-meta"><span>${escapeHtml(tc.priority)}</span><span>${escapeHtml(tc.type)}</span></div></div><div class="output-subsection"><h5>Preconditions</h5>${renderList(tc.preconditions)}</div><div class="output-subsection"><h5>Steps</h5><ol class="output-steps">${tc.steps.map(step=>`<li>${escapeHtml(step)}</li>`).join('')}</ol></div><div class="output-subsection"><h5>Expected Result</h5><p>${escapeHtml(tc.expected_result)}</p></div></article>`).join('')}</div>`}
function renderApiCoverage(items){return `<div class="api-grid">${items.map(item=>`<article class="api-card"><div class="api-method">${escapeHtml(item.method)}</div><div class="api-endpoint">${escapeHtml(item.endpoint)}</div><p>${escapeHtml(item.validation)}</p><span class="api-status">Expected: ${escapeHtml(item.expected_status)}</span></article>`).join('')}</div>`}
function renderAcceptanceMapping(items){return `<div class="mapping-grid">${items.map(item=>`<article class="mapping-card"><h4>${escapeHtml(item.criterion)}</h4><p><strong>Covered By:</strong> ${escapeHtml((item.covered_by||[]).join(', ')||'Not mapped')}</p><p><strong>Notes:</strong> ${escapeHtml(item.notes||'None')}</p></article>`).join('')}</div>`}
function renderSection(title,content,accent=''){return `<section class="output-section ${accent}"><h3>${escapeHtml(title)}</h3>${content}</section>`}
function formatPackage(data){return [
renderSection('Requirement Summary',`<p>${escapeHtml(data.requirement_summary)}</p>`,'summary-section'),
renderSection('Functional Scenarios',renderList(data.functional_scenarios),'scenarios-section'),
renderSection('Negative Scenarios',renderList(data.negative_scenarios),'scenarios-section'),
renderSection('Test Cases',renderTestCases(data.test_cases),'test-section'),
renderSection('API Coverage',renderApiCoverage(data.api_coverage),'api-section'),
renderSection('Assumptions',renderList((data.assumptions||[]).length?data.assumptions:['None identified'])),
renderSection('Open Questions',renderList((data.open_questions||[]).length?data.open_questions:['None identified'])),
renderSection('Acceptance Criteria Mapping',(data.acceptance_criteria_mapping||[]).length?renderAcceptanceMapping(data.acceptance_criteria_mapping):'<p>No acceptance criteria mapping available.</p>','mapping-section'),
renderSection('Requirement Gaps',renderList(data.requirement_gaps)),
renderSection('Automation Recommendation',`<p>${escapeHtml(data.automation_recommendation)}</p>`),
renderSection('Risk Assessment',`<div class="risk-strip"><span class="risk-score">${escapeHtml(data.risk_score)}</span><p>${escapeHtml(data.risk_reason)}</p></div>`,'risk-section'),
renderSection('Business Impact',`<p>${escapeHtml(data.business_impact)}</p>`),
renderSection('Playwright Skeleton',`<pre class="code-block"><code>${escapeHtml(data.playwright_skeleton)}</code></pre>`,'code-section')
].join('')}
async function generatePackage(){const payload={title:document.getElementById('title').value,domain:document.getElementById('domain').value,story:document.getElementById('story').value,acceptance_criteria:document.getElementById('criteria').value};await loadRuntimeConfig();const loadingMessage=runtimeConfig.use_ai?`Fetching analysis from ${formatProviderName(runtimeConfig.provider)}`:'Generating QA package locally';startLoadingStatus(loadingMessage);document.getElementById('generateBtn').disabled=true;try{const response=await fetch(API_URL,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});if(!response.ok)throw new Error(`API error: ${response.status}`);const data=await response.json();const output=document.getElementById('output');output.classList.remove('output-empty');output.innerHTML=formatPackage(data);stopLoadingStatus();setStatus(runtimeConfig.use_ai?`Generated successfully using ${formatProviderName(runtimeConfig.provider)}`:'Generated successfully using local engine')}catch(error){const output=document.getElementById('output');output.classList.add('output-empty');stopLoadingStatus();setStatus('Backend not reachable. Start FastAPI server and try again.',true);output.textContent=`Error: ${error.message}\n\nRun backend:\ncd backend\npip install -r requirements.txt\nuvicorn app.main:app --reload`}finally{document.getElementById('generateBtn').disabled=false}}
function copyOutput(){navigator.clipboard.writeText(document.getElementById('output').innerText);setStatus('Output copied to clipboard')}
loadRuntimeConfig();
