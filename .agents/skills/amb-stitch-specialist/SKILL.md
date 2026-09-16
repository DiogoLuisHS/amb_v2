---
name: amb-stitch-specialist
description: >-
  Generate UI mockups, extract screen assets, and manage design systems using the Stitch integration in AMB_V2. Use when calling Stitch tools, generating screens from text, or extracting UI layouts for frontend development.
---

# 🎨 AMB Stitch Specialist

Especialista na integração de UI, prototipagem e design systems através do **Google Stitch SDK oficial** (`@google/stitch-sdk`) no ecossistema `amb_v2`.

## 📌 Visão Geral & Arquitetura

O Stitch é a ferramenta de design generativo e prototipagem de telas do Google. No `amb_v2`, a integração opera em duas camadas totalmente alinhadas com a especificação oficial:
- **Camada Node.js (Runner Oficial):** [`integrations/stitch/stitch_client.mjs`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/integrations/stitch/stitch_client.mjs) consumindo `@google/stitch-sdk` (`StitchToolClient` e singleton `stitch`).
- **Camada Python (Cliente de Domínio):** [`integrations/stitch/stitch_client.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/integrations/stitch/stitch_client.py) (`StitchClient`).
- **Ferramentas CLI / Facades:** [`integrations/stitch/tools/`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/integrations/stitch/tools/)
- **Variáveis de Ambiente:** `STITCH_API_KEY` e opcionalmente `STITCH_PROJECT_ID`, `STITCH_DEVICE_TYPE` no `.env`.

---

## 🛠️ Ferramentas Oficiais do Stitch MCP Server

Todas as chamadas mapeiam diretamente para os 12 tools do `@google/stitch-sdk`:

| Ferramenta Oficial | Parâmetros Principais | Finalidade |
| :--- | :--- | :--- |
| `generate_screen_from_text` | `projectId`, `prompt`, `deviceType?`, `modelId?` | Gera nova tela interativa a partir de descrição textual. |
| `edit_screens` | `projectId`, `selectedScreenIds`, `prompt`, `deviceType?` | Refina e edita uma ou mais telas existentes. |
| `get_screen` | `name` (`projects/{pId}/screens/{sId}`) | Retorna DOM HTML, screenshots, dimensões e metadados. |
| `list_screens` | `projectId` | Lista todas as telas criadas no projeto. |
| `generate_variants` | `projectId`, `selectedScreenIds`, `prompt`, `variantOptions` | Gera variantes visuais exploratórias (1-5 variações). |
| `create_project` | `title?` | Cria um novo workspace/projeto no Stitch. |
| `get_project` | `name` (`projects/{projectId}`) | Consulta metadados, instâncias de tela e tema do projeto. |
| `list_projects` | `filter?` (ex: `view=owned`) | Lista projetos acessíveis ao usuário autenticado. |
| `create_design_system` | `projectId?`, `designSystem` | Cria tokens de cores, tipografia, roundness e `theme.designMd`. |
| `update_design_system` | `name`, `projectId`, `designSystem` | Atualiza tokens e especificações de um Design System existente. |
| `list_design_systems` | `projectId?` | Lista Design Systems associados ao projeto ou globais. |
| `apply_design_system` | `projectId`, `assetId`, `selectedScreenInstances` | Aplica o Design System às instâncias de tela selecionadas. |
| `download_assets` *(Virtual)* | `projectId`, `outputDir` | Baixa telas e assets do projeto para o disco local. |
| `upload` *(Domain)* | `filePath`, `opts?` | Faz upload de asset PNG/JPG/WEBP/HTML gerando tela canvas. |

---

## 📱 Resolução Genérica de Dispositivos (`deviceType`)

O Stitch aceita:
- `"MOBILE"`
- `"DESKTOP"`
- `"TABLET"`
- `"AGNOSTIC"` (design flexível/responsivo sem amarra a viewport fixa)

> [!IMPORTANT]
> **Zero Hardcoded:** O AMB_V2 **não** força `"DESKTOP"` como padrão. A prioridade de resolução é:
> 1. Flag explícita na linha de comando (`--device DESKTOP|MOBILE|TABLET|AGNOSTIC`).
> 2. Variável de ambiente (`STITCH_DEVICE_TYPE` ou `DEVICE_TYPE` no `.env`).
> 3. Configuração do projeto consumidor (`stitch.device` ou `device_type` em `amb_project.json`).
> 4. Se nenhum for especificado, o parâmetro é **omitido** (genérico), deixando o Stitch decidir.

---

## 🚀 Como Invocar o Stitch via CLI ou Código

### 1. Invocação via CLI do AMB
```bash
# Listar telas do projeto ativo
amb stitch list

# Gerar nova tela (mobile, desktop ou agnóstico) e salvar HTML local
amb stitch generate -p "Dashboard analítico com gráficos" -d MOBILE -o public/dashboard.html

# Obter detalhes e exportar HTML de uma tela existente
amb stitch get -s <screen_id> -o public/tela.html

# Refinar tela existente com novas instruções visuais
amb stitch refine -s <screen_id> -p "Adicionar modal de exportação CSV"

# Gerar variantes exploratórias
amb stitch variants -s <screen_id> -c 3

# Baixar todas as telas e assets para um diretório local
amb stitch download -o ./public/stitch_assets

# Sincronizar design.md local com o Design System oficial do Stitch
amb stitch sync -f design.md

# Consultar detalhes do projeto atual
amb stitch project

# Invocar ferramenta oficial arbitrária via JSON-RPC
amb stitch call list_screens '{"projectId": "123456"}'
```

### 2. Invocação via Python API (`StitchClient`)
```python
from integrations.stitch.stitch_client import StitchClient

client = StitchClient()

# Listar telas
screens = client.list_screens()

# Gerar tela com viewport genérica/configurada
screen_data = client.generate_screen(
    prompt="Página de login moderna com suporte a Google OAuth",
    output_file="specs/login.html"
)

# Refinar tela existente
refined = client.edit_screen(screen_id="123456", prompt="Mudar cor primária para azul royal")

# Baixar assets para diretório local
client.download_assets(output_dir="./dist/assets")

# Sincronizar design.md com Design System nativo
client.sync_design_system(design_md_path="design.md")
```

---

## ⚠️ Gotchas Críticos do Stitch

1. **Parâmetro `name` em `get_screen`:**
   - A API espera `projects/{projectId}/screens/{screenId}`. O `stitch_client.mjs` e `stitch_client.py` constroem essa URI canônica automaticamente se `screenId` for passado.
2. **Design Tokens e Markdown:**
   - O Stitch SDK suporta instruções em Markdown no campo `theme.designMd` do `create_design_system` e `update_design_system`. O AMB_V2 envia o conteúdo textual do `design.md` diretamente nesse canal nativo.
3. **Download de Assets:**
   - O comando `download_assets` reescreve links de imagens e CSS nos arquivos HTML baixados para torná-los 100% autônomos e utilizáveis offline.
