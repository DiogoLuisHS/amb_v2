document.addEventListener('DOMContentLoaded', () => {
    // Mock Data for Sessions
    const sessions = [
        { id: '#069-9483', name: 'Refatoração de Telemetria Jules & Token Limiter', module: 'core/telemetry/pipeline.py', status: 'IN_PROGRESS', branch: 'feat/telemetry-v2', duration: '03m 42s' },
        { id: '#069-9482', name: 'Auto-Healing de Testes Unitários de Integração', module: 'tests/test_autonomous_loop.py', status: 'IN_PROGRESS', branch: 'main', duration: '01m 15s' },
        { id: '#069-9481', name: 'Sincronização de Tokens com Google Stitch Engine', module: 'stitch/connector.json', status: 'COMPLETED', branch: 'design/stitch-tokens', duration: '48s' },
        { id: '#069-9480', name: 'Geração de Meta-Prompts para Loop de Diagnóstico', module: 'prompts/gemini_meta_v2.md', status: 'COMPLETED', branch: 'main', duration: '02m 04s' },
        { id: '#069-9479', name: 'Verificação de Dependências Obsoletas (Purge)', module: 'Error: Timeout no contêiner registry NPM remoto', status: 'FAILED', branch: 'chore/deps-clean', duration: '05m 00s' }
    ];

    const tbody = document.getElementById('sessions-tbody');

    // Populate Sessions Table
    sessions.forEach(session => {
        const tr = document.createElement('tr');

        let statusClass = '';
        if (session.status === 'IN_PROGRESS') statusClass = 'status-in-progress';
        if (session.status === 'COMPLETED') statusClass = 'status-completed';
        if (session.status === 'FAILED') statusClass = 'status-failed';

        tr.innerHTML = `
            <td><span class="text-cyan">${session.id}</span></td>
            <td>
                <strong>${session.name}</strong><br>
                <span class="kpi-subtext">Módulo: ${session.module}</span>
            </td>
            <td><span class="status-badge ${statusClass}">● ${session.status}</span></td>
            <td><code>${session.branch}</code></td>
            <td>${session.duration}</td>
            <td><a href="#" class="action-link">Ver Logs ↗</a></td>
        `;
        tbody.appendChild(tr);
    });

    // Terminal Logic
    const terminalOutput = document.getElementById('terminal-output');

    function addLog(message, type = 'info') {
        const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric", second: "numeric" });
        const div = document.createElement('div');
        div.className = 'log-line';

        let colorClass = '';
        if (type === 'success') colorClass = 'log-success';
        if (type === 'error') colorClass = 'log-error';
        if (type === 'warning') colorClass = 'log-warning';
        if (type === 'info') colorClass = 'log-info';

        div.innerHTML = `<span class="log-time">[${time}]</span> <span class="${colorClass}">${message}</span>`;
        terminalOutput.appendChild(div);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    // Initial Logs
    addLog('[INFO] Inicializando dashboard AMB Console v2.4.1 (cluster: local-prod-01)', 'info');
    addLog('[STITCH] Design token bridge handshake: 24 tokens importados com sucesso', 'success');
    addLog('[GEMINI] Gemini 2.5 Pro pipeline model initialized. Temperature: 0.35 | Max tokens: 8192', 'info');

    // Simulate real-time logs
    setInterval(() => {
        const messages = [
            { msg: '[MONITOR] File watcher ativo: 120 arquivos monitorados. Nenhuma anomalia de latência detectada.', type: 'info' },
            { msg: '[HEARTBEAT] Node amb-worker-01 reporta sincronização OK (ping 15ms).', type: 'success' },
            { msg: '[LIVE] Aguardando novo comando do loop autônomo...', type: 'warning' }
        ];
        const randomMsg = messages[Math.floor(Math.random() * messages.length)];
        addLog(randomMsg.msg, randomMsg.type);
    }, 15000);

    // Command Buttons Logic
    const cmdButtons = document.querySelectorAll('.cmd-btn');
    cmdButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            addLog(`[USER] Executando comando: ${cmd}...`, 'warning');

            // Simulate command execution delay
            setTimeout(() => {
                if(Math.random() > 0.2) {
                    addLog(`[SUCCESS] Comando '${cmd}' finalizado com sucesso.`, 'success');
                } else {
                    addLog(`[ERROR] Falha ao executar '${cmd}'. Verifique os logs para mais detalhes.`, 'error');
                }
            }, 1500);
        });
    });

    // Theme Toggle (Mock)
    document.getElementById('theme-toggle').addEventListener('click', () => {
        addLog('[UI] Alternância de tema solicitada (Mock).', 'info');
    });

    document.getElementById('docs-btn').addEventListener('click', () => {
        addLog('[UI] Abrindo documentação...', 'info');
    });
});
