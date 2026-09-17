# 🎯 Tarefa Jules: Auditoria e Alinhamento de `amb_cli/cli_modules/alert_notifier.py`

## 📌 Arquivo Alvo
- **Caminho:** `amb_cli/cli_modules/alert_notifier.py`
- **Estado Atual:** 60 linhas (Conforme em tamanho, necessita de auditoria de regras arquiteturais).
- **Responsabilidade Única (SRP - Regra 01):** Formatar e emitir alertas destacados no terminal com destaque de atenção visual e beeps sonoros.

---

## 📐 Regras Arquiteturais Obrigatórias (`.agents/rules/`)
1. **Regra 01 (SRP):** Manter o módulo focado exclusivamente na apresentação de notificações visuais no console.
2. **Regra 02 (Atomização para IA):** O arquivo deve permanecer abaixo de 100 linhas (limite máximo de 300 linhas).
3. **Regra 03 (DRY & Imports Canônicos):** Remover imports mortos (`import os`). Atualizar o cabeçalho para `amb_cli/cli_modules/alert_notifier.py`.
4. **Regra 04 (Tipagem Estrita):** Anotar 100% das funções com type hints completos:
   - `play_beep() -> None`
   - `notify_attention(source: str, title: str, details: str, action_command: Optional[str] = None) -> None`
   - `notify_info(message: str) -> None`
5. **Regra 05 (Documentação Concisa):** Proibido banners gigantes ASCII decorativos. Docstrings declarativas de 1 a 3 linhas.
6. **Regra 06 (Segurança Git & Testes):** Criar a suíte de testes unitários [`tests/test_alert_notifier.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/tests/test_alert_notifier.py) testando `notify_attention`, `notify_info` e `play_beep` (com mock do `winsound`). Todos os testes devem rodar com 100% de sucesso.

---

## 🛠️ Itens Específicos a Verificar / Refatorar
1. **Tipagem e Limpeza:**
   - Adicionar `from typing import Optional` e tipar estritamente todas as assinaturas.
   - Tratar `sys.platform == "win32"` de forma defensiva sem falhas em ambientes CI/CD sem áudio.
2. **Criação de Testes Unitários:**
   - Criar `tests/test_alert_notifier.py` usando `capsys` para capturar e validar a saída de `notify_attention` e `notify_info`, e mockando `play_beep`.

---

## 🧪 Validação Obrigatória
Antes de abrir o Pull Request:
```bash
python -m py_compile amb_cli/cli_modules/alert_notifier.py
python -m pytest tests/test_alert_notifier.py
python -m pytest
```
Todos os testes unitários devem passar (100% green).

---

## 🚀 Ação Final Obrigatória: Abertura do Pull Request
Ao concluir todas as alterações e validar os testes com sucesso (100% green):
1. Você DEVE submeter/abrir o Pull Request no GitHub imediatamente.
2. Não encerre a sessão apenas no estado "Ready for submission"; confirme a criação do PR diretamente no GitHub com título e descrição claros das alterações.
