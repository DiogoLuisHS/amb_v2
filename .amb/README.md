# 🧭 AMB_V2 — Configuração e Inteligência Local (`.amb/`)

Este diretório centraliza a configuração do projeto, personas autônomas e diários de aprendizado para o repositório **DiogoLuisHS/amb_v2**.

---

## 🔍 Resumo da Stack Detectada

| Propriedade | Valor |
| :--- | :--- |
| 📦 **Repositório GitHub** | `DiogoLuisHS/amb_v2` |
| 🛠️ **Stack Principal** | `python` |
| ⚡ **Gerenciador de Pacotes** | `pip` |
| 🧩 **Frameworks & Libs** | `Pytest` |
| 📜 **Regras Arquiteturais** | `.agents/rules` |

### 🛡️ Comandos de QA Configurados:
- **Test**: `pytest`
- **Typecheck**: `python -m py_compile cli.py`

---

## 🤖 Personas Autônomas (`.amb/personas/`)

O AMB_V2 utiliza personas em formato Markdown como especialistas no código:
- **`personas/engineer.md`**: Persona genérica de referência (Engenheiro de Software Autônomo).
- **Como adicionar novas personas**: Basta criar um arquivo `.md` em `.amb/personas/` (ex: `security.md`, `refactor.md`, `qa.md`) com a instrução desejada.
- O AMB descobre dinamicamente qualquer arquivo `.md` presente nesta pasta!

---

## 🚀 Comandos Principais da CLI `amb`

```bash
# 1. Diagnóstico completo de saúde do ambiente:
amb check

# 2. Listar personas disponíveis:
amb agent --list

# 3. Executar o engenheiro autônomo localmente:
amb agent --role engineer

# 4. Despachar para a VM em nuvem do Google Jules:
amb agent --role engineer --loop

# 5. Iniciar o sentinela de vigilância contínua:
amb monitor --auto-approve
```
