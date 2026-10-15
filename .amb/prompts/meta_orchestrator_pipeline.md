# 🚀 Meta-Orquestração: Executar AMB Pipeline (Stitch -> Jules -> Deploy)

## Objetivo:
Você é o agente orquestrador do repositório AMB_V2 executando na Cloud VM.
Sua missão é rodar de ponta a ponta o pipeline autônomo Design-to-Deploy no projeto, utilizando o arquivo de especificação `.amb/prompts/teste_amb_gui_web.md`.

## Passos de Execução:
1. **Auditoria de Saúde Inicial**:
   Execute `python cli.py check` para validar que as chaves de API injetadas no ambiente (Stitch, Jules, Gemini) e o repositório estão 100% operacionais.

2. **Disparo do Pipeline Autônomo**:
   Execute o comando do pipeline com auto-aprovação de design (`-y`):
   ```bash
   python cli.py pipeline .amb/prompts/teste_amb_gui_web.md -y
   ```

3. **O que o pipeline fará automaticamente**:
   - Conectará ao **Google Stitch SDK** via `STITCH_API_KEY` e gerará o layout visual do AMB Web Console.
   - Extrairá o DOM e os design tokens gerados pelo Stitch.
   - Sintetizará o prompt consolidado de design e regras arquiteturais.
   - Criará uma **segunda sessão no Google Jules Cloud VM** (`JULES_API_KEY`) para desenvolver o código da interface.
   - Monitorará a sessão do Jules desenvolvedor, aguardará a conclusão, executará os testes locais de QA (`pytest`) e consolidará a entrega.

4. **Conclusão**:
   Acompanhe os logs gerados na tela, reporte o ID do Stitch gerado, o ID da nova sessão de desenvolvimento criada no Jules e confirme a finalização com sucesso.
