#!/usr/bin/env node
/**
 * 🎨 AMB_V2 - Runner Node.js do Google Stitch SDK (@google/stitch-sdk)
 * Localização: amb_v2/integrations/stitch/stitch_client.mjs
 * Responsabilidade Única: Estabelecer conexão com o StitchToolClient e despachar chamadas oficiais.
 */

import { StitchToolClient, stitch } from '@google/stitch-sdk';
import fs from 'fs';
import path from 'path';

function getApiKey() {
  if (process.env.STITCH_API_KEY) return process.env.STITCH_API_KEY;
  if (process.env.GEMINI_API_KEY) return process.env.GEMINI_API_KEY;

  let curr = process.cwd();
  for (let i = 0; i < 6; i++) {
    const envFile = path.join(curr, '.env');
    if (fs.existsSync(envFile)) {
      const txt = fs.readFileSync(envFile, 'utf-8');
      for (const line of txt.split('\n')) {
        const t = line.trim();
        if (t.startsWith('STITCH_API_KEY=')) {
          return t.split('=')[1].trim().replace(/^['"]|['"]$/g, '');
        }
      }
    }
    const parent = path.dirname(curr);
    if (parent === curr) break;
    curr = parent;
  }
  return null;
}

async function extractScreenDetails(client, projectId, result) {
  let screenId = null;
  let screenshotUrl = null;
  let htmlCode = null;
  let title = "";
  let description = "";
  const messages = [];

  if (result && typeof result === 'object') {
    if (result.screenId) screenId = result.screenId;
    if (result.name && typeof result.name === 'string') screenId = result.name.split('/').pop();
    if (result.screenshot?.downloadUrl) screenshotUrl = result.screenshot.downloadUrl;
    if (result.screenshotUrl) screenshotUrl = result.screenshotUrl;
    if (result.htmlCode?.downloadUrl) htmlCode = result.htmlCode.downloadUrl;
    if (typeof result.htmlCode === 'string') htmlCode = result.htmlCode;
    if (result.title) title = result.title;
    if (result.description) description = result.description;
    if (result.message) messages.push(result.message);

    const comps = result.outputComponents || result.output_components || [];
    for (const comp of comps) {
      if (comp.text) messages.push(comp.text.trim());
      if (comp.design?.screens) {
        for (const s of comp.design.screens) {
          if (s.name) screenId = s.name.split('/').pop();
          if (s.screenshot?.downloadUrl) screenshotUrl = s.screenshot.downloadUrl;
          if (s.htmlCode?.downloadUrl) htmlCode = s.htmlCode.downloadUrl;
          if (s.title) title = s.title;
          if (s.description) description = s.description;
        }
      }
    }
  }

  if (htmlCode && typeof htmlCode === 'string' && (htmlCode.startsWith('http://') || htmlCode.startsWith('https://'))) {
    try {
      const resp = await fetch(htmlCode);
      if (resp.ok) {
        htmlCode = await resp.text();
      }
    } catch {}
  }

  return {
    success: true,
    screenId,
    screenshotUrl,
    htmlCode,
    title,
    description,
    messages
  };
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error(JSON.stringify({
      error: "Argumentos insuficientes.",
      usage: "node stitch_client.mjs <command> '<json_payload>'"
    }));
    process.exit(1);
  }

  const [command, rawPayload] = args;
  let payload = {};
  try {
    payload = JSON.parse(rawPayload);
  } catch (e) {
    console.error(JSON.stringify({ error: `Payload JSON inválido: ${e.message}` }));
    process.exit(1);
  }

  const apiKey = getApiKey();
  if (!apiKey) {
    console.error(JSON.stringify({
      error: "STITCH_API_KEY ausente.",
      hint: "Configure STITCH_API_KEY no arquivo .env"
    }));
    process.exit(1);
  }

  try {
    const client = new StitchToolClient({ apiKey });
    let response;

    switch (command) {
      case "generate_screen":
      case "generate_screen_from_text": {
        const res = await client.callTool("generate_screen_from_text", payload);
        response = await extractScreenDetails(client, payload.projectId, res);
        break;
      }
      case "generate_variants": {
        const res = await client.callTool("generate_variants", payload);
        response = await extractScreenDetails(client, payload.projectId, res);
        break;
      }
      case "edit_screens":
      case "edit_screen": {
        const res = await client.callTool("edit_screens", payload);
        response = await extractScreenDetails(client, payload.projectId, res);
        break;
      }
      case "get_screen": {
        const res = await client.callTool("get_screen", {
          projectId: payload.projectId,
          screenId: payload.screenId,
          name: `projects/${payload.projectId}/screens/${payload.screenId}`
        });
        response = await extractScreenDetails(client, payload.projectId, res);
        try {
          const projResp = await client.callTool("get_project", { name: `projects/${payload.projectId}` });
          const proj = projResp?.project || projResp;
          if (proj?.designTheme?.designMd) {
            response.designMd = proj.designTheme.designMd;
          }
        } catch {}
        break;
      }
      case "get_project": {
        const projName = payload.name || (payload.projectId ? `projects/${payload.projectId}` : (payload.id ? `projects/${payload.id}` : ''));
        response = await client.callTool("get_project", { name: projName });
        break;
      }
      case "list_screens": {
        const rawScreensResp = await client.callTool("list_screens", { projectId: payload.projectId });
        const screensList = rawScreensResp?.screens || [];
        
        try {
          const projName = `projects/${payload.projectId}`;
          const projResp = await client.callTool("get_project", { name: projName });
          const instances = projResp?.project?.screenInstances || projResp?.screenInstances || [];
          
          const screenMap = new Map();
          screensList.forEach(s => {
            const sid = s.id || (s.name ? s.name.split('/').pop() : '');
            if (sid) screenMap.set(sid, s);
          });

          for (const inst of instances) {
            const sid = inst.id || (inst.sourceScreen ? inst.sourceScreen.split('/').pop() : '');
            if (sid && !screenMap.has(sid)) {
              screenMap.set(sid, {
                id: sid,
                name: inst.sourceScreen || `projects/${payload.projectId}/screens/${sid}`,
                title: inst.label || inst.title || `Tela ${sid.substring(0, 8)}`,
                description: inst.description || (inst.type === 'DESIGN_SYSTEM_INSTANCE' ? 'Instância de Design System' : ''),
                width: inst.width,
                height: inst.height,
                hidden: inst.hidden
              });
            } else if (sid && screenMap.has(sid) && inst.label) {
              screenMap.get(sid).title = inst.label;
            }
          }
          response = { screens: Array.from(screenMap.values()) };
        } catch (e) {
          response = rawScreensResp;
        }
        break;
      }
      case "upload_design_md": {
        response = await client.callTool("upload_design_md", payload);
        break;
      }
      case "create_design_system_from_design_md": {
        response = await client.callTool("create_design_system_from_design_md", payload);
        break;
      }
      default: {
        response = await client.callTool(command, payload);
        break;
      }
    }

    console.log(JSON.stringify(response, null, 2));
    try { await client.close(); } catch {}
  } catch (err) {
    console.error(JSON.stringify({
      error: err.message || String(err),
      details: err.stack
    }));
    process.exit(1);
  }
}

main();
