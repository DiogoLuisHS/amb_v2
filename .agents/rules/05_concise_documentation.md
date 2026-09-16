# 📝 Regra 05: Simplificação e Clareza de Comentários e Docstrings

> **Escopo:** Documentação de Código, Docstrings e Comentários Inline no AMB_V2  
> **Objetivo:** Garantir comentários simples, objetivos e de alto valor, eliminando ruído visual, redundância de sintaxe e banners decorativos desnecessários.

---

## 1. Docstrings Simples e Declarativas

- **Foco no "O quê" e "Por quê":** Docstrings devem explicar concisamente a finalidade da função, seus invariantes ou particularidades, nunca parafrasear a sintaxe do código.
- **Formato Conciso (1 a 3 linhas):** Priorizar docstrings diretas de uma ou poucas linhas:
  ```python
  # ✅ CORRETO: Simples, informativo e declarativo
  def mask_sensitive_data(value: str, visible_chars: int = 4) -> str:
      """Mascara chaves e tokens sensíveis preservando apenas os caracteres dos extremos."""
      ...

  # ❌ INCORRETO: Prolixo, redundante e explicando o óbvio
  def mask_sensitive_data(value: str, visible_chars: int = 4) -> str:
      """
      Esta função pega uma string que é uma chave secreta.
      Primeiro ela pega o tamanho da string.
      Depois ela pega os primeiros 4 caracteres.
      Depois coloca três pontinhos no meio.
      Depois pega os últimos 4 caracteres.
      E retorna a string mascarada para o chamador.
      """
      ...
  ```

---

## 2. Eliminação de Ruído e Banners Decorativos

- **Proibição de Banners Gigantes em Métodos Internos:**
  - Evitar divisórias decorativas com centenas de caracteres ASCII (`# ==============================`) repetidas a cada 5 linhas dentro de blocos de código.
  - Divisórias de seção só são aceitáveis para grandes blocos estruturais de um arquivo, nunca dentro de funções ou classes individuais.
- **Proibição de Comentários Óbvios:**
  - Não comentar o que o próprio código já expressa com clareza:
  ```python
  # ❌ INCORRETO: Comentário óbvio e inútil
  total = total + 1  # incrementa o total em um
  user = get_user()  # pega o usuario

  # ✅ CORRETO: Comentário reservado para intenção ou regra de negócio
  # Jules API requer formato sessions/<id> em rotas de feedback
  target_id = f"sessions/{raw_id}" if not raw_id.startswith("sessions/") else raw_id
  ```

---

## 3. Diretrizes para Comentários Inline

- Utilize comentários inline **apenas** quando:
  1. Houver uma decisão técnica não-óbvia (ex: contorno de bug em biblioteca de terceiros, compatibilidade com Windows).
  2. Existir uma regra de negócio ou restrição externa de API que não possa ser inferida do nome das variáveis.
  3. Explicar condições de borda (edge cases) e invariantes de segurança.
- Mantenha a linguagem técnica clara e objetiva (português padrão do projeto ou termos canônicos em inglês).
