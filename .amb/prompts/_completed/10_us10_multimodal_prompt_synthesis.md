# US-10: Síntese Multimodal de Prompts com Imagem (amb prompt --image)

## 📌 Contexto e Objetivo
Permitir passar mockups visuais locais (PNG, JPEG, WEBP) no comando `amb prompt --synthesize --image <path>` para que o Gemini analise visualmente o design da interface e gere a especificação detalhada de UI/UX para o Jules.

## 📐 Requisitos Técnicos
1. **Argumento na CLI (`cli_parsers.py`):**
   - Flag `--image`, `-i` no comando `amb prompt` e no subcomando `amb agy prompt`.
2. **Encaminhamento Multimodal (`cli_handlers.py` & `antigravity_handler.py`):**
   - Repassar `image_path` para `run_synthesize_prompt`.
3. **Backend Gemini Multimodal (`GeminiBackend` & `AntigravityClient`):**
   - Carregar bytes da imagem, codificar em Base64 e injetar em `inlineData` nos `parts` da requisição REST.
   - Ajustar o prompt de sistema para que o Gemini audite a hierarquia visual, paleta de cores, layout e componentes do mockup.
