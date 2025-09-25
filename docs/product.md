Option 2 — Google Cloud Run (managed, secure)

Push image to Google Container Registry / Artifact Registry and deploy to Cloud Run.
Set env vars in Cloud Run (AGENT_SECRET, GEMMA_MODEL) and attach the service account with appropriate Vertex AI permissions.
Benefits: automatic HTTPS, scaling, managed uptime.
Secrets and credentials
In the Agent deployment, set:
AGENT_SECRET — secret string used by the GitHub Actions workflow to authenticate requests.
GITHUB_TOKEN — for agent to post comments or open fix PRs (this should be a least-privilege PAT or a GitHub App installation token).
For Gemma (Vertex AI):
GOOGLE_APPLICATION_CREDENTIALS — path to service account JSON (mounted into container) or rely on GCE/CloudRun built-in service account + assigned roles.
GEMMA_MODEL — model name (e.g., gemma-13b).
If using GitHub Actions in the other repos, set their repo secrets:
AGENT_URL — public URL of your agent (https://agent.example.com)
AGENT_SECRET — same secret provided to agent
