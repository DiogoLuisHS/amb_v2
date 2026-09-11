---
name: amb-stitch-specialist
description: >-
  Generate UI mockups, extract screen assets, and manage design systems using the Stitch integration in AMB_V2. Use when calling Stitch tools, generating screens from text, or extracting UI layouts for frontend development.
---

# 🎨 AMB Stitch Specialist

Especialista na integração de UI, prototipagem e design systems através do **Stitch** no ecossistema `amb_v2`.

## 📌 Visão Geral & Arquitetura

O Stitch é a ferramenta de design generativo e prototipagem de telas. No `amb_v2`, ele opera através de um cliente Node.js que expõe ferramentas JSON-RPC:
- **Cliente Node.js:** [`integrations/stitch/stitch_client.mjs`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/integrations/stitch/stitch_client.mjs)
- **Ferramentas CLI / Facades:** [`integrations/stitch/tools/`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/integrations/stitch/tools/)
- **Variável de Ambiente:** `STITCH_API_KEY` (configurada no `.env`)

---

## 🛠️ Ferramentas Disponíveis no Stitch

| Ferramenta | Parâmetros Principais | Finalidade |
| :--- | :--- | :--- |
| `get_screen` | `name` (`projects/{pId}/screens/{sId}`) | Extrai detalhes, HTML e CSS de uma tela específica. |
| `generate_screen_from_text` | `projectId`, `prompt`, `deviceType` | Cria nova tela interativa baseada em descrição textual. |
| `list_screens` | `projectId` | Lista todas as telas existentes em um projeto. |
| `create_project` | `title` | Cria um novo workspace de design no Stitch. |
| `list_projects` | — | Lista todos os projetos disponíveis na conta. |
| `create_design_system` | `projectId`, `designTokens` | Cria tokens de cores, tipografia e espaçamentos. |
| `generate_variants` | `screenId`, `prompt` | Cria variantes visuais de uma tela existente. |

---

## 🚀 Como Invocar o Stitch via CLI ou Código

### 1. Invocação via CLI do AMB
```bash
# Executa uma tool do Stitch passando payload JSON:
amb stitch call get_screen '{"name": "projects/proj_123/screens/screen_456"}'
```

### 2. Invocação via Node.js Direto
```bash
node integrations/stitch/stitch_client.mjs get_screen '{"name": "projects/proj_123/screens/screen_456"}'
```

### 3. Invocação via Python (Subprocess)
```python
import json
import subprocess
from config import find_repo_root

def fetch_stitch_screen(screen_name: str) -> dict:
    root = find_repo_root()
    cmd = ["node", "integrations/stitch/stitch_client.mjs", "get_screen", json.dumps({"name": screen_name})]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"Stitch error: {proc.stderr}")
    return json.loads(proc.stdout)
```

---

## ⚠️ Gotchas Críticos do Stitch

1. **Parâmetro `name` em `get_screen`:**
   - A API do Stitch espera o identificador canônico no campo `name`:
     `projects/{projectId}/screens/{screenId}`.
   - O `stitch_client.mjs` possui fallback automático para compor `name` caso `projectId` e `screenId` sejam fornecidos separadamente.

2. **Extração de CSS e Tokens:**
   - Ao extrair código para implementar no projeto consumidor, priorize os tokens globais definidos no `design_system` em vez de valores de pixels *hardcoded*.
