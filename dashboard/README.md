# 📡 Módulo de Monitoramento, Sentinela & Dashboard Web (`dashboard`)

Este módulo vigia ativamente os serviços do ecossistema (Google Jules, Google Stitch, Google Antigravity e Render Cloud), emitindo alertas imediatos, respondendo dúvidas no piloto automático e servindo o Dashboard Web em tempo real.

---

## 🧭 Estrutura da Pasta:

```
dashboard/
├── README.md                      # 📖 Este guia
├── dashboard_server.py            # 🖥️ Servidor Web SPA em tempo real (Porta 3333)
├── unified_monitor.py             # 📡 Sentinela contínuo em tempo real (com --auto-approve e --interactive)
└── watchers/                      # 👁️ Sentinelas Isolados (SRP)
    ├── jules_watcher.py           # Monitor de sessões, atividades e feedback do Jules
    ├── render_watcher.py          # Monitor de status e falhas de deploy no Render
    └── alert_notifier.py          # Emissor de alertas visuais e sonoros
```

---

## 🚀 Como Executar via CLI (`amb`):

### 1. Iniciar o Dashboard Web SPA:
```bash
amb dashboard
# Ou em porta customizada:
amb dashboard --port 8080
```

### 2. Rodar o Sentinela Contínuo:
```bash
amb monitor
```

### 3. Rodar o Sentinela no Piloto Automático (Auto-Reply com Gemini):
```bash
amb monitor --auto-approve
```

### 4. Checagem Rápida de 1 Rodada:
```bash
amb monitor --check-once
```

### 5. Menu Cognitivo de Resolução de Pendências:
```bash
amb advisor
# Ou:
amb monitor --interactive
```
