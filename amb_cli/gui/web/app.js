// Mock Data for Terminal
const logLines = [
    '<span style="color: #94a3b8">[SYS] Kernel v6.18-arch-amb loaded. Jules daemon connected to ws://127.0.0.1:8941</span>',
    '<span><span style="color: #94a3b8">18:42:01.002</span> <span style="background: rgba(6,182,212,0.2); color: #06b6d4; padding: 0 4px; border-radius: 2px;">INFO</span> Orquestrador AMB iniciado com flag <span style="color: #06b6d4">--continuous-eval</span></span>',
    '<span><span style="color: #94a3b8">18:42:02.318</span> <span style="background: rgba(16,185,129,0.2); color: #10b981; padding: 0 4px; border-radius: 2px;">STITCH</span> Conectado ao endpoint Stitch Gateway. Hash de sincronia: <span style="color: #10b981">#b9f1a0</span></span>',
    '<span><span style="color: #94a3b8">18:42:03.144</span> <span style="background: rgba(139,92,246,0.2); color: #8b5cf6; padding: 0 4px; border-radius: 2px;">GEMINI</span> Gemini 2.5 Pro instanciado: Modelo sintetizando contexto dos arquivos</span>',
    '<span><span style="color: #94a3b8">18:42:04.550</span> <span style="background: rgba(6,182,212,0.2); color: #06b6d4; padding: 0 4px; border-radius: 2px;">JULES</span> Agente #204 alocado para <span style="color: #06b6d4">auto-fix: resolve type drift</span> na branch</span>',
    '<span><span style="color: #94a3b8">18:42:07.820</span> <span style="background: rgba(245,158,11,0.2); color: #f59e0b; padding: 0 4px; border-radius: 2px;">LOOP</span> Executando ciclo de verificação autônoma <span style="color: #f59e0b">amb check --strict</span></span>',
    '<span><span style="color: #94a3b8">18:42:08.910</span> <span style="background: rgba(16,185,129,0.2); color: #10b981; padding: 0 4px; border-radius: 2px;">SUCCESS</span> ✓ Test Suite: <span style="color: #10b981">42 passed, 0 failed.</span> QA report persistido em</span>',
    '<span><span style="color: #94a3b8">18:42:11.402</span> <span style="background: rgba(139,92,246,0.2); color: #8b5cf6; padding: 0 4px; border-radius: 2px;">GEMINI</span> Sugestão de otimização gerada: 14% de ganho de velocidade ao paralelizar</span>',
    '<span><span style="color: #94a3b8">18:42:15.118</span> <span style="background: rgba(6,182,212,0.2); color: #06b6d4; padding: 0 4px; border-radius: 2px;">INFO</span> Telemetry heartbeat enviado para Alpha-Node-01. Resposta em <span style="color: #06b6d4">18ms</span></span>',
    '<span><span style="color: #94a3b8">18:42:19.004</span> <span style="background: rgba(6,182,212,0.2); color: #06b6d4; padding: 0 4px; border-radius: 2px;">JULES</span> Sessão #204 concluída a etapa de linting estático. Ingressando no estágio<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;de commit automatizado...</span>'
];

const terminalOutput = document.getElementById('terminal-output');

function renderTerminal() {
    terminalOutput.innerHTML = '';
    logLines.forEach(line => {
        const div = document.createElement('div');
        div.innerHTML = line;
        terminalOutput.appendChild(div);
    });
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

// Mock Data for Sessions
const sessionsData = [
    { id: '#204', desc: 'Type drift auto-resolution<br><span style="color:#94a3b8; font-size: 0.75rem">Refatoração de interfaces no módulo telemetria</span>', status: 'IN_PROGRESS', branch: 'feature/jules-sync' },
    { id: '#203', desc: 'QA Regression Sentinel<br><span style="color:#94a3b8; font-size: 0.75rem">Validação contínua do endpoint /v2/agent/eval</span>', status: 'IN_PROGRESS', branch: 'main' },
    { id: '#202', desc: 'Prompt Synthesis optimization<br><span style="color:#94a3b8; font-size: 0.75rem">Geração de tokens determinísticos para Gemini</span>', status: 'COMPLETED', branch: 'feature/prompt-draft' },
    { id: '#201', desc: 'Legacy session cleanup worker<br><span style="color:#94a3b8; font-size: 0.75rem">Timeout de lock no socket IPC /tmp/jules.sock</span>', status: 'FAILED', branch: 'chore/cleaner' }
];

const sessionsBody = document.getElementById('sessions-body');

function renderSessions() {
    sessionsBody.innerHTML = '';
    sessionsData.forEach(session => {
        const tr = document.createElement('tr');

        let statusClass = '';
        if (session.status === 'IN_PROGRESS') statusClass = 'status-in_progress';
        if (session.status === 'COMPLETED') statusClass = 'status-completed';
        if (session.status === 'FAILED') statusClass = 'status-failed';

        tr.innerHTML = `
            <td style="color: var(--cyan); font-family: monospace;">${session.id}</td>
            <td>${session.desc}</td>
            <td><span class="badge-status ${statusClass}">● ${session.status}</span></td>
            <td style="font-family: monospace; font-size: 0.75rem">${session.branch}</td>
        `;
        sessionsBody.appendChild(tr);
    });
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    renderTerminal();
    renderSessions();
});
