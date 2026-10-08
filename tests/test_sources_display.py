#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para a exibição enriquecida de fontes no comando `list_sources.py`.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
import io
import sys

from integrations.jules.tools.list_sources import run_list_sources
from core import Colors


class DummyJulesClient:
    def __init__(self, mock_sources):
        self.mock_sources = mock_sources

    def list_sources(self, filter_expr=None):
        return self.mock_sources


def test_private_repository_formatting(capsys):
    """Testa se repositório privado ganha a tag [🔒 Privado]."""
    mock_sources = [{
        "name": "sources/github-myorg-myrepo",
        "id": "github-myorg-myrepo",
        "githubRepo": {
            "owner": "myorg",
            "repo": "myrepo",
            "isPrivate": True,
            "defaultBranch": {
                "displayName": "main"
            }
        }
    }]
    client = DummyJulesClient(mock_sources)
    run_list_sources(as_json=False, client=client)

    captured = capsys.readouterr()
    stdout = captured.out

    assert f"{Colors.YELLOW}[🔒 Privado]{Colors.RESET}" in stdout
    assert f"{Colors.DIM}[🌿 Default: main]{Colors.RESET}" in stdout
    assert "(myorg/myrepo)" in stdout


def test_public_repository_formatting(capsys):
    """Testa se repositório público ganha a tag [🌐 Público]."""
    mock_sources = [{
        "name": "sources/github-myorg-publicrepo",
        "id": "github-myorg-publicrepo",
        "githubRepo": {
            "owner": "myorg",
            "repo": "publicrepo",
            "isPrivate": False,
            "defaultBranch": {
                "displayName": "master"
            }
        }
    }]
    client = DummyJulesClient(mock_sources)
    run_list_sources(as_json=False, client=client)

    captured = capsys.readouterr()
    stdout = captured.out

    assert f"{Colors.BLUE}[🌐 Público]{Colors.RESET}" in stdout
    assert f"{Colors.DIM}[🌿 Default: master]{Colors.RESET}" in stdout
    assert "(myorg/publicrepo)" in stdout


def test_resilience_missing_metadata(capsys):
    """Testa resiliência quando campos estão ausentes."""
    mock_sources = [{
        "name": "sources/github-minimal",
        "id": "github-minimal",
        "githubRepo": {
            "owner": "minimal",
            "repo": "repo"
            # Sem isPrivate e defaultBranch
        }
    }, {
        "name": "sources/other",
        # Sem githubRepo
    }]
    client = DummyJulesClient(mock_sources)
    run_list_sources(as_json=False, client=client)

    captured = capsys.readouterr()
    stdout = captured.out

    assert "(minimal/repo)" in stdout
    # Garantir que não crashou e não imprimiu tags vazias desnecessárias de forma feia
    assert "sources/other" in stdout


def test_as_json_ignores_ansi(capsys):
    """Testa se as_json=True retorna puramente JSON."""
    mock_sources = [{
        "name": "sources/github-myorg-myrepo",
        "githubRepo": {
            "owner": "myorg",
            "repo": "myrepo",
            "isPrivate": True,
            "defaultBranch": {"displayName": "main"}
        }
    }]
    client = DummyJulesClient(mock_sources)
    result = run_list_sources(as_json=True, client=client)

    captured = capsys.readouterr()
    stdout = captured.out

    assert result == mock_sources

    parsed = json.loads(stdout)
    assert parsed == mock_sources

    # Assegurar que ANSI colors do Colors não estão na saída JSON
    assert Colors.YELLOW not in stdout
    assert Colors.BLUE not in stdout
