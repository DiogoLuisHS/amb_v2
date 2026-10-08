# US-18: Síntese Automática de Título Amigável para Sessões do Jules

## 📌 Contexto e Objetivo
Ao criar uma sessão no Google Jules Cloud VM via API REST (`POST /v1alpha/sessions`), o campo `title` é opcional. Quando omitido, a interface web do Jules (`https://jules.google.com`) exibe a sessão sem título ou com marcadores padrão, dificultando a identificação rápida e o rastreamento no painel de sessões.

No AMB_V2, os desenvolvedores frequentemente disparam comandos como:
`amb jules create -p "Implementar testes unitários para o módulo X"` ou passam um arquivo de prompt markdown sem especificar a flag `--title`.

Esta US implementa a síntese automática e inteligente de títulos concisos para sessões quando `--title` não for explicitamente fornecido.

---

## 📐 Requisitos Técnicos

### 1. Função Atômica de Síntese de Título
- **Módulo Atômico (`amb_cli/integrations/jules/jules_core/title_synthesizer.py`):**
  - Criar função pura `synthesize_session_title(prompt_or_path: str, max_chars: int = 60) -> str`:
    - Se for caminho de arquivo markdown existente:
      - Ler as primeiras linhas procurando o primeiro título `# Título` ou primeira linha com texto.
      - Se falhar na leitura, usar o nome base do arquivo sem extensão (ex: `16_us16_jules_create_approval` -> `US-16 Jules Create Approval`).
    - Se for texto direto:
      - Pegar a primeira linha não vazia.
      - Remover marcações markdown iniciais (`#`, `*`, `>`, `-`).
      - Remover espaços extras.
      - Truncar em `max_chars` caracteres, adicionando `...` se truncado.
    - Se o prompt resultar vazio, retornar fallback padrão `"Sessão AMB_V2"`.

### 2. Integração no Fluxo de Criação
- **Arquivo (`amb_cli/integrations/jules/tools/create_session.py`):**
  - Se `title` for nulo ou vazio, invocar `synthesize_session_title(prompt)` antes de enviar o payload à API.
  - Exibir o título sintetizado na saída de confirmação no terminal:
    `  • Título: <title_sintetizado>`

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_auto_title_synthesis.py` cobrindo:
     - Síntese a partir de string direta curta e longa (truncamento em 60 chars).
     - Síntese com limpeza de caracteres markdown (`# Minha Tarefa`).
     - Síntese a partir de arquivo markdown contendo cabeçalho `#`.
     - Integração com `create_session` quando `title=None`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
