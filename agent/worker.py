import asyncio
from asyncio import Queue
import tempfile
import os
import shutil
import subprocess
import json
from .analyzers import analyze_logs
from .llm_client import analyze_with_llm

_queue: Queue | None = None


def get_queue():
    global _queue
    if _queue is None:
        _queue = Queue()
        # start background consumer
        asyncio.create_task(_consumer())
    return _queue


async def enqueue_job(job: dict):
    q = get_queue()
    await q.put(job)


async def _consumer():
    q = get_queue()
    while True:
        job = await q.get()
        try:
            await _run_job(job)
        except Exception as e:
            print("Job failed:", e)
        finally:
            q.task_done()


async def _run_job(job: dict):
    payload = job.get("payload", {})
    # Extract clone url and ref from payload (supports PR payloads)
    pr = payload.get("pull_request") or {}
    clone_url = pr.get("head", {}).get("repo", {}).get("clone_url")
    ref = pr.get("head", {}).get("ref")
    if not clone_url or not ref:
        print("No PR details found; skipping job")
        return

    tmpdir = tempfile.mkdtemp(prefix="repro_")
    try:
        repo_dir = os.path.join(tmpdir, "repo")
        print(f"Cloning {clone_url}#{ref} into {repo_dir}")
        subprocess.check_call(["git", "clone", clone_url, repo_dir])
        subprocess.check_call(["git", "checkout", ref], cwd=repo_dir)

        # Determine build commands: by convention read agent_config.json or use defaults
        cfg_path = os.path.join(repo_dir, "agent_config.json")
        cmds = ["./build.sh"]
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                cmds = cfg.get("build_commands", cmds)

        logs = ""
        for cmd in cmds:
            print("Running:", cmd)
            try:
                # Use shell to allow common commands; in production use a more secure runner
                p = subprocess.run(cmd, cwd=repo_dir, shell=True, capture_output=True, text=True, timeout=600)
                logs += f"\n$ {cmd}\n" + p.stdout + p.stderr
            except subprocess.TimeoutExpired as e:
                logs += f"\n$ {cmd}\nTIMEOUT\n"

        # Run analyzers
        findings = analyze_logs(logs)

        # LLM analysis (placeholder)
        llm_suggestion = analyze_with_llm(logs)

        result = {"job_id": job.get("id"), "findings": findings, "llm": llm_suggestion}
        print(json.dumps(result, indent=2))

    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
