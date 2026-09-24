---
name: amb-design-to-code
description: >-
  Bridge UI prototypes from Stitch to production code implementations via amb pipeline or Google Jules inside any consumer project. Use when translating visual screens, DOM structure, and design tokens into coded components and Pull Requests.
---

# 🎨➔💻 AMB Design-to-Code Pipeline

Guia para converter **protótipos visuais do Google Stitch** em **código de produção** (React, Tailwind, Vue, CSS Modules, etc.) e Pull Requests no seu repositório consumidor através do comando `amb pipeline`.

---

## 📌 1. Como Funciona a Ponte Design-to-Code

O pipeline *Design-to-Code* elimina o retrabalho manual de recortar telas e reescrever CSS do zero:
1. **Design Generativo (Stitch):** Gera a tela visual com HTML semântico, CSS, screenshots e tokens visuais.
2. **Orquestrador AMB (`amb pipeline`):** Extrai o código da tela, DOM e tokens, e sintetiza um prompt de engenharia contextualizado com a stack do seu projeto.
3. **Engenharia de Software (Jules):** O Google Jules recebe o prompt na nuvem e implementa os componentes reais, respeitando a estrutura de pastas do seu projeto consumidor.
4. **Gatekeeper de QA:** Executa os testes do seu projeto (`amb_project.json`) e valida se a tela compila e passa nas checagens estáticas.

---

## 🚀 2. Operação do `amb pipeline` com Prompts Separados (SRP)

O `amb pipeline` adota o princípio da responsabilidade única: aceita um arquivo dedicado para as instruções visuais do Stitch (`-s`) e outro para as instruções de engenharia do Jules (`-j`).

### 1. Preparar os Arquivos de Especificação

**Arquivo de Design (`specs/drawer_ui.md`):**
```markdown
# Visual Drawer Spec
- Painel lateral que desliza da direita para a esquerda ao clicar no botão de filtros.
- Fundo com glassmorphism leve (backdrop-blur-md) e bordas suaves.
- Tipografia limpa com hierarquia clara entre títulos de seção e opções.
```

**Arquivo de Engenharia (`specs/drawer_eng.md`):**
```markdown
# Engineering Spec
- Componente: `apps/web/src/components/FilterDrawer.tsx`
- Framework: React 19 + Tailwind CSS + Lucide Icons
- Integrar com o estado global da URL usando os searchParams do React Router.
- Adicionar suporte a navegação por teclado (ESC para fechar) e foco acessível.
- Garantir aprovação em `npm run typecheck --prefix apps/web`.
```

### 2. Executar o Pipeline Completo
```bash
# Execução padrão (Gatekeeper 1 pausa para validação visual da tela):
amb pipeline -s specs/drawer_ui.md -j specs/drawer_eng.md --branch feature/filter-drawer

# Modo 100% autônomo (aprova a tela automaticamente sem pausar):
amb pipeline -s specs/drawer_ui.md -j specs/drawer_eng.md -y
```

### 3. Execução para Tarefas de Engenharia Pura (Sem Tela Stitch)
Quando a tarefa for estritamente de backend, refatoração ou API:
```bash
amb pipeline -j specs/fix_auth_tokens.md --skip-stitch --branch fix/auth-bug
```

### 4. Retomar uma Sessão Existente (`--resume-session`)
Se uma sessão do Jules já foi criada e você deseja apenas reconectar o monitoramento e a validação de QA:
```bash
amb pipeline --resume-session <SESSION_ID>
```

---

## 🛠️ 3. Boas Práticas na Tradução de Estilos para o Projeto Consumidor

Quando o Jules implementar o código a partir da tela do Stitch, oriente no prompt de engenharia:
1. **Mapeamento para Tailwind:**
   - Instrua o agente a converter hexadecimais soltos (`#1E40AF`) para as classes utilitárias do Tailwind configuradas no seu `tailwind.config.js` (ex: `bg-blue-800`).
2. **Tokens de Design System (`design.md`):**
   - Se o seu projeto tiver variáveis CSS globais (ex: `var(--color-primary)`), instrua o agente a usá-las diretamente.
3. **Acessibilidade Obrigatória:**
   - Exija `aria-modal="true"`, `role="dialog"` e labels acessíveis para botões de fechar e inputs.
4. **Validação Local:**
   - O pipeline executa `npm run typecheck` e `npm test` antes de considerar a tarefa entregue.
