# 📚 Catálogo de Prompts Atômicos: Expansão do Ecossistema Google AI

Este diretório contém os prompts sequenciais atômicos para orientar o **Google Jules** na implementação em lote via `amb agent -p .amb/prompts/`.

Cada arquivo `.md` representa **estritamente 1 User Story (US) Atômica = 1 Sessão de VM no Jules = 1 Pull Request Incremental**, garantindo:
- **Economia extrema de tokens e contexto limpo.**
- **Conformidade arquitetural estrita (SRP, atomização <= 300 linhas, tipagem estrita).**
- **Testes unitários dedicados sem inflar arquivos existentes.**
- **Ciclo contínuo de Auto-Merge seguro via QA local.**

---

## 📑 Matriz Sequencial de Prompts Atômicos (22 USs)

### 🔹 Feature 1: Modernização com Google Gen AI SDK (`google-genai`)
| # | Arquivo Prompt | Módulo Alvo | User Story / Responsabilidade |
|---|---|---|---|
| **01** | [`01_us01_setup_dep_google_genai.md`](./01_us01_setup_dep_google_genai.md) | `pyproject.toml`, `gemini_backend.py` | US-01: Adicionar dependência `google-genai>=1.0.0` e importação defensiva com `HAS_GENAI_SDK`. |
| **02** | [`02_us02_gemini_backend_sdk_generation.md`](./02_us02_gemini_backend_sdk_generation.md) | `gemini_backend.py` | US-02: Implementar método `_generate_via_sdk` usando `genai.Client` e `GenerateContentConfig`. |
| **03** | [`03_us03_gemini_backend_fallback_and_quota.md`](./03_us03_gemini_backend_fallback_and_quota.md) | `gemini_backend.py` | US-03: Integrar fallback transparente para REST e failover de rotação de modelos em caso de erro 429. |
| **04** | [`04_us04_gemini_backend_tests.md`](./04_us04_gemini_backend_tests.md) | `tests/test_gemini_backend.py` | US-04: Suíte de testes unitários isolada para `GeminiBackend` com mocks de SDK e fallbacks. |

### 🔹 Feature 2: Grounding Semântico com Google Developer Knowledge MCP
| # | Arquivo Prompt | Módulo Alvo | User Story / Responsabilidade |
|---|---|---|---|
| **05** | [`05_us05_developer_knowledge_grounding_module.md`](./05_us05_developer_knowledge_grounding_module.md) | `context_core/knowledge_grounding.py` | US-05: Criar módulo `DeveloperKnowledgeGrounder` com catálogo canônico e resiliência offline. |
| **06** | [`06_us06_ai_context_builder_grounding_integration.md`](./06_us06_ai_context_builder_grounding_integration.md) | `architecture/ai_context_builder.py` | US-06: Integrar grounding no `ai_context_builder.py` mantendo o arquivo abaixo de 290 linhas. |
| **07** | [`07_us07_context_cli_grounding_flag.md`](./07_us07_context_cli_grounding_flag.md) | `cli_parsers.py`, `context_handler.py` | US-07: Expor a flag `--grounding` no comando `amb context`. |
| **08** | [`08_us08_knowledge_grounding_tests.md`](./08_us08_knowledge_grounding_tests.md) | `tests/test_knowledge_grounding.py` | US-08: Suíte de testes unitários dedicada para o módulo de grounding de diretrizes oficiais. |

### 🔹 Feature 3: Guardrail de Segurança com Vertex AI Model Armor
| # | Arquivo Prompt | Módulo Alvo | User Story / Responsabilidade |
|---|---|---|---|
| **09** | [`09_us09_model_armor_core_and_patterns.md`](./09_us09_model_armor_core_and_patterns.md) | `core/security/model_armor.py` | US-09: Criar pacote `core/security` com padrões regex para tokens GitHub, Google keys, JWTs e DB URLs. |
| **10** | [`10_us10_model_armor_prompt_injection_guard.md`](./10_us10_model_armor_prompt_injection_guard.md) | `core/security/model_armor.py` | US-10: Adicionar heurística de detecção e neutralização de prompt injection em logs e mensagens. |
| **11** | [`11_us11_model_armor_layer_integration.md`](./11_us11_model_armor_layer_integration.md) | `base_google_client.py`, `cognitive_advisor.py` | US-11: Integrar o guardrail na fundação HTTP e no advisor cognitivo sem inversão de camadas. |
| **12** | [`12_us12_model_armor_tests.md`](./12_us12_model_armor_tests.md) | `tests/test_model_armor.py` | US-12: Suíte de testes unitários dedicada para `ModelArmorGuardrail`. |

### 🔹 Feature 4: Servidor MCP Nativo do Google Stitch (`amb stitch mcp`)
| # | Arquivo Prompt | Módulo Alvo | User Story / Responsabilidade |
|---|---|---|---|
| **13** | [`13_us13_stitch_mcp_server_protocol_core.md`](./13_us13_stitch_mcp_server_protocol_core.md) | `stitch_core/mcp_server.py` | US-13: Loop stdio JSON-RPC 2.0, handshake `initialize` e redirecionamento de logs para `sys.stderr`. |
| **14** | [`14_us14_stitch_mcp_tools_list_manifest.md`](./14_us14_stitch_mcp_tools_list_manifest.md) | `stitch_core/mcp_server.py` | US-14: Manifesto de ferramentas em `tools/list` com JSON Schemas estritos para as tools do Stitch. |
| **15** | [`15_us15_stitch_mcp_tools_call_dispatch.md`](./15_us15_stitch_mcp_tools_call_dispatch.md) | `stitch_core/mcp_server.py` | US-15: Despacho de ferramentas em `tools/call` com captura estruturada de erro (`isError: true`). |
| **16** | [`16_us16_stitch_mcp_cli_and_handler.md`](./16_us16_stitch_mcp_cli_and_handler.md) | `cli_parsers.py`, `stitch_handler.py` | US-16: Registrar subcomando `amb stitch mcp` e rotear execução no handler. |
| **17** | [`17_us17_stitch_mcp_tests.md`](./17_us17_stitch_mcp_tests.md) | `tests/test_stitch_mcp.py` | US-17: Suíte de testes unitários isolada para `StitchMCPServer` (mantendo `test_stitch_integration.py` intocado). |

### 🔹 Feature 5: Introspecção Dinâmica de Banco com MCP Toolbox (`amb schema --live`)
| # | Arquivo Prompt | Módulo Alvo | User Story / Responsabilidade |
|---|---|---|---|
| **18** | [`18_us18_live_db_inspector_sqlite_core.md`](./18_us18_live_db_inspector_sqlite_core.md) | `context_core/live_db_inspector.py` | US-18: Introspecção de SQLite local em tempo de execução via biblioteca nativa `sqlite3`. |
| **19** | [`19_us19_live_db_inspector_readonly_safety.md`](./19_us19_live_db_inspector_readonly_safety.md) | `context_core/live_db_inspector.py` | US-19: Invariante de segurança incondicional Read-Only bloqueando palavras-chave DML/DDL com `AmbError`. |
| **20** | [`20_us20_db_schema_reader_live_integration.md`](./20_us20_db_schema_reader_live_integration.md) | `architecture/db_schema_reader.py` | US-20: Método `inspect_live` em `DbSchemaReader` com autodescoberta de arquivos SQLite. |
| **21** | [`21_us21_schema_cli_live_flags.md`](./21_us21_schema_cli_live_flags.md) | `cli_parsers.py`, `schema_handler.py` | US-21: Flags `--live` (`-l`) e `--uri` expostas no comando `amb schema`. |
| **22** | [`22_us22_live_db_inspector_tests.md`](./22_us22_live_db_inspector_tests.md) | `tests/test_live_db_inspector.py` | US-22: Suíte de testes unitários dedicada para `LiveDatabaseInspector`. |

---

## 🚀 Como Executar com o AMB Agent em Lote

### 1. Execução Sequencial em Lote
Para executar todas as 22 USs em sequência na branch ativa com o Google Jules:
```bash
amb agent -p .amb/prompts/
```

### 2. Direcionar para uma Feature Branch
```bash
amb agent -p .amb/prompts/ --branch feature/google-ai-ecosystem
```

### 3. O que o AMB fará automaticamente em cada prompt (US):
1. **Cloud VM Dedicada:** Cria uma VM isolada no Google Jules exclusivamente para a US do prompt.
2. **Contexto Cirúrgico:** Injeta automaticamente o mapa de arquivos via `ai_context_builder` para a US.
3. **Auto-Advisor Gemini:** Monitora logs e comandos bash do Jules e responde dúvidas técnicas instantaneamente.
4. **Validação & Auto-Merge:** Ao abrir o PR (sempre em Draft pelo Jules), executa `gh pr ready`, roda a suíte local de testes (`pytest`), aprova e faz auto-merge no GitHub.
5. **Git Pull & Avanço:** Faz `git pull` local e passa de forma limpa para a próxima US até concluir as 22 etapas com 100% de sucesso!
