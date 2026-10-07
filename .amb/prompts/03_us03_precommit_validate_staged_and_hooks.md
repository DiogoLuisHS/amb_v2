# 🎯 US-03: Validação Pré-Commit de Regras e Gerador de Git Hook (amb validate --staged e amb hooks install)

## 👤 User Story
> **Como** desenvolvedor do AMB_V2,  
> **Quero** poder auditar regras arquiteturais apenas nos arquivos em stage (`amb validate --staged`) e instalar um pre-commit hook automático (`amb hooks install`),  
> **Para que** violações de regras arquiteturais (arquivos >300 linhas, imports proibidos) sejam barradas antes do commit sem onerar o desenvolvedor.

---

## 📌 Critérios de Aceitação BDD

* **Cenário 1: Auditoria Cirúrgica com --staged**
  * **Dado** que há arquivos preparados no Git (`git add`);
  * **Quando** `amb validate --staged` for invocado;
  * **Então** deve identificar apenas os arquivos modificados em staged usando `git diff --name-only --cached`;
  * **E** deve auditar cada arquivo contra as regras em `.agents/rules/`;
  * **E** se houver violação, deve retornar código de saída diferente de 0 com relatório dos arquivos problemáticos.

* **Cenário 2: Execução com Stage Vazio**
  * **Dado** que nenhum arquivo foi adicionado ao stage do Git;
  * **Quando** `amb validate --staged` for executado;
  * **Então** deve exibir mensagem informando que não há arquivos no stage e retornar código 0.

* **Cenário 3: Gerador de Hook (amb hooks install)**
  * **Dado** um repositório Git com diretório `.git/`;
  * **Quando** o comando `amb hooks install` for executado;
  * **Então** deve criar ou atualizar o arquivo `.git/hooks/pre-commit` com permissão executável contendo a chamada para `amb validate --staged`;
  * **E** deve imprimir confirmação de instalação bem-sucedida.

---

## 🛠️ Arquivos Alvo & Alterações Necessárias

### 1. `amb_cli/architecture/rules_manager.py`
Adicionar método `get_staged_files() -> List[str]` utilizando subprocess com `git diff --name-only --cached` e tratando repositórios sem commits iniciais de forma segura.

### 2. `amb_cli/cli_modules/handlers_core/validate_handler.py`
Atualizar o handler para suportar a flag `--staged`, validando apenas a lista de arquivos retornada.

### 3. `amb_cli/cli_modules/handlers_core/hooks_handler.py` (Novo)
Implementar `handle_hooks_install()` criando `.git/hooks/pre-commit` com shebang `#!/bin/sh` e chamada para `python -m amb_cli.cli validate --staged`. Configurar permissão `0o755` se não estiver no Windows, ou script compatível multiplataforma.

### 4. `amb_cli/cli_modules/cli_parsers.py` e `amb_cli/cli_modules/cli_dispatch.py`
- Adicionar argumento `--staged` ao parser de `validate`.
- Adicionar comando `amb hooks` com subcomando `install`.

### 5. `tests/test_hooks_and_validate_staged.py` (Novo)
Testes cobrindo:
- Mock do git diff staged com violação de regra e com arquivos conformes.
- Criação e conteúdo do hook `.git/hooks/pre-commit`.

---

## 🔍 Comandos de Verificação Local
```bash
# Validar testes unitários dos hooks e validate --staged
pytest tests/test_hooks_and_validate_staged.py -v

# Validar suíte completa
pytest -q

# Testar comandos
python -m amb_cli.cli validate --staged
python -m amb_cli.cli hooks install
```

---

## 📋 Definition of Done (DoD)
- [ ] Flag `--staged` funcionando no comando `amb validate`.
- [ ] Subcomando `amb hooks install` gerando o hook pre-commit corretamente.
- [ ] Suíte de testes unitários dedicada em `tests/test_hooks_and_validate_staged.py` 100% passando.
- [ ] Arquivos novos e modificados com menos de 250 linhas cada.
