document.addEventListener('DOMContentLoaded', () => {
    // 1. Simulação de Terminal
    const terminalLogs = document.getElementById('terminal-logs');

    const initialLogs = [
        { time: '14:32:01.004', type: 'info', tag: '[INFO]', msg: 'AMB Runtime Core inicializado v2.4.1' },
        { time: '14:32:01.320', type: 'info', tag: '[CONFIG]', msg: 'Carregando chaves de API: Google Stitch [VÁLIDO]' },
        { time: '14:32:02.840', type: 'success', tag: '[STITCH]', msg: 'Conexão com Google Stitch estabelecida via mTLS.' },
        { time: '14:32:05.412', type: 'info', tag: '[GEMINI]', msg: 'Sessão de meta-prompt #3042 criada.' },
    ];

    function addLog(log) {
        const div = document.createElement('div');
        div.className = `log-line ${log.type}`;
        div.innerHTML = `<span class="time">[${log.time}]</span> <span class="tag">${log.tag}</span> ${log.msg}`;
        terminalLogs.appendChild(div);
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
    }

    initialLogs.forEach(addLog);

    // 2. Simulação de Sessões
    const sessionsBody = document.getElementById('sessions-table-body');
    const sessions = [
        { id: '#SES-9483', name: 'Auto-healing loop test fix', status: 'IN_PROGRESS', statusClass: 'in_progress', branch: 'feat/agent-heal', duration: '00m 12s' },
        { id: '#SES-9482', name: 'Figma token synchronizer', status: 'IN_PROGRESS', statusClass: 'in_progress', branch: 'sync/stitch-tokens', duration: '02m 45s' },
        { id: '#SES-9481', name: 'Regression Suite QA Run', status: 'COMPLETED', statusClass: 'completed', branch: 'main', duration: '06m 38s' },
        { id: '#SES-9479', name: 'Stitch Webhook Sandbox Test', status: 'FAILED', statusClass: 'failed', branch: 'fix/webhook-retry', duration: '00m 18s' }
    ];

    sessions.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span style="color: var(--accent-cyan); font-family: var(--font-mono)">${s.id}</span></td>
            <td>${s.name}</td>
            <td><span class="status-badge ${s.statusClass}">${s.status}</span></td>
            <td>${s.branch}</td>
            <td>${s.duration}</td>
            <td><button class="action-btn">Ver Logs ></button></td>
        `;
        sessionsBody.appendChild(tr);
    });

    // 3. Interatividade de Botões (Mock)
    const cmdBtns = document.querySelectorAll('.cmd-btn');
    cmdBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            const now = new Date();
            const timeStr = `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}.${now.getMilliseconds()}`;
            addLog({ time: timeStr, type: 'info', tag: '[EXEC]', msg: `Executando comando: ${cmd}` });

            // Aqui seria a integração real com o backend (fetch para /api/exec)
            fetch(`/api/exec?cmd=${encodeURIComponent(cmd)}`)
                .then(res => res.json())
                .then(data => {
                    const doneTime = new Date();
                    const doneTimeStr = `${doneTime.getHours()}:${doneTime.getMinutes()}:${doneTime.getSeconds()}.${doneTime.getMilliseconds()}`;
                    addLog({ time: doneTimeStr, type: data.status === 'ok' ? 'success' : 'error', tag: '[RESULT]', msg: data.output || 'Concluído' });
                })
                .catch(err => console.error(err));
        });
    });
});