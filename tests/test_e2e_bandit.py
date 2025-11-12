import os
import subprocess
import sys
from pathlib import Path


def test_e2e_runs_bandit_multi(tmp_path):
    """End-to-end test: create a venv, install bandit and this package, run bandit -f multi and assert outputs."""
    repo_root = Path(__file__).resolve().parents[1]

    # create venv
    venv_dir = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    pip = venv_dir / "bin" / "pip"
    bandit_exe = venv_dir / "bin" / "bandit"

    # install pip packages inside venv
    subprocess.run([str(pip), "install", "-U", "pip"], check=True)
    subprocess.run([str(pip), "install", "bandit", "pytest"], check=True)

    # install this package in editable mode so the entry-point is available
    subprocess.run([str(pip), "install", "-e", str(repo_root)], check=True)

    # prepare a small sample project
    sample = tmp_path / "sample_project"
    sample.mkdir()
    vuln = sample / "vuln.py"
    vuln.write_text("""
def insecure_eval(user_input):
    eval(user_input)
""")

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    env = os.environ.copy()
    env["BANDIT_MULTI_FORMATS"] = "json,txt"
    # ensure bandit writes to our chosen folder
    env["BANDIT_MULTI_OUTPUT_DIR"] = str(out_dir)

    # run bandit CLI from the venv
    subprocess.run([
        str(bandit_exe),
        "-r",
        str(sample),
        "-f",
        "multi",
    ], env=env)

    # assert outputs exist and not empty
    assert (out_dir / "bandit_output.json").exists()
    assert (out_dir / "bandit_output.json").stat().st_size > 0
    assert (out_dir / "bandit_output.txt").exists()
    assert (out_dir / "bandit_output.txt").stat().st_size > 0
