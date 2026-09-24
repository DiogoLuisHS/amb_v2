# 🎯 Task: Grounding Semântico com Google Developer Knowledge MCP

## 📌 Contexto & Responsabilidade Única (SRP)
O Google disponibiliza o **Google Developer Knowledge MCP** (`developerknowledge.googleapis.com`), expondo busca estruturada e grounding semântico sobre documentação oficial de engenharia para agentes autônomos.
No AMB, o `ai_context_builder` mapeia as camadas do projeto consumidor (DB, Services, API, UI). Integrar grounding semântico garante que além dos caminhos de arquivos, o Jules e o Antigravity recebam diretrizes canônicas e atualizadas sobre as tecnologias detectadas no projeto (evitando alucinação de APIs obsoletas).

Sua missão é criar o módulo de grounding em `amb_cli/architecture/context_core/knowledge_grounding.py` e integrá-lo de forma opcional e graciosa ao `ai_context_builder.py`.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. Novo Módulo: `amb_cli/architecture/context_core/knowledge_grounding.py`
- Crie a classe `DeveloperKnowledgeGrounder`:
  - Recebe as tecnologias detectadas no `amb_project.json` (ex: `typescript`, `react`, `drizzle`, `fastapi`).
  - Consulta o endpoint/servidor do Developer Knowledge ou utiliza cache embutido de diretrizes oficiais para gerar um bloco Markdown conciso (`## 📚 Canonical Developer Knowledge Guidelines`).
  - Suporta modo offline / fallback silencioso: se não houver rede ou credencial, omite o bloco sem quebrar o fluxo.
  - Formato conciso: máximo 20 linhas por tecnologia com links oficiais e boas práticas.
  - Teto do arquivo: <= 200 linhas.

### 2. Integrar em `amb_cli/architecture/ai_context_builder.py`
- Adicione o parâmetro opcional `include_grounding: bool = False` na função `build_ai_context(...)`.
- Quando `include_grounding=True`, invoque `DeveloperKnowledgeGrounder` e anexe a seção ao final do roteiro Markdown gerado.
- Adicione a flag `--grounding` no parser da CLI para o comando `amb context` em `amb_cli/cli_modules/cli_parsers.py`.

### 3. Testes Unitários
- `tests/test_ai_context_builder.py`:
  - Adicione testes unitários para a classe `DeveloperKnowledgeGrounder`.
  - Verifique que `build_ai_context(include_grounding=True)` inclui a seção correspondente.
  - Verifique que falhas de rede no grounder não impedem a geração do contexto arquitetural padrão (resiliência).

---

## 📋 Critérios de Aceite (DoD)
1. `amb context --grounding` inclui diretrizes oficiais no blueprint gerado.
2. Modo offline opera com fallback gracioso sem disparar exceções não tratadas.
3. Arquivos mantidos abaixo do teto de 300 linhas.
4. Suíte `pytest` 100% verde.
