# ⚙️ Módulo de Configuração & Setup Inteligente (`config`)

Este módulo isola o carregamento de variáveis de ambiente, a validação estrita de dependências (Fail-Fast) e o assistente cognitivo de configuração inicial de projetos.

---

## 🛠️ Arquivos e Scripts:

| Arquivo | Responsabilidade Única |
| :--- | :--- |
| `__init__.py` | Exportações de símbolos e exceções para o pacote. |
| `config.py` | Gerenciador central de `.env`, validações estritas (`require_env`), logging e detecção da raiz do repositório. |
| `setup_project.py` | Assistente inteligente que analisa git, stack técnica e regras com o Antigravity SDK. |
| `.env.example` | Modelo limpo de variáveis de ambiente necessárias. |

---

## 🚀 Como Executar via CLI (`amb`):

```bash
# Validar ambiente, chaves e checklist do projeto
amb check

# Rodar assistente de auto-setup do projeto
amb setup

# Exibir o Prompt Mestre de Auto-Configuração para IAs
amb prompt
```
