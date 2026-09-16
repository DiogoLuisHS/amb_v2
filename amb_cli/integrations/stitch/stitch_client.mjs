#!/usr/bin/env node
/**
 * 🎨 AMB_V2 - Runner Node.js do Google Stitch SDK (@google/stitch-sdk)
 * Localização: amb_v2/integrations/stitch/stitch_client.mjs
 * Responsabilidade Única: Estabelecer conexão com o StitchToolClient e despachar chamadas oficiais.
 */

import { StitchToolClient, stitch } from '@google/stitch-sdk';
import fs from 'fs';
import path from 'path';

function getEnvValue(key) {
  if (process.env[key]) return process.env[key].trim().replace(/^['"]|['"]$/g, '');

  let curr = process.cwd();
  for (let i = 0; i < 6; i++) {
    const envFile = path.join(curr, '.env');
    if (fs.existsSync(envFile)) {
      try {
        const txt = fs.readFileSync(envFile, 'utf-8');
        for (const line of txt.split('\n')) {
          const t = line.trim();
          if (t.startsWith(`${key}=`)) {
            return t.split('=')[1].trim().replace(/^['"]|['"]$/g, '');
          }
        }
      } catch {}
    }
    const parent = path.dirname(curr);
    if (parent === curr) break;
    curr = parent;
  }
  return null;
}

function getApiKey() {
  return getEnvValue('STITCH_API_KEY') || getEnvValue('GEMINI_API_KEY');
}

function getProjectId() {
  return getEnvValue('STITCH_PROJECT_ID');
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

  if (!payload.projectId) {
    const envPid = getProjectId();
    if (envPid) payload.projectId = envPid;
  }

  if (apiKey) {
    process.env.STITCH_API_KEY = apiKey;
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
        const varPayload = { ...payload };
        if (!varPayload.selectedScreenIds && varPayload.screenId) {
          varPayload.selectedScreenIds = [varPayload.screenId];
          delete varPayload.screenId;
        }
        if (!varPayload.variantOptions) {
          varPayload.variantOptions = {
            variantCount: varPayload.variantCount || 3,
            creativeRange: varPayload.creativeRange || "EXPLORE"
          };
        }
        const res = await client.callTool("generate_variants", varPayload);
        response = await extractScreenDetails(client, payload.projectId, res);
        break;
      }
      case "edit_screens":
      case "edit_screen": {
        const editPayload = { ...payload };
        if (!editPayload.selectedScreenIds && editPayload.screenId) {
          editPayload.selectedScreenIds = [editPayload.screenId];
          delete editPayload.screenId;
        }
        const res = await client.callTool("edit_screens", editPayload);
        response = await extractScreenDetails(client, payload.projectId, res);
        break;
      }
      case "get_screen": {
        const screenName = payload.name || `projects/${payload.projectId}/screens/${payload.screenId}`;
        const res = await client.callTool("get_screen", {
          name: screenName,
          projectId: payload.projectId,
          screenId: payload.screenId
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
      case "create_project": {
        response = await client.callTool("create_project", payload || {});
        break;
      }
      case "list_projects": {
        response = await client.callTool("list_projects", payload || {});
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
      case "create_design_system": {
        response = await client.callTool("create_design_system", payload);
        break;
      }
      case "update_design_system": {
        response = await client.callTool("update_design_system", payload);
        break;
      }
      case "list_design_systems": {
        response = await client.callTool("list_design_systems", payload || {});
        break;
      }
      case "apply_design_system": {
        response = await client.callTool("apply_design_system", payload);
        break;
      }
      case "download_assets": {
        response = await client.callTool("download_assets", payload);
        break;
      }
      case "upload":
      case "upload_asset": {
        const proj = stitch.project(payload.projectId);
        const screens = await proj.upload(payload.filePath, payload.opts || {});
        response = {
          success: true,
          screens: (screens || []).map(s => ({
            id: s.id,
            screenId: s.screenId,
            projectId: s.projectId
          }))
        };
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
