#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AMB_V2 - Extrator de Histórico e Turnos de Conversação (SRP)
Localização: amb_cli/agents/auto_reply_core/turn_extractor.py
Responsabilidade Única: Analisar payloads de atividades da API do Jules,
extrair mensagens textuais, filtrar ruídos e determinar o último turno e status da conversação.
"""

from typing import Any, Dict, List, Optional, Tuple


class TurnHistoryExtractor:
    """Extrai e estrutura o histórico de conversações e turnos de sessões do Jules."""

    @staticmethod
    def _extract_text_from_node(node: Any, keys: List[str]) -> str:
        """Extrai a primeira ocorrência textual válida de uma lista de chaves ou string direta."""
        if isinstance(node, str) and node.strip():
            return node.strip()
        if isinstance(node, dict):
            for k in keys:
                val = node.get(k)
                if isinstance(val, str) and val.strip():
                    return val.strip()
        return ""

    @classmethod
    def extract_activity_text(cls, activity: Dict[str, Any], role: str = "agent") -> str:
        """Extrai com precisão o texto de mensagens da API do Jules para qualquer formato retornado."""
        if not activity or not isinstance(activity, dict):
            return ""

        keys = ["agentMessage", "userMessage", "text", "message", "question"]
        if role == "agent":
            for field in ["agentMessaged", "agentMessage", "userFeedbackRequired"]:
                if field in activity:
                    txt = cls._extract_text_from_node(activity[field], keys)
                    if txt:
                        return txt
        elif role == "user":
            for field in ["userMessaged", "userMessage"]:
                if field in activity:
                    txt = cls._extract_text_from_node(activity[field], keys)
                    if txt:
                        return txt

        return ""

    @classmethod
    def get_last_conversation_turn(cls, acts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa a lista de atividades (garantindo ordem da mais recente para a mais antiga)
        e determina quem falou por último e qual foi a última pergunta/plano real.
        """
        turn_info = {
            "last_speaker": None,  # 'USER' | 'AGENT' | 'PLAN' | 'SYSTEM'
            "last_user_msg": "",
            "last_agent_msg": "",
            "last_agent_msg_id": None,
            "has_unapproved_plan": False,
            "unapproved_plan_title": "",
            "is_awaiting_user_action": False,
        }

        if not acts:
            return turn_info

        # Garante ordem decrescente (mais recente primeiro) baseada em createTime se presente
        ordered_acts = list(acts)
        if any(a.get("createTime") for a in ordered_acts):
            first_time = next((a.get("createTime") for a in ordered_acts if a.get("createTime")), None)
            last_time = next((a.get("createTime") for a in reversed(ordered_acts) if a.get("createTime")), None)
            if first_time and last_time and first_time < last_time:
                ordered_acts = list(reversed(ordered_acts))

        for a in ordered_acts:
            aid = a.get("id") or a.get("name")

            # 1. Mensagem ou Ação do Usuário
            user_txt = cls.extract_activity_text(a, role="user")
            if user_txt or "planApproved" in a or a.get("planApproved"):
                if not turn_info["last_speaker"]:
                    turn_info["last_speaker"] = "USER"
                    turn_info["last_user_msg"] = user_txt or "Plano aprovado pelo usuário."
                    turn_info["is_awaiting_user_action"] = False
                    break

            # 2. Mensagem do Agente / Pergunta ou Feedback Requerido
            # NOTA: Precede planos antigos para responder dúvidas recentes do agente no chat
            agent_txt = cls.extract_activity_text(a, role="agent")
            if agent_txt:
                if not turn_info["last_speaker"]:
                    turn_info["last_speaker"] = "AGENT"
                    turn_info["last_agent_msg"] = agent_txt
                    turn_info["last_agent_msg_id"] = aid
                    turn_info["is_awaiting_user_action"] = True
                    break

            # 3. Plano com aprovação pendente
            plan = (
                a.get("plan") or a.get("agentMessage", {}).get("plan")
                if isinstance(a.get("agentMessage"), dict)
                else None
            )
            if not plan and "planGenerated" in a:
                plan = a["planGenerated"].get("plan")

            if plan and (plan.get("state") == "PENDING_USER_APPROVAL" or "steps" in plan or plan.get("id")):
                if not turn_info["last_speaker"]:
                    turn_info["last_speaker"] = "PLAN"
                    turn_info["has_unapproved_plan"] = True
                    steps = plan.get("steps", [])
                    p_title = plan.get("title") or (steps[0].get("title") if steps else "Plano de Implementação")
                    turn_info["unapproved_plan_title"] = p_title
                    turn_info["last_agent_msg_id"] = aid
                    turn_info["last_agent_msg"] = f"Plano proposto: {p_title}"
                    turn_info["is_awaiting_user_action"] = True
                    break

        return turn_info

    @classmethod
    def get_full_session_history(
        cls, client: Any, session_id: str
    ) -> Tuple[Dict[str, Any], str, str, str, Dict[str, Any]]:
        """Obtém a sessão, o prompt inicial, a conversa cronológica formatada, a última dúvida e metadados do turno."""
        session = client.get_session(session_id)
        initial_prompt = session.get("prompt", "")

        acts_resp = client.list_activities(session_id=session_id, page_size=100)
        acts = acts_resp if isinstance(acts_resp, list) else acts_resp.get("activities", [])

        turn_info = cls.get_last_conversation_turn(acts)

        # Garante ordem cronológica estrita (mais antiga primeiro) para exibição linear da conversa
        chronological_acts = list(acts)
        if any(a.get("createTime") for a in chronological_acts):
            first_time = next((a.get("createTime") for a in chronological_acts if a.get("createTime")), None)
            last_time = next((a.get("createTime") for a in reversed(chronological_acts) if a.get("createTime")), None)
            if first_time and last_time and first_time > last_time:
                chronological_acts = list(reversed(chronological_acts))

        chat_lines = []
        current_question = turn_info.get("last_agent_msg", "")

        for a in chronological_acts:
            time_str = a.get("createTime", "")[:19].replace("T", " ")

            # Mensagem do Usuário
            user_txt = cls.extract_activity_text(a, role="user")
            if user_txt:
                chat_lines.append(f"[{time_str}] 👤 USUÁRIO:\n{user_txt}\n")

            # Mensagem do Jules
            agent_txt = cls.extract_activity_text(a, role="agent")
            if agent_txt:
                chat_lines.append(f"[{time_str}] 🤖 AGENTE JULES:\n{agent_txt}\n")
                current_question = agent_txt

            # Comando Bash
            elif a.get("bashCommand"):
                cmd = a["bashCommand"].get("command", "")
                out = a["bashCommand"].get("output", "")
                trunc_out = out[:800] + (
                    f"\n...[+{len(out) - 800} chars omitidos]" if len(out) > 800 else ""
                )
                chat_lines.append(
                    f"[{time_str}] 💻 BASH: `$ {cmd}`\nOutput:\n{trunc_out}\n"
                )

            # Plano do Agente
            elif a.get("plan") or a.get("planGenerated"):
                p_obj = a.get("plan") or a.get("planGenerated", {}).get("plan") or {}
                plan_title = p_obj.get("title", "")
                steps = p_obj.get("steps", [])
                step_lines = "\n".join(
                    [
                        f"   - [{'x' if s.get('state') == 'COMPLETED' else ' '}] {s.get('description', '')}"
                        for s in steps
                    ]
                )
                chat_lines.append(
                    f"[{time_str}] 📋 PLANO PROPOSTO: {plan_title}\n{step_lines}\n"
                )

            # Progresso ou Avaliação do Agente
            elif a.get("progressUpdated"):
                p_title = a["progressUpdated"].get("title", "")
                p_desc = a["progressUpdated"].get("description", "")
                chat_lines.append(
                    f"[{time_str}] 📊 PROGRESSO/AVALIAÇÃO: {p_title}\n{p_desc}\n"
                )

        full_history = "\n".join(chat_lines)
        return session, initial_prompt, full_history, current_question, turn_info
