# US-30: Renderização Dinâmica de Progresso com progressUpdated no Streaming do Jules

## 📌 Contexto e Objetivo
A documentação de tipos da API REST do Google Jules (`https://jules.google/docs/api/reference/types`) define que, durante a execução de tarefas na nuvem, o agente emite atividades do tipo `progressUpdated` reportando o estágio atual do processamento:
```json
{
  "name": "sessions/12345/activities/67890",
  "originator": "agent",
  "progressUpdated": {
    "title": "Installing dependencies",
    "description": "Running npm install in the workspace root"
  }
}
```

No AMB_V2, o streaming de atividades ao vivo em `amb jules get <id> --watch` (executado por [`stream_session_activities`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/jules/jules_watcher.py)) captura mensagens de usuário, respostas do agente e planos gerados, mas descarta o evento específico `progressUpdated`, caindo em um fallback genérico de descrição muitas vezes em branco:
```python
desc = act.get("description") or act.get("type") or "Atividade"
print(f"[{ctime}] ⚙️  {desc}")
```
Como consequência, enquanto o Jules está trabalhando ativamente (`IN_PROGRESS`), o desenvolvedor no terminal visualiza longos períodos de silêncio sem saber em qual etapa o agente se encontra (ex: clonando repositório, instalando pacotes, executando a suíte de testes ou compilando o projeto).

Esta US adiciona extração e exibição dedicada para eventos `progressUpdated` no streaming e monitoramento em tempo real do Jules.

---

## 📐 Requisitos Técnicos

### 1. Função Auxiliar de Extração de Progresso
- **Arquivo (`amb_cli/integrations/jules/jules_core/session_helpers.py`):**
  - Adicionar a função:
    ```python
    def extract_progress_update(activity: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        """
        Extrai (title, description) do evento progressUpdated de uma atividade.
        Retorna None se a atividade não contiver o evento.
        """
    ```
  - Verificar se `"progressUpdated"` está presente em `activity`.
  - Se for um dicionário, extrair `title = p.get("title", "").strip()` e `description = p.get("description", "").strip()`.
  - Se `title` ou `description` existirem, retornar a tupla `(title, description)`. Caso contrário, retornar `None`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Renderização em `stream_session_activities`
- **Arquivo (`amb_cli/integrations/jules/jules_watcher.py`):**
  - No loop de processamento de atividades em `stream_session_activities`:
    - Após checar `planGenerated` e antes do fallback genérico:
      ```python
      # 3.1. Atualização Dinâmica de Progresso
      prog = extract_progress_update(act)
      if prog:
          p_title, p_desc = prog
          desc_str = f" — {p_desc}" if p_desc else ""
          print(f"{Colors.BOLD}{Colors.CYAN}[{ctime}] ⏳ {p_title}{Colors.RESET}{Colors.DIM}{desc_str}{Colors.RESET}")
          continue
      ```
  - Importar `extract_progress_update` a partir de `integrations.jules.jules_core.session_helpers`.
  - Manter o arquivo estritamente abaixo de 300 linhas (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_progress_updated_display.py` cobrindo:
     - Extração correta de `extract_progress_update` com `title` e `description`.
     - Extração quando apenas `title` ou apenas `description` estão preenchidos.
     - Retorno `None` para atividades sem `progressUpdated`.
     - Simulação de streaming capturando e formatando a linha com `[⏳ Título — Descrição]`.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
