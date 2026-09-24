---
name: amb-stitch-specialist
description: >-
  Generate UI mockups, extract screen assets, and manage design systems using the Stitch integration for any consumer project. Use when calling Stitch tools, generating screens from text, exporting HTML/DOM layouts, or syncing design tokens with design.md.
---

# 🎨 AMB Stitch Specialist

Guia para gerar **telas visuais, protótipos de interface e design systems** para o seu projeto consumidor utilizando a integração oficial com o **Google Stitch SDK** via `amb stitch`.

---

## 📌 1. Como o Stitch se Conecta ao seu Projeto

O Google Stitch gera telas interativas com código HTML, CSS puro, screenshots e estruturas de DOM a partir de instruções em linguagem natural:
- As telas geradas podem ser exportadas para a pasta pública do seu projeto (ex: `public/screens/` ou `dist/stitch_assets/`).
- O Design System do projeto pode ser sincronizado a partir de um arquivo local `design.md`.
- Funciona em conjunto com o `amb pipeline` para transformar os protótipos em componentes nativos de produção (React, Vue, Tailwind, etc.).

*Requisito:* `STITCH_API_KEY` (e opcionalmente `STITCH_PROJECT_ID`) configurada no `.env` do seu projeto.

---

## 🚀 2. Comandos Operacionais da CLI (`amb stitch`)

### 1. Gerar uma Nova Tela a Partir de Texto (`generate`)
Cria uma tela interativa baseada no seu prompt:
```bash
# Gerar tela com viewport Mobile e salvar o HTML localmente no projeto:
amb stitch generate -p "Dashboard SaaS com cards de métricas financeiras e gráfico de barras" -d MOBILE -o public/dashboard.html

# Gerar tela com viewport Desktop:
amb stitch generate -p "Tabela de gestão de usuários com paginação e busca" -d DESKTOP -o public/usuarios.html

# Gerar tela sem amarra a dispositivo fixo (Design Agnóstico/Responsivo):
amb stitch generate -p "Página de checkout limpa com cartão de crédito e pix" -d AGNOSTIC
```

### 2. Dispositivos e Viewports Suportados (`-d / --device`)
O Stitch aceita:
- `MOBILE`: Viewport vertical para smartphones.
- `DESKTOP`: Viewport horizontal para telas grandes.
- `TABLET`: Viewport intermediária para tablets.
- `AGNOSTIC`: Layout fluido e flexível sem amarra a tamanho de janela.

> **Zero Hardcoded:** Se você não passar `--device`, o AMB busca a preferência em `STITCH_DEVICE_TYPE` no `.env` ou `stitch.device` no `amb_project.json`. Se nenhum estiver definido, omite o parâmetro para o Stitch decidir.

### 3. Refinar uma Tela Existente (`refine`)
Ajusta cores, componentes ou layouts em uma tela já gerada:
```bash
amb stitch refine -s <SCREEN_ID> -p "Mudar a cor primária para azul royal e arredondar os botões para border-radius de 12px"
```

### 4. Gerar Variantes Visuais Exploratórias (`variants`)
Cria de 1 a 5 variações visuais da tela para comparação estética:
```bash
amb stitch variants -s <SCREEN_ID> --count 3
```

### 5. Inspecionar e Exportar Código da Tela (`get`)
Obtém o código HTML completo, classes CSS, dimensões e metadados:
```bash
amb stitch get -s <SCREEN_ID> -o public/telas/minha_tela.html
```

### 6. Baixar Telas e Assets do Projeto para Disco (`download`)
Baixa todas as telas e assets do projeto Stitch ativo diretamente para o diretório local do projeto:
```bash
amb stitch download -o ./public/stitch_assets
```
*O comando reescreve links de imagens e CSS para torná-los 100% autônomos e utilizáveis offline.*

### 7. Sincronizar Design Tokens (`sync`)
Sincroniza as especificações do arquivo `design.md` local com o Design System oficial do Stitch:
```bash
amb stitch sync -f design.md
```

### 8. Invocar Qualquer Ferramenta Oficial via JSON-RPC (`call`)
Permite invocar diretamente qualquer um dos 12 tools oficiais do `@google/stitch-sdk`:
```bash
amb stitch call list_screens '{"projectId": "17421675534889463957"}'
```

---

## 💡 3. O Fluxo de Prototipagem Rápida no Projeto

1. **Gere a Tela Inicial:**
   ```bash
   amb stitch generate -p "Kanban board com colunas To Do, In Progress e Done" -d DESKTOP -o public/kanban.html
   ```
2. **Abra o HTML no Navegador:**
   Abra `public/kanban.html` para validar visualmente o layout gerado.
3. **Refine se Necessário:**
   ```bash
   amb stitch refine -s <SCREEN_ID> -p "Adicionar modal de criação de card ao clicar no botão + Adicionar"
   ```
4. **Leve para Produção:**
   Use o comando `amb pipeline` para instruir o Jules a converter o HTML/CSS gerado nos componentes reais da stack do seu projeto!
