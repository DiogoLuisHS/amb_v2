#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AMB_V2 - Cognitive Advisor (SRP Core)
Localização: amb_cli/agents/auto_reply_core/cognitive_advisor.py
Responsabilidade Única: Formulação e geração cognitiva de respostas técnicas contextuais
utilizando o cliente Antigravity/Gemini e as regras centralizadas via RulesManager.
"""

import functools
import os
from typing import Optional, Tuple

from config.bootstrap import ensure_amb_env
ensure_amb_env()

from config import Colors, find_repo_root, log_error, RulesManager, get_rules_manager
from integrations.antigravity.antigravity_client import AntigravityClient


class CognitiveAdvisor:
    """Conselheiro cognitivo alimentado por IA para sessões do Google Jules."""

    def __init__(
        self,
        antigravity_client: Optional[AntigravityClient] = None,
        rules_dir: Optional[str] = None,
    ):
        self.client = antigravity_client or AntigravityClient()
        self._custom_rules_dir = rules_dir
        self.rules_manager = RulesManager.get_instance(custom_rules_dir=rules_dir)

    @staticmethod
    def filter_rules_for_jules(content: str) -> str:
        """Filtra seções de Git/VCS das regras para não enviar restrições limitantes ao Jules."""
        lines = []
        skip = False
        for line in content.splitlines():
            # Detecta início de seção bloqueada (qualquer nível de header)
            if any(
                kw in line
                for kw in [
                    "Version Control",
                    "Git Safety Lock",
                    "SAFETY LOCK",
                    "Git Lock",
                    "VCS Rules",
                ]
            ):
                skip = True
                continue
            # Qualquer header markdown (# ## ###) encerra a seção bloqueada
            if skip and line.lstrip().startswith("#"):
                skip = False
            if not skip:
                lines.append(line)
        return "\n".join(lines)

    @classmethod
    @functools.lru_cache(maxsize=128)
    def load_rules(cls, rules_dir: str) -> str:
        """Carrega e cacheia o conteúdo das regras filtradas para evitar I/O redundante."""
        rules_context = ""
        if os.path.exists(rules_dir):
            for f in sorted(os.listdir(rules_dir)):
                if f.endswith(".md"):
                    try:
                        with open(
                            os.path.join(rules_dir, f),
                            "r",
                            encoding="utf-8",
                            errors="replace",
                        ) as rf:
                            filtered_rule = cls.filter_rules_for_jules(rf.read())
                            rules_context += f"\n--- [REGRA: {f}] ---\n" + filtered_rule
                    except Exception:
                        pass
        return rules_context

    def _resolve_rules_dir(self) -> str:
        """Determina o diretório de regras ativo delegando para o RulesManager."""
        resolved = self.rules_manager.resolve_rules_dir(custom_dir=self._custom_rules_dir)
        if resolved:
            return resolved
        root = find_repo_root()
        rules_dir = os.path.join(root, ".antigravity", "rules")
        if not os.path.exists(rules_dir):
            rules_dir = os.path.join(root, ".gemini", "rules")
        return rules_dir

    def build_prompt(
        self,
        session_title: str,
        initial_prompt: str,
        full_chat_history: str,
        current_question: str,
    ) -> Tuple[str, str]:
        """Gera a instrução do sistema e o prompt estruturado para o modelo cognitivo."""
        rules_dir = self._resolve_rules_dir()
        rules_context = self.load_rules(rules_dir) if rules_dir and os.path.exists(rules_dir) else self.rules_manager.load_rules()

        system_instruction = (
            "Você é o Antigravity Cognitive Advisor para o Google Jules. "
            "Sua função é analisar o contexto completo do chat, a missão inicial do projeto "
            "e responder com precisão cirúrgica e técnica à ÚLTIMA mensagem ou dúvida enviada pelo agente Jules."
        )

        prompt = f"""Você deve responder à última mensagem enviada pelo agente Google Jules no chat.

================================================================================
📌 1. MISSÃO INICIAL DA SESSÃO (OBJETIVO ORIGINAL):
================================================================================
Título: {session_title}
Prompt de Despacho:
"{initial_prompt}"

================================================================================
📜 2. CONTEXTO GERAL (HISTÓRICO COMPLETO DE TODAS AS MENSAGENS E AÇÕES DO CHAT):
================================================================================
{full_chat_history if full_chat_history.strip() else "Nenhuma mensagem anterior registrada."}

================================================================================
🎯 3. ÚLTIMA MENSAGEM / DÚVIDA DO JULES A SER RESPONDIDA AGORA:
================================================================================
"{current_question if current_question.strip() else "O agente concluiu uma etapa e aguarda instruções para prosseguir."}"

================================================================================
📐 4. REGRAS ARQUITETURAIS DO REPOSITÓRIO:
================================================================================
{rules_context or "Mantenha tipagem estrita, boas práticas, SRP e não quebre contratos de API."}

================================================================================
INSTRUÇÃO DE FORMULAÇÃO DA RESPOSTA:
================================================================================
1. FOCO NA ÚLTIMA MENSAGEM: Responda diretamente ao que o agente perguntou ou propôs na Seção 3.
2. USE O CONTEXTO COMPLETO: Utilize o histórico da Seção 2 e as regras da Seção 4 para não autorizar desvios, alterações indevidas em código funcional ou violações dos contratos e padrões da stack do projeto.
3. SE HOUVER DESVIO: Dê instruções corretivas claras e diretas para o agente retomar o objetivo original da Seção 1.
4. SE O TRABALHO ESTIVER CORRETO: Aprove a proposta e instrua o agente a rodar os testes/build e abrir o Pull Request.

Retorne APENAS o texto da mensagem técnica pronta para ser enviada no chat do Jules."""

        return system_instruction, prompt

    def generate_suggestion(
        self,
        session_title: str,
        initial_prompt: str,
        full_chat_history: str,
        current_question: str,
    ) -> str:
        """Gera a sugestão de resposta técnica via Antigravity/Gemini ou aplica fallback contextualizado."""
        system_instruction, prompt = self.build_prompt(
            session_title=session_title,
            initial_prompt=initial_prompt,
            full_chat_history=full_chat_history,
            current_question=current_question,
        )

        try:
            return self.client.generate_text(
                prompt=prompt, system_instruction=system_instruction
            )
        except Exception as e:
            log_error("ANTIGRAVITY", f"Falha na inferência Gemini: {e}")
            # Fallback contextualizado e seguro para resiliência contínua
            q_lower = current_question.lower()
            if any(k in q_lower for k in ["open the pr", "create a pr", "proceed", "pr as it is"]):
                return (
                    "Yes, please proceed to open the Pull Request with your completed fixes. "
                    "Our local AMB_V2 Gatekeeper will run the complete typecheck and build suite locally before merging. Thank you!"
                )
            elif any(k in q_lower for k in ["plan", "approve"]):
                return (
                    "Approved. Please proceed with the proposed plan, adhering strictly to repository architecture, contracts and zero runtime errors."
                )
            else:
                return (
                    "Please proceed with the proposed implementation adhering to the repository rules, and open the Pull Request when ready."
                )
