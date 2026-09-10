# ⚡ Assistente Gráfico Interativo — AMB_V2 (`gui`)

Interface gráfica nativa (desenvolvida em Python / Tkinter) criada para substituir painéis web legados, proporcionando montagem dinâmica de comandos e gestão direta de configurações do ambiente.

---

## 🧭 Características Principais

1. **Introspecção Dinâmica de Comandos**:
   - Lê a árvore oficial de comandos e opções de `cli_parsers.py` em tempo de execução.
   - Apresenta os parâmetros de cada comando com checkboxes para flags booleanas e campos de texto interativos para opções que aceitam argumentos.
   - Exibe resumo descritivo de cada comando selecionado sem poluição de códigos ANSI.

2. **Detecção Dinâmica do Projeto Ativo**:
   - Identifica automaticamente a raiz do projeto de onde o comando `amb gui` foi disparado (utilizando `find_repo_root()`).
   - Apresenta no cabeçalho o repositório (`GITHUB_REPOSITORY`), a pasta física e o arquivo `.env` correspondente.
   - Possui o botão `📁 Trocar Pasta do Projeto...` para permitir alternar entre múltiplos monorepos ou projetos sem reiniciar a aplicação.

3. **Gerenciador de Configurações (.env)**:
   - Lê e exibe todos os parâmetros configurados no arquivo `.env` do projeto ativo.
   - Assegura a visibilidade imediata de chaves centrais como `STITCH_PROJECT_ID`, `STITCH_API_KEY`, `JULES_API_KEY`, `GEMINI_API_KEY`, `GITHUB_REPOSITORY`, `RENDER_API_KEY`, `TURSO_DATABASE_URL` e `TURSO_AUTH_TOKEN`.
   - Área com barra de rolagem (Canvas Scrollável) que comporta dezenas de variáveis sem cortes visuais.
   - Permite adicionar novas chaves customizadas via `➕ Adicionar Variável`.
   - Salva diretamente no `.env` do projeto ativo preservando comentários e formatação original.

4. **Execução Direta no Contexto do Projeto**:
   - Ao clicar em **"Executar no Terminal"**, a janela monta a linha de comando completa do `amb` e a dispara diretamente com o diretório de trabalho (`cwd`) apontado para a pasta do projeto ativo.

---

## 🚀 Como Executar

No terminal, a partir de qualquer pasta de projeto:
```bash
amb gui
```

Ou através dos aliases:
```bash
amb ui
amb wizard
```
