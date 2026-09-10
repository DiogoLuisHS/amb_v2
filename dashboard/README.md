# 📡 Módulo de Monitoramento & Sentinela (`dashboard`)

Este módulo vigia ativamente os serviços do ecossistema (Google Jules, Google Stitch, Google Antigravity e Render Cloud), emitindo alertas imediatos e respondendo dúvidas no piloto automático.

> [!NOTE]
> Para a interface gráfica interativa e gerenciador de `.env`, utilize o assistente nativo `amb gui` (módulo [`gui/`](../gui/README.md)).

---

## 🧭 Estrutura da Pasta:

```
dashboard/
├── README.md                      # 📖 Este guia
├── unified_monitor.py             # 📡 Sentinela contínuo em tempo real (com --auto-approve e --interactive)
└── watchers/                      # 👁️ Sentinelas Isolados (SRP)
    ├── jules_watcher.py           # Monitor de sessões, atividades e feedback do Jules
    ├── render_watcher.py          # Monitor de status e falhas de deploy no Render
    └── alert_notifier.py          # Emissor de alertas visuais e sonoros
```

---

## 🚀 Como Executar via CLI (`amb`):

### 1. Rodar o Sentinela Contínuo:
```bash
amb monitor
```

### 2. Rodar o Sentinela no Piloto Automático (Auto-Reply com Gemini):
```bash
amb monitor --auto-approve
# ou com alias:
amb monitor -y
```

### 3. Checagem Rápida de 1 Rodada:
```bash
amb monitor --check-once
# ou com alias:
amb monitor -1
```

### 4. Menu Cognitivo de Resolução de Pendências:
```bash
amb advisor
# Ou:
amb monitor --interactive
```
