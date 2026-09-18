# -*- coding: utf-8 -*-
"""
Tests unitários para a integração oficial do Google Stitch SDK em AMB_V2.
Garante alinhamento estrito com os métodos e tools da especificação oficial do Stitch SDK.
"""

import os
import json
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from core.bootstrap import ensure_amb_env
ensure_amb_env()

from core import ConfigurationError, ApiExecutionError
from integrations.stitch.stitch_client import (
    StitchClient,
    generate_screen,
    edit_screen,
    get_screen,
    list_screens,
    get_project,
    create_project,
    list_projects,
    generate_variants,
    download_assets,
    upload_asset,
    create_design_system,
    update_design_system,
    list_design_systems,
    apply_design_system,
    sync_design_system,
    call_tool
)
from integrations.stitch.tools.generate_screen import run_generate_screen
from integrations.stitch.tools.edit_screen import run_edit_screen
from integrations.stitch.tools.get_screen import run_get_screen
from integrations.stitch.tools.generate_variants import run_generate_variants
from integrations.stitch.tools.download_assets import run_download_assets
from integrations.stitch.tools.sync_design_system import run_sync_design_system
from integrations.stitch.tools.list_screens import run_list_screens


@pytest.fixture(autouse=True)
def mock_stitch_env(monkeypatch):
    monkeypatch.setenv("STITCH_API_KEY", "test_stitch_key")
    monkeypatch.setenv("STITCH_PROJECT_ID", "test_project_123")


def test_stitch_client_node_missing_raises_configuration_error(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: None if bin_name == "node" else "/usr/bin/" + bin_name)
    client = StitchClient()
    with pytest.raises(ConfigurationError) as exc_info:
        client._run_node_command("get_screen", {"screenId": "s1"})
    assert "Node.js" in str(exc_info.value)
    assert "Instale o Node.js" in exc_info.value.hint


def test_stitch_client_missing_sdk_raises_configuration_error(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node" if bin_name == "node" else None)
    mock_proc = MagicMock(returncode=1, stderr="Error: Cannot find module '@google/stitch-sdk'", stdout="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    with pytest.raises(ConfigurationError) as exc_info:
        client._run_node_command("get_screen", {"screenId": "s1"})
    assert "@google/stitch-sdk" in str(exc_info.value)
    assert "npm install" in exc_info.value.hint


def test_stitch_client_generate_screen_and_output_file(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    expected = {
        "success": True,
        "screenId": "screen_abc",
        "htmlCode": "<html><body><h1>Dashboard</h1></body></html>",
        "screenshotUrl": "https://stitch.example.com/shot.png",
        "title": "Dashboard Analítico"
    }
    mock_proc = MagicMock(returncode=0, stdout=json.dumps(expected), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "dashboard.html")
        res = client.generate_screen(prompt="Criar dashboard", output_file=out_html)

        assert res["screenId"] == "screen_abc"
        assert res["title"] == "Dashboard Analítico"
        assert os.path.exists(out_html)
        with open(out_html, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<h1>Dashboard</h1>" in content


def test_stitch_client_edit_screen(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    expected = {
        "success": True,
        "screenId": "screen_abc",
        "htmlCode": "<div>Refinado</div>",
        "screenshotUrl": "https://stitch.example.com/shot_v2.png"
    }
    mock_proc = MagicMock(returncode=0, stdout=json.dumps(expected), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    res = client.edit_screen(screen_id="screen_abc", prompt="Mudar para azul")
    assert res["screenId"] == "screen_abc"
    assert res["screenshotUrl"] == "https://stitch.example.com/shot_v2.png"


def test_stitch_client_get_screen(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    expected = {
        "success": True,
        "screenId": "screen_xyz",
        "title": "Login Page",
        "screenshotUrl": "https://stitch.example.com/login.png",
        "htmlCode": "<form><input></form>"
    }
    mock_proc = MagicMock(returncode=0, stdout=json.dumps(expected), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    res = client.get_screen(screen_id="screen_xyz")
    assert res["screenId"] == "screen_xyz"
    assert res["title"] == "Login Page"


def test_stitch_client_list_screens(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    expected = {
        "screens": [
            {"id": "screen_1", "title": "Home", "width": 1920, "height": 1080},
            {"id": "screen_2", "title": "Settings", "width": 1920, "height": 1080}
        ]
    }
    mock_proc = MagicMock(returncode=0, stdout=json.dumps(expected), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    screens = client.list_screens()
    assert len(screens) == 2
    assert screens[0]["id"] == "screen_1"
    assert screens[1]["title"] == "Settings"


def test_stitch_client_get_project(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    expected = {
        "id": "test_project_123",
        "title": "Projeto Alpha",
        "designTheme": {"designMd": "# Design Tokens"}
    }
    mock_proc = MagicMock(returncode=0, stdout=json.dumps(expected), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    proj = client.get_project()
    assert proj["title"] == "Projeto Alpha"


def test_stitch_client_create_and_list_projects(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    mock_proc = MagicMock(returncode=0, stdout=json.dumps({"name": "projects/p_new", "title": "New Workspace"}), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    res = client.create_project(title="New Workspace")
    assert res["title"] == "New Workspace"

    list_mock = MagicMock(returncode=0, stdout=json.dumps({"projects": [{"title": "P1"}, {"title": "P2"}]}), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: list_mock)
    projs = client.list_projects()
    assert len(projs) == 2


def test_stitch_client_generate_variants(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    expected = {
        "success": True,
        "screenId": "var_1",
        "screenshotUrl": "https://stitch.example.com/var_1.png"
    }
    mock_proc = MagicMock(returncode=0, stdout=json.dumps(expected), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    res = client.generate_variants(screen_id="screen_123", prompt="Explorar variações com foco em contraste", variant_count=3)
    assert res["screenId"] == "var_1"


def test_stitch_client_download_and_upload_assets(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    download_mock = MagicMock(returncode=0, stdout=json.dumps({"content": [{"type": "text", "text": "Assets downloaded"}]}), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: download_mock)

    client = StitchClient()
    with tempfile.TemporaryDirectory() as tmpdir:
        res = client.download_assets(output_dir=tmpdir)
        assert "content" in res

        # Upload test
        dummy_file = os.path.join(tmpdir, "screen.png")
        with open(dummy_file, "w") as f:
            f.write("fake-png-content")

        upload_mock = MagicMock(returncode=0, stdout=json.dumps({"success": True, "screens": [{"id": "s_up"}]}), stderr="")
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: upload_mock)
        up_res = client.upload_asset(dummy_file)
        assert up_res["success"] is True


def test_stitch_client_design_system_tools(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    calls = []

    def mock_run(cmd, *args, **kwargs):
        calls.append(cmd[2])
        return MagicMock(returncode=0, stdout=json.dumps({"success": True}), stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)
    client = StitchClient()

    client.create_design_system({"displayName": "DS"})
    client.update_design_system("assets/123", {"displayName": "DS2"})
    client.list_design_systems()
    client.apply_design_system("assets/123", [{"id": "inst_1", "sourceScreen": "projects/p/screens/s1"}])

    assert calls == [
        "create_design_system",
        "update_design_system",
        "list_design_systems",
        "apply_design_system"
    ]


def test_stitch_client_sync_design_system_with_official_tools(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    calls = []
    create_payload = {}

    def mock_run(cmd, *args, **kwargs):
        nonlocal create_payload
        action = cmd[2]
        calls.append(action)
        if action == "list_design_systems":
            out = {"designSystems": []}
        elif action == "create_design_system":
            create_payload = json.loads(cmd[3])
            out = {"name": "assets/new_ds_1", "success": True}
        else:
            out = {}
        return MagicMock(returncode=0, stdout=json.dumps(out), stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)

    with tempfile.TemporaryDirectory() as tmpdir:
        design_file = os.path.join(tmpdir, "design.md")
        with open(design_file, "w", encoding="utf-8") as f:
            f.write("# Cores e Tipografia\n--primary: #10B981;\ncolorMode: LIGHT\nfont: Epilogue\nroundness: ROUND_FOUR")

        client = StitchClient()
        res = client.sync_design_system(design_md_path=design_file)
        assert res["success"] is True
        assert calls == ["list_design_systems", "create_design_system"]
        # Verifica que os tokens do design.md foram extraídos dinamicamente sem valores hardcoded a priori
        assert create_payload["designSystem"]["theme"]["customColor"] == "#10B981"
        assert create_payload["designSystem"]["theme"]["colorMode"] == "LIGHT"
        assert create_payload["designSystem"]["theme"]["headlineFont"] == "EPILOGUE"
        assert create_payload["designSystem"]["theme"]["roundness"] == "ROUND_FOUR"


def test_parse_design_tokens_and_config():
    from workspace import parse_design_tokens_from_text, get_design_system_config
    tokens = parse_design_tokens_from_text("--primary: #FF5722;\nmode: DARK\nfont: Geist\nraio: 12")
    assert tokens["customColor"] == "#FF5722"
    assert tokens["colorMode"] == "DARK"
    assert tokens["headlineFont"] == "GEIST"
    assert tokens["roundness"] == "ROUND_TWELVE"


def test_stitch_client_call_tool(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    mock_proc = MagicMock(returncode=0, stdout=json.dumps({"custom": "result"}), stderr="")
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_proc)

    client = StitchClient()
    res = client.call_tool("custom_stitch_tool", {"param": 1})
    assert res == {"custom": "result"}


def test_stitch_facade_tools_exported_and_callable():
    assert callable(run_generate_screen)
    assert callable(run_edit_screen)
    assert callable(run_get_screen)
    assert callable(run_generate_variants)
    assert callable(run_download_assets)
    assert callable(run_sync_design_system)
    assert callable(run_list_screens)


def test_stitch_client_device_type_dynamic(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda bin_name: "node")
    captured_payload = {}

    def mock_run(cmd, *args, **kwargs):
        nonlocal captured_payload
        captured_payload = json.loads(cmd[3])
        return MagicMock(returncode=0, stdout=json.dumps({"success": True, "screenId": "s_dyn"}), stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)
    client = StitchClient()

    # 1. Sem configuração de device, deviceType não é forçado (default genérico)
    client.generate_screen(prompt="Teste")
    assert "deviceType" not in captured_payload

    # 2. Configurado no .env como MOBILE
    monkeypatch.setenv("STITCH_DEVICE_TYPE", "MOBILE")
    client.generate_screen(prompt="Teste")
    assert captured_payload.get("deviceType") == "MOBILE"

    # 3. Passado explicitamente pelo usuário, sobrescreve a preferência do projeto
    client.generate_screen(prompt="Teste", device_type="TABLET")
    assert captured_payload.get("deviceType") == "TABLET"

    # 4. Device AGNOSTIC suportado
    client.generate_screen(prompt="Teste", device_type="AGNOSTIC")
    assert captured_payload.get("deviceType") == "AGNOSTIC"
