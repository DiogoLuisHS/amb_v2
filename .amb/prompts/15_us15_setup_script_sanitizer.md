# US-15: Sanitização de Scripts de Setup para a VM do Jules contra Processos Bloqueantes

## 📌 Contexto e Objetivo
Conforme a documentação oficial do Google Jules (`https://jules.google/docs/errors/`), uma das causas mais frequentes de falhas e timeouts na inicialização de VMs é a presença de comandos de longa duração ou servidores contínuos no script de setup (por exemplo: `npm run dev`, `npm start`, `yarn dev`, `flask run`, `uvicorn`, `python manage.py runserver`, `nodemon`).
Esta funcionalidade introduz o módulo `SetupSanitizer`, que audita e sanitiza scripts de setup (inferidos ou configurados), removendo comandos bloqueantes e alertando o desenvolvedor para garantir que a VM do Jules inicialize com sucesso em modo non-interactive.

---

## 📐 Requisitos Técnicos

1. **Módulo Sanitizador (`amb_cli/workspace/setup/setup_sanitizer.py`):**
   - Criar a classe `SetupSanitizer`:
     - Lista canônica de comandos bloqueantes proibidos para setup:
       - `npm run dev`, `npm start`, `yarn dev`, `yarn start`, `pnpm dev`, `flask run`, `uvicorn`, `manage.py runserver`, `nodemon`, `vite`, `next dev`, `http.server`.
     - Método estático `sanitize_script(script_text: str) -> tuple[str, list[str]]`:
       - Analisa linha por linha.
       - Filtra comandos bloqueantes, mantendo os comandos válidos de instalação, compilação e teste (`npm install`, `pip install -e .`, `npm run build`, `pytest -q`).
       - Retorna `(script_sanitizado, lista_de_comandos_removidos)`.
     - Método estático `has_blocking_commands(script_text: str) -> bool`:
       - Retorna True se houver algum comando proibido.

2. **Integração no Analisador de Ambiente (`env_inspector.py` ou `ProjectAnalyzer`):**
   - Ao inferir ou inspecionar o setup para o Jules, submete o script a `SetupSanitizer.sanitize_script`.
   - Se houver comandos bloqueantes removidos, exibe alerta informativo no console (`log("ENV", f"Comando bloqueante ignorado no setup: ...", Colors.YELLOW)`).

---

## 🧪 Critérios de Aceite
1. **Suíte de Testes:** Criar `tests/test_setup_sanitizer.py` cobrindo:
   - Identificação e remoção de comandos como `npm run dev` e `flask run`.
   - Preservação integral de comandos legítimos de build e teste (`npm install`, `pip install -e .`, `pytest`).
   - Retorno correto de avisos informativos.
   - Integração com o fluxo do `env_inspector.py`.
2. **Qualidade de Código:**
   - 100% dos testes unitários passando (`pytest -q`).
   - Limite estrito de no máximo 300 linhas por arquivo (Regra 02).
   - Tipagem estrita com `typing` (Regra 04).
   - Zero dependências externas novas.
