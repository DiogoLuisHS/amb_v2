# 🚀 US-Test: Nova Interface Web para AMB GUI (Design-to-Deploy)

## 🎨 Especificação Visual (Stitch)
Crie uma interface web moderna, profissional e de alta fidelidade para o **AMB GUI (Web Console)**.
O design deve seguir estética dark-mode premium (fundo escuro profundo slate-950, acentos em ciano neon, violeta e verde esmeralda, efeitos de glassmorphism sutis e tipografia moderna).

### Componentes e Layout da Tela:
1. **Header Superior (Navbar)**:
   - Logo / Título: "AMB_V2 Web Console" com badge de status do projeto ("DiogoLuisHS/amb_v2 - Online").
   - Indicadores de status de APIs: Google Jules (verde), Google Stitch (verde), Gemini IA (verde).
   - Botão de alternância rápida de tema e botão "Documentação".

2. **Visão Geral / Cards de Métricas (Dashboard KPIs)**:
   - 4 cards principais em grid:
     - "Sessões Jules Ativas": contador com indicador de progresso.
     - "Saúde do Projeto (QA)": 100% testes aprovados.
     - "Branch Git Ativa": main (status: sincronizada).
     - "Status do Loop Autônomo": Idle / Running.

3. **Painel de Ações Rápidas (Command Hub)**:
   - Botões interativos com ícones para os principais comandos:
     - "Executar Diagnóstico (amb check)"
     - "Sintetizar Prompt com IA (amb prompt)"
     - "Iniciar Pipeline Design-to-Deploy (amb pipeline)"
     - "Sentinela em Tempo Real (amb monitor)"
     - "Auditar e Limpar Sessões (amb jules clean)"

4. **Terminal / Console de Logs ao Vivo**:
   - Painel escuro com visual de terminal (fonte mono, destaque de sintaxe em cores ANSI) simulando a saída de execução de comandos da CLI.

5. **Lista de Sessões Recentes**:
   - Tabela elegante com listagem das sessões do Jules, status com badges coloridos (COMPLETED, IN_PROGRESS, FAILED), branch associada e botão de ação rápida "Ver Logs".

---

## ⚡ Especificação de Engenharia (Jules)
Implemente a base da nova interface web do **AMB GUI** (`amb_cli/gui/web/`) substituindo ou complementando a interface legada Tkinter por um servidor web leve e moderno (usando `http.server` nativo do Python ou micro-serviço web com HTML5/CSS3/Vanilla JS sem dependências externas pesadas).

### Requisitos Técnicos:
1. **Estrutura de Arquivos**:
   - Crie a pasta `amb_cli/gui/web/` contendo:
     - `index.html`: Layout semântico baseado no design gerado pelo Stitch.
     - `styles.css`: Estilização dark-mode com variáveis CSS, responsivo e com componentes de glassmorphism.
     - `app.js`: Script frontend interativo para renderização de status, cards e simulação de terminal.
     - `server.py`: Servidor HTTP leve em Python que serve a interface estática na porta local (ex: 8080) e abre automaticamente no navegador padrão com fallback para headless.
2. **Integração com a CLI**:
   - Atualize `amb_cli/gui/wizard_app.py` ou crie função `start_web_gui()` para lançar o servidor local e abrir no navegador quando o usuário executar `amb gui --web` ou por padrão.
3. **Qualidade e Testes**:
   - Crie testes unitários em `tests/test_web_gui.py` garantindo que o servidor inicializa corretamente e os arquivos estáticos existem e são válidos.
   - Garanta que todos os testes passem com 100% de cobertura e sem regressões na suíte existente (`pytest -q`).
   - Mantenha conformidade estrita com as regras do repositório (Regra 02: arquivos < 300 linhas, Regra 04: tipagem).
