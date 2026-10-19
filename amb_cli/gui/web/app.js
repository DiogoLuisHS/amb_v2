document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('sessions-tbody');
    const terminalOutput = document.getElementById('terminal-output');

    function stripAnsi(text) {
        return String(text).replace(/\x1B\[[0-?]*[ -/]*[@-~]/g, '').replace(/\[\d+m/g, '');
    }

    function addLog(message, type = 'info') {
        const time = new Date().toLocaleTimeString('pt-BR', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const div = document.createElement('div');
        div.className = 'log-line';

        let colorClass = 'log-info';
        if (type === 'success') colorClass = 'log-success';
        if (type === 'error') colorClass = 'log-error';
        if (type === 'warning') colorClass = 'log-warning';

        const cleanMsg = stripAnsi(message);
        div.innerHTML = `<span class="log-time">[${time}]</span> <span class="${colorClass}">${cleanMsg}</span>`;
        terminalOutput.appendChild(div);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    function updateApiDot(elementId, isConfigured, apiName) {
        const el = document.getElementById(elementId);
        if (!el) return;
        el.className = 'dot ' + (isConfigured ? 'green' : 'red');
        el.title = `${apiName}: ${isConfigured ? 'Configurada (.env)' : 'Não configurada (.env)'}`;
    }

    let previousState = null;

    function renderStatus(data, isInitial = false) {
        // 1. Atualizar Header
        const badge = document.getElementById('repo-badge');
        if (badge && data.project) {
            badge.textContent = `${data.project.name} (${data.project.branch})`;
        }

        // 2. Indicadores de APIs
        if (data.apis) {
            updateApiDot('dot-jules', data.apis.jules, 'Google Jules API');
            updateApiDot('dot-stitch', data.apis.stitch, 'Google Stitch API');
            updateApiDot('dot-gemini', data.apis.gemini, 'Gemini IA API');
            updateApiDot('dot-github', data.apis.github, 'GitHub Token');
        }

        // 3. Atualizar KPIs
        if (data.model) {
            const modelEl = document.getElementById('kpi-gemini-model');
            const modelSub = document.getElementById('kpi-gemini-subtext');
            if (modelEl) modelEl.textContent = data.model.name;
            if (modelSub) modelSub.textContent = `Origem: ${data.model.source}`;
        }

        if (data.project) {
            const branchEl = document.getElementById('kpi-git-branch');
            const branchSub = document.getElementById('kpi-git-subtext');
            if (branchEl) branchEl.textContent = data.project.branch;
            if (branchSub) {
                branchSub.textContent = data.project.git_clean ? 'Working tree limpo' : 'Modificações não commitadas';
            }
        }

        if (data.loop_state) {
            const loopEl = document.getElementById('kpi-loop-state');
            const loopSub = document.getElementById('kpi-loop-subtext');
            if (loopEl) {
                loopEl.textContent = data.loop_state.state;
                loopEl.className = 'kpi-value ' + (data.loop_state.state === 'IDLE' ? 'text-cyan' : 'text-green');
            }
            if (loopSub) {
                if (data.loop_state.state !== 'IDLE') {
                    loopSub.textContent = `Ciclo ${data.loop_state.current_cycle} de ${data.loop_state.total_cycles}`;
                } else {
                    loopSub.textContent = 'Orquestrador aguardando comandos';
                }
            }
        }

        if (data.sessions) {
            const sessCount = document.getElementById('kpi-sessions-count');
            const sessSub = document.getElementById('kpi-sessions-subtext');
            if (sessCount) sessCount.textContent = data.sessions.length;
            if (sessSub) {
                sessSub.textContent = data.sessions.length > 0 ? `${data.sessions.length} registradas em .amb/` : 'Nenhuma sessão registrada';
            }

            // 4. Renderizar Tabela de Sessões Reais
            tbody.innerHTML = '';
            if (data.sessions.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                            Nenhuma sessão recente encontrada no projeto (.amb/).
                        </td>
                    </tr>
                `;
            } else {
                data.sessions.forEach(session => {
                    const tr = document.createElement('tr');
                    let statusClass = 'status-in-progress';
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
                        <td><span class="action-link" style="cursor: default;">Registrado</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }

        // 5. Logs Reais do Sistema
        if (isInitial) {
            addLog(`[SISTEMA] Console conectado ao repositório: ${data.project.name} (branch: ${data.project.branch})`, 'info');
            addLog(`[CONFIG] Modelo Gemini ativo: ${data.model.name} (${data.model.source})`, 'info');
            const apisOk = data.apis.gemini && data.apis.jules;
            addLog(`[ENV] Status APIs: Gemini=${data.apis.gemini ? 'OK' : 'Ausente'}, Jules=${data.apis.jules ? 'OK' : 'Ausente'}, Stitch=${data.apis.stitch ? 'OK' : 'Ausente'}, GitHub=${data.apis.github ? 'OK' : 'Ausente'}`, apisOk ? 'success' : 'warning');
            addLog(`[LOOP] Estado atual da máquina: ${data.loop_state.state}`, 'info');
        } else if (previousState && previousState !== data.loop_state.state) {
            addLog(`[LOOP] Transição de estado: ${previousState} ➔ ${data.loop_state.state}`, 'warning');
        }

        previousState = data.loop_state ? data.loop_state.state : null;
    }

    function loadStatus(isInitial = false) {
        fetch('/api/status')
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                renderStatus(data, isInitial);
            })
            .catch(err => {
                if (isInitial) {
                    addLog(`[ERRO] Falha ao consultar status do projeto: ${err.message}`, 'error');
                }
            });
    }

    // Carregamento inicial de status real
    loadStatus(true);

    // Polling regular a cada 8 segundos para manter dados reais sincronizados
    setInterval(() => {
        loadStatus(false);
    }, 8000);

    // Execução de comandos reais da CLI
    const cmdButtons = document.querySelectorAll('.cmd-btn');
    cmdButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            if (!cmd) return;

            btn.disabled = true;
            btn.style.opacity = '0.5';
            addLog(`[CLI] Disparando execução: ${cmd}`, 'warning');

            fetch(`/api/exec?cmd=${encodeURIComponent(cmd)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'ok') {
                        addLog(`[CLI] Sucesso ao executar '${cmd}':`, 'success');
                    } else {
                        addLog(`[CLI] Erro ao executar '${cmd}':`, 'error');
                    }

                    if (data.output) {
                        const lines = data.output.split('\n');
                        lines.forEach(line => {
                            if (line.trim()) {
                                addLog(line, data.status === 'ok' ? 'info' : 'error');
                            }
                        });
                    }
                    loadStatus(false);
                })
                .catch(err => {
                    addLog(`[CLI] Erro de comunicação ao executar '${cmd}': ${err.message}`, 'error');
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                });
        });
    });

    // Botão de Atualização Manual
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            addLog('[UI] Atualizando dados do ambiente e Git...', 'info');
            loadStatus(false);
        });
    }

    // Toggle de tema
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
            const isDark = document.documentElement.classList.contains('dark');
            addLog(`[UI] Modo de exibição: ${isDark ? 'Escuro' : 'Claro'}`, 'info');
        });
    }

    // Botão de Documentação
    const docsBtn = document.getElementById('docs-btn');
    if (docsBtn) {
        docsBtn.addEventListener('click', () => {
            addLog('[DOCS] Diretrizes de engenharia disponíveis em AGENTS.md e README.md', 'info');
        });
    }
});
