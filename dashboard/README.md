# 📡 Módulo de Monitoramento & Sentinela em Tempo Real (`06_monitoramento`)

Este módulo vigia ativamente todos os 4 serviços (Google Jules, Google Stitch, Google Antigravity e Render Cloud), emitindo alertas imediatos ou respondendo dúvidas no piloto automático:

---

## 🧭 Estrutura da Pasta:

```
06_monitoramento/
├── README.md                      # 📖 Este guia
│
├── unified_monitor.py             # 📡 Sentinela contínuo em tempo real (com --auto-approve)
├── auto_advisor.py                # 🤖 Menu cognitivo para resolver pendências com Antigravity
│
└── watchers/                      # 👁️ Sentinelas Isolados (SRP)
    ├── jules_watcher.py           # Monitor de sessões, atividades e feedback do Jules
    ├── render_watcher.py          # Monitor de status e falhas de deploy no Render
    └── alert_notifier.py          # Emissor de alertas visuais e sonoros (beep ANSI)
```

---

## 🚀 Como Executar:

### 1. Rodar o Sentinela Contínuo:
```bash
python amb_v2/dashboard/unified_monitor.py
```

### 2. Rodar o Sentinela no Piloto Automático (Auto-Reply com IA):
```bash
python amb_v2/dashboard/unified_monitor.py --auto-approve
```

### 3. Abrir o Menu Central de Resolução de Pendências:
```bash
python amb_v2/dashboard/auto_advisor.py
```
*(Ou em lote: `python amb_v2/dashboard/auto_advisor.py --auto-approve`)*
