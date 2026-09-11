---
name: amb-render-specialist
description: >-
  Monitor cloud services, inspect deployment health, and verify post-merge builds on Render in the AMB_V2 ecosystem. Use when checking deploy statuses, troubleshooting deploy failures, or verifying service availability.
---

# 🚀 AMB Render Specialist

Especialista na integração de deploy e monitoramento de serviços em nuvem no **Render** dentro do `amb_v2`.

## 📌 Visão Geral & Arquitetura

O módulo do Render é responsável por auditar deploys automáticos disparados após merges de PRs no GitHub, garantindo que o código em produção não quebre.
- **Cliente Core:** [`integrations/render/render_client.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/integrations/render/render_client.py)
- **Sentinela / Watcher:** [`dashboard/watchers/render_watcher.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/dashboard/watchers/render_watcher.py)
- **Variável de Ambiente:** `RENDER_API_KEY` (configurada no `.env`)

---

## 🛠️ Capacidades do Módulo Render

1. **Listagem de Serviços:**
   - Lista web services, background workers e databases configurados na conta do Render.
2. **Inspeção de Deploys:**
   - Rastreia o status de cada build: `created`, `build_in_progress`, `live`, `deactivated`, `build_failed`, `canceled`.
3. **Auditoria Pós-Merge:**
   - Quando um PR é mergeado na branch principal (ex: `main` ou `develop`), o Render Watcher aguarda e valida se o novo deploy atingiu o status `live`.

---

## 🚀 Comandos & Utilização

### 1. Monitorar no Sentinela do AMB
O sentinela monitora concorrentemente o Render e o Jules:
```bash
# Iniciar monitoramento contínuo:
amb monitor

# Executar apenas uma checagem pontual:
amb monitor --check-once
```

### 2. Uso Programático em Python
```python
from render_client import RenderClient

client = RenderClient()

# Listar todos os serviços
services = client.list_services()

# Buscar o último deploy de um serviço
for svc in services:
    service_id = svc.get("service", {}).get("id")
    deploys = client.list_deploys(service_id, limit=1)
    if deploys:
        latest = deploys[0].get("deploy", {})
        print(f"Serviço {service_id}: Status = {latest.get('status')}")
```

---

## ⚠️ Regras de Confiabilidade

1. **Tratamento de Rate Limit:**
   - A API pública do Render possui limites de requisições por minuto. Polling no loop sentinela deve respeitar um intervalo mínimo de 15 segundos (`--interval 15`).
2. **Falha de Deploy Silenciosa:**
   - Se um deploy passar de `build_in_progress` para `build_failed`, o `RenderWatcher` emite um alerta crítico no terminal e pode disparar uma notificação no sistema operacional para intervenção rápida.
