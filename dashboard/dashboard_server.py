#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛰️ AMB_V2 - Dashboard Unificado (Google Jules & Stitch)
Localização: amb_v2/dashboard/dashboard_server.py
Responsabilidade: Servidor web leve e SPA em tempo real para monitorar sessões, chats e telas.
"""

import os
import sys
import json
import socketserver
import http.server
import urllib.parse
import subprocess

# Bootstrap dinâmico de caminhos amb_v2
_cur = os.path.dirname(os.path.abspath(__file__))
while _cur and os.path.basename(_cur) != "amb_v2":
    _p = os.path.dirname(_cur)
    if _p == _cur:
        break
    _cur = _p
_AMB = _cur
for _sub in [
    "config", "agents", "pipeline", "dashboard", "dashboard/watchers",
    "integrations/jules", "integrations/jules/tools",
    "integrations/stitch", "integrations/stitch/tools",
    "integrations/antigravity", "integrations/antigravity/tools",
    "integrations/render", "integrations/render/tools",
]:
    _p = os.path.normpath(os.path.join(_AMB, *_sub.split("/")))
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from config import Colors, get_repo_name
from jules_client import JulesClient

PORT = int(os.environ.get("DASHBOARD_PORT", 3333))
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STITCH_RUNNER = os.path.abspath(os.path.join(CURRENT_DIR, "..", "integrations", "stitch", "stitch_client.mjs"))

HTML_PAGE = """<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AMB_V2 — Live Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background-color: #0c0d0e; }
    code, pre { font-family: 'JetBrains Mono', monospace; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-thumb { background: #26282b; border-radius: 4px; }
  </style>
</head>
<body class="text-slate-200 h-screen w-screen flex flex-col overflow-hidden">

  <!-- Header -->
  <header class="border-b border-slate-800 bg-[#121316] px-4 h-14 flex items-center justify-between shrink-0">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow">🛰️</div>
      <div>
        <h1 class="font-bold text-sm text-white flex items-center gap-2">
          AMB_V2 <span class="text-indigo-400 font-medium">Control Center</span>
          <span class="px-1.5 py-0.5 text-[9px] font-bold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">LIVE</span>
        </h1>
        <p class="text-[11px] text-slate-400">Monitor Unificado Google Jules & Stitch</p>
      </div>
    </div>

    <!-- Tabs & Refresh -->
    <div class="flex items-center gap-3">
      <div class="flex bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
        <button id="tabJulesBtn" onclick="switchTab('jules')" class="px-3 py-1 rounded-md font-semibold bg-indigo-600 text-white">🛰️ Jules & IA</button>
        <button id="tabStitchBtn" onclick="switchTab('stitch')" class="px-3 py-1 rounded-md font-semibold text-slate-400 hover:text-white">🎨 Stitch Design</button>
      </div>
      <button onclick="refreshData()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-200 transition">Atualizar</button>
    </div>
  </header>

  <!-- Main View -->
  <main class="flex-1 w-full p-3 overflow-hidden flex flex-col">
    
    <!-- ABA JULES -->
    <div id="julesView" class="w-full h-full grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 overflow-hidden">
      <!-- Sidebar -->
      <aside class="lg:col-span-4 xl:col-span-3 flex flex-col bg-[#121316] border border-slate-800 rounded-xl p-3 h-full overflow-hidden">
        <div class="flex items-center justify-between mb-2 text-xs font-bold text-slate-300">
          <span>📋 Sessões de Desenvolvimento</span>
          <span id="sessionsCount" class="font-mono text-slate-500">0</span>
        </div>
        <input type="text" id="searchInput" oninput="filterSessions()" placeholder="Filtrar sessões..." class="w-full bg-slate-900 border border-slate-800 text-xs rounded-lg px-2.5 py-1.5 text-slate-200 mb-2 focus:outline-none focus:border-indigo-500">
        <div id="sessionsList" class="flex-1 overflow-y-auto space-y-1.5 pr-1"></div>
      </aside>

      <!-- Chat & Logs -->
      <section class="lg:col-span-8 xl:col-span-9 flex flex-col bg-[#121316] border border-slate-800 rounded-xl h-full overflow-hidden">
        <div id="sessionHeader" class="p-3 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between shrink-0">
          <div>
            <div class="flex items-center gap-2">
              <span id="activeBadge" class="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-slate-800 text-slate-400">Selecione</span>
              <h2 id="activeTitle" class="text-xs font-bold text-white truncate max-w-xl">Nenhuma sessão selecionada</h2>
            </div>
            <p id="activeId" class="text-[11px] font-mono text-slate-500 mt-0.5">ID: —</p>
          </div>
        </div>
        <div id="activitiesFeed" class="flex-1 overflow-y-auto p-4 space-y-3">
          <div class="flex items-center justify-center h-full text-slate-500 text-xs">Selecione uma sessão na lateral.</div>
        </div>
        <div id="replyBar" class="p-2 border-t border-slate-800 bg-slate-900/80 flex items-center gap-2 shrink-0 hidden">
          <input type="text" id="manualReplyInput" placeholder="Enviar instrução ao Jules..." class="flex-1 bg-slate-950 border border-slate-800 text-xs rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500">
          <button onclick="sendManualReply()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-lg transition">Enviar</button>
        </div>
      </section>
    </div>

    <!-- ABA STITCH -->
    <div id="stitchView" class="hidden w-full h-full grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 overflow-hidden">
      <!-- Sidebar Stitch -->
      <aside class="lg:col-span-4 xl:col-span-3 flex flex-col bg-[#121316] border border-slate-800 rounded-xl p-3 h-full overflow-hidden">
        <div class="flex items-center justify-between mb-2 text-xs font-bold text-slate-300">
          <span>🎨 Telas e Componentes</span>
          <span id="stitchCount" class="font-mono text-slate-500">0</span>
        </div>
        <select id="stitchProjSelect" onchange="onStitchProjChange()" class="w-full bg-slate-900 border border-slate-800 text-xs rounded-lg px-2.5 py-1.5 text-slate-200 mb-2 focus:outline-none">
          <option value="">Carregando projetos...</option>
        </select>
        <div id="stitchList" class="flex-1 overflow-y-auto space-y-1.5 pr-1"></div>
      </aside>

      <!-- Chat Feed Stitch -->
      <section class="lg:col-span-8 xl:col-span-9 flex flex-col bg-[#121316] border border-slate-800 rounded-xl h-full overflow-hidden">
        <div class="p-3 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between shrink-0">
          <div>
            <h2 id="stitchTitle" class="text-xs font-bold text-white">Selecione uma tela Stitch</h2>
            <p id="stitchId" class="text-[11px] font-mono text-slate-500">Screen ID: —</p>
          </div>
          <a href="https://stitch.withgoogle.com" target="_blank" class="px-2.5 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 border border-slate-700">Abrir no Stitch ↗</a>
        </div>
        <div id="stitchFeed" class="flex-1 overflow-y-auto p-4 space-y-3">
          <div class="flex items-center justify-center h-full text-slate-500 text-xs">Selecione uma tela na lateral.</div>
        </div>
        <div class="p-2 border-t border-slate-800 bg-slate-900/80 flex items-center gap-2 shrink-0">
          <input type="text" id="stitchPromptInput" placeholder="Enviar novo prompt de design ao Stitch SDK..." class="flex-1 bg-slate-950 border border-slate-800 text-xs rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500">
          <button onclick="sendStitchPrompt()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-lg transition">Gerar no Stitch</button>
        </div>
      </section>
    </div>

  </main>

  <script>
    let currentTab = 'jules';
    let allSessions = [], selectedSessionId = null;
    let stitchProjects = [], selectedStitchProjId = null, allStitchScreens = [], selectedScreenId = null;

    function switchTab(tab) {
      currentTab = tab;
      document.getElementById('tabJulesBtn').className = `px-3 py-1 rounded-md font-semibold ${tab === 'jules' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`;
      document.getElementById('tabStitchBtn').className = `px-3 py-1 rounded-md font-semibold ${tab === 'stitch' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`;
      document.getElementById('julesView').classList.toggle('hidden', tab !== 'jules');
      document.getElementById('stitchView').classList.toggle('hidden', tab !== 'stitch');
      if (tab === 'stitch' && stitchProjects.length === 0) fetchStitch();
    }

    async function fetchSessions() {
      try {
        const res = await fetch('/api/sessions');
        const data = await res.json();
        allSessions = data.sessions || [];
        renderSessions(allSessions);
        if (!selectedSessionId && allSessions.length > 0) {
          selectSession(allSessions[0].id || allSessions[0].name.split('/').pop());
        } else if (selectedSessionId && currentTab === 'jules') {
          loadSessionActivities(selectedSessionId, false);
        }
      } catch (e) {}
    }

    function renderSessions(list) {
      document.getElementById('sessionsCount').innerText = list.length;
      const c = document.getElementById('sessionsList');
      c.innerHTML = list.map(s => {
        const id = s.id || s.name.split('/').pop();
        const active = id === selectedSessionId;
        return `
          <div onclick="selectSession('${id}')" class="p-2.5 rounded-lg border text-xs cursor-pointer transition ${active ? 'bg-indigo-600/10 border-indigo-500/50' : 'bg-slate-900/50 border-slate-800 hover:bg-slate-800/50'}">
            <div class="flex items-center justify-between mb-1">
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${s.state === 'IN_PROGRESS' ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-400'}">${s.state || 'ACTIVE'}</span>
              <span class="text-[10px] text-slate-500">${formatDate(s.createTime)}</span>
            </div>
            <div class="font-medium text-slate-200 truncate">${escapeHtml(s.title || 'Sessão')}</div>
          </div>
        `;
      }).join('');
    }

    function selectSession(id) {
      selectedSessionId = id;
      const s = allSessions.find(x => (x.id || x.name.split('/').pop()) === id);
      if (!s) return;
      document.getElementById('activeBadge').innerText = s.state || 'ACTIVE';
      document.getElementById('activeTitle').innerText = s.title || 'Sessão';
      document.getElementById('activeId').innerText = `ID: ${id}`;
      document.getElementById('replyBar').classList.toggle('hidden', s.state === 'COMPLETED');
      renderSessions(allSessions);
      loadSessionActivities(id, true);
    }

    async function loadSessionActivities(id, scroll) {
      try {
        const res = await fetch(`/api/sessions/${id}/activities`);
        const data = await res.json();
        renderActivities(data.activities || [], scroll);
      } catch (e) {}
    }

    function renderActivities(acts, scroll) {
      const c = document.getElementById('activitiesFeed');
      if (!acts.length) {
        c.innerHTML = '<div class="text-slate-500 text-xs text-center py-8">Nenhuma atividade registrada ainda.</div>';
        return;
      }
      c.innerHTML = acts.map(a => {
        const time = formatDate(a.createTime);
        if (a.userMessage) {
          return `<div class="p-3 bg-indigo-950/30 border border-indigo-500/30 rounded-xl text-xs"><div class="text-cyan-400 font-bold mb-1">👤 Usuário <span class="text-slate-500 text-[10px] float-right">${time}</span></div><div class="whitespace-pre-wrap">${escapeHtml(a.userMessage.text || '')}</div></div>`;
        }
        if (a.agentMessage) {
          return `<div class="p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs"><div class="text-indigo-400 font-bold mb-1">🤖 Jules <span class="text-slate-500 text-[10px] float-right">${time}</span></div><div class="whitespace-pre-wrap">${escapeHtml(a.agentMessage.text || '')}</div></div>`;
        }
        if (a.bashCommand) {
          return `<div class="p-2.5 bg-black/60 border border-slate-800 rounded-lg text-xs font-mono"><div class="text-amber-400 text-[10px] font-bold mb-1">💻 BASH <span class="text-slate-500 float-right">${time}</span></div><code class="text-amber-200">$ ${escapeHtml(a.bashCommand.command || '')}</code></div>`;
        }
        const patch = a.artifacts?.[0]?.changeSet?.gitPatch?.unidiffPatch;
        if (patch) {
          const files = patch.split('\\n')[0].replace('diff --git a/', '').replace(' b/', ' -> ');
          return `<div class="p-2 bg-slate-900/60 border border-indigo-500/20 rounded-lg text-xs flex justify-between items-center"><span class="font-mono text-indigo-300 truncate">📝 Edit: ${escapeHtml(files || 'Código')}</span><span class="text-[10px] text-slate-500">${time}</span></div>`;
        }
        return `<div class="p-2 bg-slate-900/30 border border-slate-800/40 rounded text-xs text-slate-400 flex justify-between"><span>${escapeHtml(a.description || 'Atividade')}</span><span class="text-[10px] text-slate-500">${time}</span></div>`;
      }).join('');
      if (scroll) c.scrollTop = c.scrollHeight;
    }

    async function sendManualReply() {
      const input = document.getElementById('manualReplyInput');
      const msg = input.value.trim();
      if (!msg || !selectedSessionId) return;
      await fetch(`/api/sessions/${selectedSessionId}/send_message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      input.value = '';
      setTimeout(() => loadSessionActivities(selectedSessionId, true), 1000);
    }

    async function fetchStitch() {
      try {
        const res = await fetch('/api/stitch/projects');
        const data = await res.json();
        stitchProjects = data.projects || [];
        const sel = document.getElementById('stitchProjSelect');
        sel.innerHTML = stitchProjects.map(p => `<option value="${p.id || p.name.split('/').pop()}">${escapeHtml(p.title || 'Projeto')}</option>`).join('');
        selectedStitchProjId = stitchProjects[0]?.id || stitchProjects[0]?.name?.split('/')?.pop();
        if (selectedStitchProjId) loadStitchScreens(selectedStitchProjId);
      } catch (e) {}
    }

    function onStitchProjChange() {
      selectedStitchProjId = document.getElementById('stitchProjSelect').value;
      if (selectedStitchProjId) loadStitchScreens(selectedStitchProjId);
    }

    async function loadStitchScreens(projId) {
      try {
        const res = await fetch(`/api/stitch/screens?projectId=${projId}`);
        const data = await res.json();
        allStitchScreens = data.screens || [];
        document.getElementById('stitchCount').innerText = allStitchScreens.length;
        const c = document.getElementById('stitchList');
        c.innerHTML = allStitchScreens.map(s => {
          const id = s.id || s.name?.split('/')?.pop();
          const active = id === selectedScreenId;
          return `
            <div onclick="selectStitchScreen('${id}')" class="p-2.5 rounded-lg border text-xs cursor-pointer transition ${active ? 'bg-indigo-600/10 border-indigo-500/50' : 'bg-slate-900/50 border-slate-800 hover:bg-slate-800/50'}">
              <div class="font-medium text-slate-200 truncate">${escapeHtml(s.title || 'Tela')}</div>
              <div class="text-[10px] font-mono text-slate-500 truncate mt-0.5">ID: ${id}</div>
            </div>
          `;
        }).join('');
        if (!selectedScreenId && allStitchScreens.length > 0) {
          selectStitchScreen(allStitchScreens[0].id || allStitchScreens[0].name.split('/').pop());
        }
      } catch (e) {}
    }

    async function selectStitchScreen(id) {
      selectedScreenId = id;
      const s = allStitchScreens.find(x => (x.id || x.name?.split('/')?.pop()) === id) || {};
      document.getElementById('stitchTitle').innerText = s.title || 'Tela Stitch';
      document.getElementById('stitchId').innerText = `Screen ID: ${id}`;
      loadStitchScreens(selectedStitchProjId);

      const res = await fetch(`/api/stitch/screen_details?projectId=${selectedStitchProjId}&screenId=${id}`);
      const details = await res.json();
      renderStitchChat(details, s.title, s);
    }

    function renderStitchChat(details, title, s) {
      const c = document.getElementById('stitchFeed');
      const time = formatDate(s.updateTime || s.createTime || new Date());
      const img = details.screenshotUrl || s.screenshot?.downloadUrl;
      const desc = details.description || s.description || '';
      const msgs = details.messages || [];

      let html = `
        <div class="p-3 bg-indigo-950/30 border border-indigo-500/30 rounded-xl text-xs space-y-1">
          <div class="text-cyan-300 font-bold flex justify-between"><span>👤 Tela / Prompt</span><span class="text-slate-500 text-[10px]">${time}</span></div>
          <div class="text-slate-200 font-medium">${escapeHtml(title || 'Especificação')}</div>
          ${desc ? `<div class="text-slate-400 mt-1">${escapeHtml(desc)}</div>` : ''}
        </div>
      `;

      if (msgs.length > 0) {
        msgs.forEach(m => {
          html += `
            <div class="p-3.5 bg-slate-900 border border-slate-800 rounded-xl text-xs space-y-2">
              <div class="text-indigo-400 font-bold flex items-center justify-between">
                <span class="flex items-center gap-1.5"><span>🎨</span> Registro do agente Stitch</span>
                <span class="text-slate-500 text-[10px] font-mono">${time}</span>
              </div>
              <div class="text-slate-300 whitespace-pre-wrap leading-relaxed">${escapeHtml(m)}</div>
            </div>
          `;
        });
      } else {
        html += `
          <div class="p-3.5 bg-slate-900 border border-slate-800 rounded-xl text-xs space-y-2.5">
            <div class="text-indigo-400 font-bold flex items-center justify-between">
              <span class="flex items-center gap-1.5"><span>🎨</span> Registro do agente Stitch</span>
              <span class="text-slate-500 text-[10px] font-mono">${time}</span>
            </div>
            <div class="text-slate-300 leading-relaxed">
              <p>Tela concebida e renderizada aplicando o <strong>Obsidian Design System</strong> (Tailwind CSS v4, tipografia Outfit/Inter e paleta Dark Obsidian).</p>
              ${desc ? `<p class="mt-2 text-slate-400">${escapeHtml(desc)}</p>` : ''}
            </div>
          </div>
        `;
      }

      if (img) {
        html += `
          <div class="p-2 bg-slate-900 border border-slate-800 rounded-xl max-w-xl">
            <div class="text-[10px] font-bold text-slate-400 mb-1.5 px-1">📸 Preview Visual da Tela (Stitch Canvas)</div>
            <img src="${img}" alt="${escapeHtml(title)}" class="w-full h-auto rounded-lg border border-slate-800 bg-black/40">
          </div>
        `;
      }

      c.innerHTML = html;
      c.scrollTop = c.scrollHeight;
    }

    async function sendStitchPrompt() {
      const input = document.getElementById('stitchPromptInput');
      const prompt = input.value.trim();
      if (!prompt || !selectedStitchProjId) return;
      input.value = '';
      const c = document.getElementById('stitchFeed');
      c.innerHTML += `<div class="p-3 bg-indigo-950/30 border border-indigo-500/30 rounded-xl text-xs"><div class="text-cyan-300 font-bold">👤 Você</div><p class="mt-1">${escapeHtml(prompt)}</p></div><div class="p-3 text-indigo-400 text-xs font-semibold animate-pulse">🎨 Processando no Google Stitch SDK...</div>`;
      c.scrollTop = c.scrollHeight;

      const res = await fetch('/api/stitch/prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, projectId: selectedStitchProjId })
      });
      const data = await res.json();
      loadStitchScreens(selectedStitchProjId);
    }

    function filterSessions() {
      const q = document.getElementById('searchInput').value.toLowerCase();
      renderSessions(allSessions.filter(s => (s.title || '').toLowerCase().includes(q) || (s.id || '').toLowerCase().includes(q)));
    }

    function formatDate(d) {
      if (!d) return '';
      try { return new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); } catch { return ''; }
    }

    function escapeHtml(t) {
      return (t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function refreshData() {
      if (currentTab === 'jules') fetchSessions(); else fetchStitch();
    }

    fetchSessions();
    setInterval(fetchSessions, 5000);
  </script>
</body>
</html>
"""


# Cache em memória para Stitch screens
STITCH_CACHE = {}

class DashboardHTTPHandler(http.server.BaseHTTPRequestHandler):
    def send_json(self, data: dict, status: int = 200):
        try:
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            try:
                body = HTML_PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                pass
            return

        if path == "/favicon.ico":
            try:
                body = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🛰️</text></svg>'.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "image/svg+xml")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                pass
            return

        # Jules API
        if path == "/api/sessions":
            try:
                client = JulesClient()
                resp = client.list_sessions(page_size=50, repo_filter=get_repo_name())
                self.send_json({"sessions": resp if isinstance(resp, list) else resp.get("sessions", [])})
            except Exception as e:
                self.send_json({"error": str(e), "sessions": []}, 500)
            return

        if path.startswith("/api/sessions/") and path.endswith("/activities"):
            session_id = path.strip("/").split("/")[2]
            try:
                client = JulesClient()
                resp = client.list_activities(session_id=session_id, page_size=100)
                self.send_json({"activities": resp if isinstance(resp, list) else resp.get("activities", [])})
            except Exception as e:
                self.send_json({"error": str(e), "activities": []}, 500)
            return

        # Stitch API
        if path == "/api/stitch/projects":
            try:
                res = subprocess.run(["node", STITCH_RUNNER, "list_projects", "{}"], capture_output=True, text=True, timeout=15)
                data = json.loads(res.stdout) if res.returncode == 0 else {}
                self.send_json({"projects": data.get("projects", [])})
            except Exception as e:
                self.send_json({"projects": []})
            return

        if path == "/api/stitch/screens":
            proj_id = urllib.parse.parse_qs(parsed.query).get("projectId", ["15194701482505107374"])[0]
            try:
                res = subprocess.run(["node", STITCH_RUNNER, "list_screens", json.dumps({"projectId": proj_id})], capture_output=True, text=True, timeout=15)
                data = json.loads(res.stdout) if res.returncode == 0 else {}
                screens = data.get("screens", [])
                for s in screens:
                    sid = s.get("id") or s.get("name", "").split("/")[-1]
                    STITCH_CACHE[sid] = s
                self.send_json({"screens": screens})
            except Exception as e:
                self.send_json({"screens": []})
            return

        if path == "/api/stitch/screen_details":
            query = urllib.parse.parse_qs(parsed.query)
            proj_id = query.get("projectId", ["15194701482505107374"])[0]
            screen_id = query.get("screenId", [""])[0]
            
            # Responde imediatamente se estiver em cache
            if screen_id in STITCH_CACHE and "screenshotUrl" in STITCH_CACHE[screen_id]:
                self.send_json(STITCH_CACHE[screen_id])
                return

            try:
                res = subprocess.run(["node", STITCH_RUNNER, "get_screen", json.dumps({"projectId": proj_id, "screenId": screen_id})], capture_output=True, text=True, timeout=15)
                data = json.loads(res.stdout) if res.returncode == 0 else {}
                STITCH_CACHE[screen_id] = {**STITCH_CACHE.get(screen_id, {}), **data}
                self.send_json(STITCH_CACHE[screen_id])
            except Exception as e:
                self.send_json(STITCH_CACHE.get(screen_id, {"error": str(e)}))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/sessions/") and path.endswith("/send_message"):
            session_id = path.strip("/").split("/")[2]
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                JulesClient().send_message(session_id=session_id, message=data.get("message", ""))
                self.send_json({"success": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        if path == "/api/stitch/prompt":
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                res = subprocess.run(
                    ["node", STITCH_RUNNER, "generate_screen_from_text", json.dumps({"projectId": data.get("projectId"), "prompt": data.get("prompt")})],
                    capture_output=True, text=True, timeout=60
                )
                self.send_json(json.loads(res.stdout) if res.returncode == 0 else {"error": res.stderr})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def start_dashboard(port: int = PORT):
    for p in range(port, port + 10):
        try:
            httpd = ThreadedHTTPServer(("", p), DashboardHTTPHandler)
            print("\n" + "=" * 70)
            print(f"🖥️  {Colors.BOLD}{Colors.CYAN}AMB_V2 LIVE DASHBOARD (THREADED){Colors.RESET}")
            print("=" * 70)
            print(f"🌐 Acesse: {Colors.BOLD}{Colors.GREEN}http://localhost:{p}{Colors.RESET}")
            print("🛑 Pressione Ctrl+C para encerrar.\n")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nDashboard encerrado.")
            finally:
                httpd.server_close()
            return
        except OSError as e:
            if "10048" in str(e) or "already in use" in str(e) or "soquete" in str(e):
                continue
            raise


if __name__ == "__main__":
    start_dashboard()
