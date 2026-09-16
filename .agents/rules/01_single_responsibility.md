# 📐 Regra 01: Princípio da Responsabilidade Única (SRP)

> **Escopo:** Arquitetura de Módulos, Classes e Funções no AMB_V2  
> **Objetivo:** Garantir que cada componente tenha apenas uma razão para mudar, separando estritamente camadas de apresentação, controle e regras de negócio.

---

## 1. Separação Estrita de Camadas

O ecossistema `amb_v2` é dividido em camadas desacopladas com fronteiras rígidas:

1. **Camada de Parsing (`cli_modules/cli_parsers.py`):**
   - **Responsabilidade:** Única e exclusivamente declarar argumentos de linha de comando, flags, tipos e textos de ajuda (`argparse`).
   - **Proibido:** Fazer chamadas de rede, ler arquivos de configuração ou executar lógica de negócios.

2. **Camada de Handlers (`cli_modules/cli_handlers.py`):**
   - **Responsabilidade:** Intermediar a entrada do terminal (`args`), extrair parâmetros, invocar os serviços apropriados e formatar a saída para o usuário (texto rico ou JSON).
   - **Proibido:** Implementar lógica de domínio ou algoritmos complexos diretamente dentro dos handlers.

3. **Camada de Ferramentas de Fachada (`integrations/<service>/tools/<tool>.py`):**
   - **Responsabilidade:** Expor uma função de serviço autocontida (`run_<tool_name>(...)`) que orquestra uma operação específica.
   - **Proibido:** Conter lógica de parsing de argumentos ou chamadas exclusivas em blocos `if __name__ == "__main__"`.

4. **Camada de Clientes e Serviços (`integrations/<service>/<client>.py`):**
   - **Responsabilidade:** Comunicação com APIs externas (Google Jules, Stitch, Antigravity, Git CLI), tratamento de rede, autenticação e serialização.
   - **Proibido:** Acessar `sys.argv`, imprimir mensagens com `print` direto (usar `log` ou retornar dados) ou depender de interfaces de usuário.

---

## 2. Declaração Explícita de Responsabilidade

Todo módulo Python deve iniciar com uma docstring contendo o cabeçalho padronizado:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ AMB_V2 - Nome do Módulo
Localização: amb_cli/caminho/para/modulo.py
Responsabilidade Única: Descrição concisa da função exata deste módulo.
"""
```

---

## 3. Diretrizes de Funções e Métodos

- **Uma Ação por Função:** Funções devem executar apenas uma tarefa atômica. Se uma função valida parâmetros, executa requisição HTTP, salva arquivo em disco e notifica o usuário, ela viola o SRP e deve ser decomposta.
- **Isolamento de Efeitos Colaterais:** Separar funções puras (cálculo de backoff, parsing de JSON, extração de texto) de funções com efeitos colaterais (chamadas I/O, escrita em disco, requisições de rede).
