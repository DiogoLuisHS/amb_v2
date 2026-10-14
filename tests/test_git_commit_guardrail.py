import os
import subprocess
import pytest
from core.bootstrap import ensure_amb_env

ensure_amb_env()

@pytest.fixture
def temp_git_repo(tmp_path):
    """Fixture that creates a temporary git repository."""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)

    # Make an initial commit
    init_file = repo_dir / "init.txt"
    init_file.write_text("initial commit")
    subprocess.run(["git", "add", "init.txt"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)

    return repo_dir

def run_amb_commit(repo_dir, message, no_verify=False):
    cmd = ["amb", "git", "commit", message]
    if no_verify:
        cmd.append("--no-verify")

    result = subprocess.run(
        cmd,
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    return result

def test_git_commit_success(temp_git_repo):
    """Test successful commit with valid staged file (< 300 lines)."""
    valid_file = temp_git_repo / "valid.py"
    valid_file.write_text("print('Hello World')\n" * 10)

    subprocess.run(["git", "add", "valid.py"], cwd=temp_git_repo, check=True)

    res = run_amb_commit(temp_git_repo, "Add valid file")

    assert res.returncode == 0
    assert "✔ Commit realizado com sucesso!" in res.stdout

    # Verify the commit was actually made
    git_log = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=temp_git_repo, capture_output=True, text=True)
    assert "Add valid file" in git_log.stdout

def test_git_commit_blocked_violation(temp_git_repo):
    """Test commit is blocked when file violates rules (> 300 lines)."""
    invalid_file = temp_git_repo / "invalid.py"
    invalid_file.write_text("print('Hello World')\n" * 301)

    subprocess.run(["git", "add", "invalid.py"], cwd=temp_git_repo, check=True)

    res = run_amb_commit(temp_git_repo, "Add invalid file")

    assert res.returncode == 0 # we didn't exit with error code in handler, but we returned
    assert "Commit abortado devido a violações arquiteturais" in res.stdout

    # Verify the commit was NOT made
    git_log = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=temp_git_repo, capture_output=True, text=True)
    assert "Add invalid file" not in git_log.stdout

def test_git_commit_no_verify_bypass(temp_git_repo):
    """Test commit bypasses validation with --no-verify."""
    invalid_file = temp_git_repo / "invalid_bypass.py"
    invalid_file.write_text("print('Hello World')\n" * 301)

    subprocess.run(["git", "add", "invalid_bypass.py"], cwd=temp_git_repo, check=True)

    res = run_amb_commit(temp_git_repo, "Add invalid file with bypass", no_verify=True)

    assert res.returncode == 0
    assert "✔ Commit realizado com sucesso!" in res.stdout

    # Verify the commit was actually made
    git_log = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=temp_git_repo, capture_output=True, text=True)
    assert "Add invalid file with bypass" in git_log.stdout
