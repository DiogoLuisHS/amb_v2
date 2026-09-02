# 🎯 Feature: Painel de Saúde do Sistema & Status de Integrações (System Health)

## 1. 🎨 Especificação Visual (Google Stitch SDK)
Criar uma interface moderna e premium no formato Dashboard Desktop:
- **Header Superior**: Título "AMB_V2 System Health", badge verde pulsante "ALL SYSTEMS OPERATIONAL" e botão de ação secundária "Run Diagnostic".
- **Grid de Cards KPI (4 colunas)**:
  1. *Google Jules API*: Status "99.8% Uptime", latência "120ms", ícone de nuvem.
  2. *Google Stitch SDK*: Status "Connected", 24 telas geradas hoje, ícone de paleta de cores.
  3. *Google Gemini 3.7*: Status "Active", tempo médio de resposta "480ms", ícone de cérebro IA.
  4. *Render Cloud*: Status "Live", 3 serviços monitorados, ícone de servidor.
- **Tabela / Feed de Eventos Recentes**:
  - Lista com as últimas 5 execuções de sessões (ID, Persona, Status Badge, Duração e Ações).
- **Estética Visual**:
  - Tema escuro sofisticado com tons neutros escuros (`#0F172A`, `#1E293B`), bordas sutis com glassmorphism, tipografia limpa (Inter/Roboto) e badges semânticos coloridos (verde, azul, roxo e amarelo).

---

## 2. ⚡ Especificação de Engenharia (Google Jules & Antigravity)
Implementar os componentes e utilitários correspondentes seguindo os padrões arquiteturais:
1. **Estrutura de Componentes**:
   - Criar módulo desacoplado seguindo SRP (Princípio da Responsabilidade Única).
   - Tipagem rigorosa com TypeScript / interfaces para `SystemMetric`, `ServiceStatus` e `SessionEvent`.
2. **Contratos & Resiliência**:
   - Tratar estados de loading, vazio e erro para cada serviço monitorado.
   - Garantir 0 erros de compilação no typecheck e build de produção.
3. **Padrões de Código**:
   - Funções puras para formatação de datas e cálculo de latências.
   - Preservar separação estrita de camadas e arquitetura limpa.
