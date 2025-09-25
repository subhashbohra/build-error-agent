import threading
import queue
import tempfile
import os
import shutil
import subprocess
import json
from .analyzers import analyze_logs
from .llm_client import analyze_with_llm


_queue: queue.Queue | None = None
_consumer_thread: threading.Thread | None = None


def _ensure_consumer():
    global _queue, _consumer_thread
    if _queue is None:
        _queue = queue.Queue()
    if _consumer_thread is None or not _consumer_thread.is_alive():
        _consumer_thread = threading.Thread(target=_consumer, daemon=True)
        _consumer_thread.start()


def enqueue_job(job: dict):
    _ensure_consumer()
    _queue.put(job)


def _consumer():
    q = _queue
    while True:
        job = q.get()
        try:
            _run_job(job)
        except Exception as e:
            print("Job failed:", e)
        finally:
            q.task_done()


def _run_job(job: dict):
    payload = job.get('payload', {})
    pr = payload.get('pull_request') or {}
    clone_url = pr.get('head', {}).get('repo', {}).get('clone_url')
    ref = pr.get('head', {}).get('ref')
    if not clone_url or not ref:
        print('No PR details found; skipping job')
        return

    tmpdir = tempfile.mkdtemp(prefix='repro_')
    try:
        repo_dir = os.path.join(tmpdir, 'repo')
        print(f"Cloning {clone_url}#{ref} into {repo_dir}")
        subprocess.check_call(['git', 'clone', clone_url, repo_dir])
        subprocess.check_call(['git', 'checkout', ref], cwd=repo_dir)

        # Determine build commands: by convention read agent_config.json or use defaults
        cfg_path = os.path.join(repo_dir, 'agent_config.json')
        cmds = ['./build.sh']
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                cmds = cfg.get('build_commands', cmds)

        logs = ''
        for cmd in cmds:
            print('Running:', cmd)
            try:
                p = subprocess.run(cmd, cwd=repo_dir, shell=True, capture_output=True, text=True, timeout=600)
                logs += f"\n$ {cmd}\n" + p.stdout + p.stderr
            except subprocess.TimeoutExpired:
                logs += f"\n$ {cmd}\nTIMEOUT\n"

        findings = analyze_logs(logs)
        llm_suggestion = analyze_with_llm(logs)

        result = {'job_id': job.get('id'), 'findings': findings, 'llm': llm_suggestion}
        print(json.dumps(result, indent=2))

    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
