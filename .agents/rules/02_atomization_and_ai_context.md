# 🧩 Regra 02: Atomização de Arquivos e Otimização para IA

> **Escopo:** Granularidade Estrutural e Arquitetura Cognitiva no AMB_V2  
> **Objetivo:** Manter arquivos altamente coesos, granulares e compactos, otimizados para a janela de contexto de modelos de linguagem (LLMs) e agentes autônomos.

---

## 1. Limite de Linhas e Granularidade

- **Tamanho Recomendado:** Arquivos fonte devem ter preferencialmente entre **100 e 250 linhas**, com teto máximo aceitável de **300 linhas**.
- **God Files são Proibidos:** Nenhum arquivo deve acumular múltiplas responsabilidades ou se transformar em repositório genérico de utilitários ("catch-all").
- **Decomposição Modular Contínua:** Sempre que um módulo ultrapassar 300 linhas, ele deve ser refatorado em um subpacote dedicado com submódulos atômicos:
  - *Exemplo real:* `auto_reply.py` (>400 linhas) foi decomposto em `auto_reply_core/` contendo:
    - `turn_extractor.py` (extração de turnos de diálogo)
    - `cognitive_advisor.py` (filtro e geração de aconselhamento com IA)
    - `feedback_dispatcher.py` (despacho de respostas e aprovação de planos)

---

## 2. Por que Atomizar para IA?

1. **Janela de Contexto Limpa:** Modelos como Google Jules e Gemini têm atenção máxima e raciocínio superior quando recebem arquivos atômicos e autocontidos, sem ruído desnecessário.
2. **Eliminação de Alucinações:** Quanto menor e mais coeso o arquivo, menor a probabilidade do modelo alucinar assinaturas de métodos ou perder invariantes de segurança.
3. **Diffs Pequenos e Conflitos Zero:** Arquivos atômicos produzem Pull Requests menores, com diffs cirúrgicos e facilidade de auto-merge no pipeline de CI/CD.

---

## 3. Diretrizes de Organização Modular

- **Ferramentas Especializadas:** Cada ferramenta em `integrations/<service>/tools/` deve residir em seu próprio arquivo dedicado (ex: `approve_plan.py`, `create_session.py`).
- **Imports Claros e Explícitos:** Proibido o uso de `from modulo import *`. Todo símbolo importado deve ser declarado explicitamente no topo do arquivo.
- **Acoplamento Fraco:** Módulos atômicos devem depender apenas de abstrações ou de interfaces mínimas necessárias para sua operação.
