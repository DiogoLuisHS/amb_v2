# ⚙️ Módulo de Configuração & Setup Inteligente (`00_setup_config`)

Este módulo isola o carregamento de variáveis de ambiente, a validação estrita de dependências (Fail-Fast) e o assistente cognitivo de configuração inicial de projetos.

---

## 🛠️ Arquivos e Scripts:

| Arquivo | Responsabilidade Única |
| :--- | :--- |
| `config.py` | Gerenciador central de `.env`, validações estritas (`require_env`), logging e caminhos do repositório. |
| `setup_project.py` | Assistente inteligente que analisa git, stack técnica e regras com o Antigravity SDK. |
| `amb_project.json` | Arquivo gerado com a especificação e metadados detectados do projeto. |
| `.env.example` | Modelo limpo de variáveis de ambiente necessárias. |

---

## 🚀 Como Executar:

```bash
# Validar ambiente e chaves
python amb_v2/config/config.py

# Rodar assistente de auto-setup do projeto
python amb_v2/config/setup_project.py
```
