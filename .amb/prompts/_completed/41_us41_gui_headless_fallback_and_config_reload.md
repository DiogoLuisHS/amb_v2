# US-41: Fallback Gracioso Headless e Sincronização de ConfigManager em amb gui

## 📌 Contexto e Objetivo
O comando `amb gui` ([`wizard_app.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/gui/wizard_app.py)) abre o Assistente Gráfico Interativo baseado em Tkinter. No entanto, dois pontos de fragilidade afetam a experiência do desenvolvedor:
1. **Quebra Hostil em Ambientes Headless:** Ao ser executado em servidores remotos, conexões SSH, containers Docker ou WSL sem servidor X11/Wayland, o comando falha abruptamente com exceção não-tratada `_tkinter.TclError: no display name and no $DISPLAY environment variable`.
2. **Desalinhamento de Cache do `ConfigManager`:** Quando o desenvolvedor edita credenciais e salva alterações no `.env` pela aba de Configurações ([`settings_tab.py`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/gui/wizard_core/settings_tab.py)), o singleton central `ConfigManager` (introduzido na US-04) não tem seu cache em memória recarregado, mantendo dados obsoletos na execução.

Esta US implementa a captura graciosa de falhas de interface gráfica orientando o uso alternativo pela CLI e aciona a sincronização imediata do `ConfigManager.reload()` pós-salvamento na GUI.

---

## 📐 Requisitos Técnicos

### 1. Tratamento e Fallback Headless em `wizard_app.py`
- **Arquivo (`amb_cli/gui/wizard_app.py`):**
  - No método `start_wizard`:
    - Envolver a instanciação de `DynamicWizard()` e o `mainloop()` em tratamento de exceção seguro:
      ```python
      try:
          app = DynamicWizard()
          app.attributes('-topmost', True)
          app.after_idle(app.attributes, '-topmost', False)
          app.mainloop()
      except (tk.TclError, Exception) as err:
          # Se o erro for relacionado à falta de display X11/Wayland ou inicialização de Tk
          from core.exceptions import AmbError
          raise AmbError(
              f"Interface gráfica indisponível no ambiente atual: {err}",
              "Execute a CLI diretamente pelo terminal:\n"
              "  • amb --help (ver todos os comandos)\n"
              "  • amb check  (diagnóstico de credenciais)\n"
              "  • amb setup  (assistente de configuração)"
          )
      ```
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

### 2. Sincronização do `ConfigManager` em `settings_tab.py`
- **Arquivo (`amb_cli/gui/wizard_core/settings_tab.py`):**
  - No método de salvamento de variáveis de ambiente:
    - Logo após persistir o arquivo `.env`:
      ```python
      try:
          from core.config_manager import ConfigManager
          ConfigManager.get_instance().reload()
      except Exception:
          pass
      ```
    - Garantir que a mensagem de status da interface informe: `"Configurações salvas e recarregadas com sucesso!"`.
  - Manter o limite rígido de 300 linhas por arquivo (Regra 02).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes Unitários:**
   - Criar `tests/test_gui_headless_fallback.py` cobrindo:
     - Disparo de `AmbError` com mensagem amigável e dica de resolução quando `DynamicWizard` lança `tk.TclError`.
     - Execução do método de salvamento em `SettingsTab` invocando `ConfigManager.get_instance().reload()`.
     - Resiliência caso `ConfigManager` não esteja instanciado.
2. **Qualidade de Código e Limites Arquiteturais:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Teto rígido de 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
