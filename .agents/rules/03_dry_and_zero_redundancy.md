# 🔄 Regra 03: Zero Redundância e Fonte Única da Verdade (DRY)

> **Escopo:** Reuso de Código, Constantes e Abstrações Compartilhadas no AMB_V2  
> **Objetivo:** Eliminar duplicações de lógica, dados ou comportamento em todo o código-fonte, estabelecendo uma única fonte canônica para cada regra de negócio.

---

## 1. Princípio DRY Estrito

- **Proibição de Código Copiado:** Se a mesma lógica (validação, cálculo, formatação, regex ou chamada) for necessária em mais de um lugar, ela deve ser extraída para um módulo compartilhado.
- **Herança de Clientes Base (`BaseGoogleClient`):**
  - Todos os clientes que interagem com APIs Google (`JulesClient`, `StitchClient`, `AntigravityClient`) devem herdar de [`BaseGoogleClient`](file:///c:/Users/DiogoHungaro/Desktop/Script/amb_v2/amb_cli/integrations/common/base_google_client.py).
  - É expressamente proibido reimplementar de forma ad-hoc:
    - Retentativas automáticas com jitter e backoff exponencial.
    - Mascaramento de dados e chaves sensíveis (`mask_sensitive_data`).
    - Normalização de códigos de erro HTTP e mensagens amigáveis.
    - Sanitização de URLs de endpoint.

---

## 2. Centralização de Configuração e Paths

- **Resolução de Caminhos:**
  - Raiz do AMB_V2: resolvida unicamente por `get_amb_root()` em `config/bootstrap.py`.
  - Raiz do pacote de código: resolvida por `get_amb_package_dir()`.
  - Raiz do repositório ativo do usuário: resolvida por `find_repo_root()` em `config/config.py`.
  - Proibido recalcular caminhos com `Path(__file__).parent...` soltos pelo código fora de módulos de bootstrap.
- **Gerenciamento de Ambiente:**
  - Variáveis de ambiente são carregadas exclusivamente via `load_env_file()`.
  - Acesso a variáveis mandatórias com validação Fail-Fast é feito via `require_env(key, hint=...)`.

---

## 3. Constantes e Mensagens de Erro

- Constantes de domínio, rotas de API e strings padronizadas devem ser definidas em nível de módulo ou classe, evitando literais mágicos espalhados pelo código.
- Textos de ajuda da CLI, modelos suportados e schemas são mantidos em seus respectivos catálogos canônicos.
