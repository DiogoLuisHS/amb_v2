# 🧭 Personas e Diários de Engenharia (`.amb/`)

Este diretório centraliza a inteligência local, especificações de telas, as **10 Personas Autônomas de Manutenção** e seus respectivos **Diários de Aprendizado** no repositório **DiogoLuisHS/amb_v2**.

---

## 🔍 Resumo do Ambiente do Projeto

| Propriedade | Valor Detectado |
| :--- | :--- |
| 📦 **Repositório GitHub** | `DiogoLuisHS/amb_v2` |
| 🛠️ **Stack Principal** | `python` |
| ⚡ **Gerenciador de Pacotes** | `pip/poetry` |
| 🧩 **Frameworks & Libs** | `Genérico` |
| 📜 **Regras Arquiteturais** | `Nenhuma pasta de regras identificada` |
| 🚀 **Deploy em Nuvem** | `Manual / Não configurado` |

---

## 🤖 Catálogo das 10 Personas Oficiais

| Emoji | Persona | Prompt da Persona | Diário de Aprendizado | Objetivo Principal |
| :--- | :--- | :--- | :--- | :--- |
| 📐 | **Align** | [`personas/align.md`](./personas/align.md) | [`diarios/align.md`](./diarios/align.md) | Padronizar envelopes de erro, status codes HTTP semânticos e contratos de backend. |
| 🗼 | **Beacon** | [`personas/beacon.md`](./personas/beacon.md) | [`diarios/beacon.md`](./diarios/beacon.md) | Acessibilidade (a11y), navegação por teclado, `aria-labels` e contraste WCAG AAA. |
| ⚡ | **Bolt** | [`personas/bolt.md`](./personas/bolt.md) | [`diarios/bolt.md`](./diarios/bolt.md) | Performance, redução de latência, eliminação de waterfalls e paralelização assíncrona. |
| 🪓 | **Deadwood** | [`personas/deadwood.md`](./personas/deadwood.md) | [`diarios/deadwood.md`](./diarios/deadwood.md) | Remoção cirúrgica de código morto, métodos não utilizados e imports órfãos. |
| 📝 | **Doc** | [`personas/doc.md`](./personas/doc.md) | [`diarios/doc.md`](./diarios/doc.md) | Documentação técnica TSDoc/Docstrings e sanitização de anotações informais. |
| 🧭 | **Order** | [`personas/order.md`](./personas/order.md) | [`diarios/order.md`](./diarios/order.md) | Organização top-down de funções seguindo o princípio da *Step-Down Rule*. |
| 🎨 | **Pixel** | [`personas/pixel.md`](./personas/pixel.md) | [`diarios/pixel.md`](./diarios/pixel.md) | Fidelidade visual e Design System, eliminando inline styles com suporte a Light/Dark Mode. |
| 🧪 | **Pure** | [`personas/pure.md`](./personas/pure.md) | [`diarios/pure.md`](./diarios/pure.md) | Extração de funções puras determinísticas e conformidade estrita com SRP. |
| 🛰️ | **Relay** | [`personas/relay.md`](./personas/relay.md) | [`diarios/relay.md`](./diarios/relay.md) | Validador de fluxo ponta a ponta (DB -> Service -> API -> Client -> UI) e persistência. |
| 👁️ | **Sentry** | [`personas/sentry.md`](./personas/sentry.md) | [`diarios/sentry.md`](./diarios/sentry.md) | Blindagem de rotas e validação de schemas de entrada na borda da API. |

---

## 🚀 Principais Comandos da CLI `amb`

```bash
# 1. Diagnóstico e Checklist de Chaves
amb check

# 2. Ver o Prompt Mestre de Auto-Configuração de IA
amb prompt

# 3. Inspecionar Schemas do Banco de Dados (Read-Only)
amb schema [modulo]

# 4. Gerar Roteiro Ordenado de Arquivos para a IA
amb context <modulo>

# 5. Listar todas as Personas Disponíveis
amb agent --list

# 6. Executar uma Persona Localmente no Repositório
amb agent --role deadwood

# 7. Despachar uma Persona para a Nuvem do Google Jules (Cria VM + Branch + PR)
amb agent --role bolt --dispatch-jules

# 8. Despachar TODAS as Personas em Lote para a Nuvem
amb agent --all --dispatch-jules

# 9. Iniciar o Sentinela em Tempo Real (Piloto Automático)
amb monitor --auto-approve

# 10. Menu Cognitivo para Resolver Dúvidas de Agentes
amb advisor

# 11. Executar o Pipeline Design-to-Deploy de uma Tela
amb pipeline .amb/prompts/minha_tela.md
```
