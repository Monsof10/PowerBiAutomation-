PDF Monthly Automation — How to run (for recipient)

Overview
- This Docker image runs a Playwright-based automation that logs into Power BI, navigates dashboards, and exports monthly PDFs.
- The Docker image has been exported as `pdf_automation.tar` and is included in the repository root.

Prerequisites on your machine
- Docker installed and running.
- Network access to the Power BI / authentication endpoints used by the script.
- Plain credentials (username/password) for the service account used by the automation, or an alternative secret mechanism.
- A Windows host folder to receive output files (PDFs) mounted into the container.

Load the provided image and run
1) Load the image (PowerShell):

```pwsh
# Run where pdf_automation.tar is located
docker load -i pdf_automation.tar
```

2) Start the container and map an output folder, passing credentials as env vars:

```pwsh
# Example: adjust host output path and credentials
docker run -d --name pdf_automation \
  -v C:\Users\YourUser\pdf_output:C:\app\output \
  -e PLAYWRIGHT_USERNAME=you@example.com \
  -e PLAYWRIGHT_PASSWORD=YourSecretPassword \
  --restart unless-stopped \
  pdf_monthly_automation_wip-pdf-automation:latest
```

Notes on environment and files
- Output: The container writes PDFs and logs to `/app/output` (mapped to your host path). Ensure the host path exists and Docker has write permission.
- Credentials: Prefer passing credentials via `-e` environment variables or using Docker secrets. Do NOT edit or commit credentials into the image.
- Config file: If you prefer to provide a `config.py`, mount it into `/app/config.py` instead of env vars.

Run the automation manually (testing)
- Execute the automation once to test:

```pwsh
docker exec -it pdf_automation powershell -Command "python /app/automation.py"
```

- Or non-interactive:

```pwsh
docker exec pdf_automation python /app/automation.py
```

Check logs
- View container logs:

```pwsh
docker logs -f pdf_automation
```

Scheduling
- The image contains a cron entry scheduled for the 1st of every month at 00:00. If you prefer host scheduling instead, run the image on demand from Task Scheduler or a host cron job.

Troubleshooting checklist
- Login failures: verify `PLAYWRIGHT_USERNAME` and `PLAYWRIGHT_PASSWORD` and network access. If your tenant requires MFA, the automation may not work—use a service account or app credentials.
- No output files: ensure the host directory is correctly mounted and writable.
- Playwright errors: check container logs; increase timeouts or capture screenshots by modifying `playwright_download.py` if the UI changed.

Security recommendations
- Use a service account with minimum required permissions.
- Use Docker secrets or an environment secret manager where possible.

If anything breaks
- Send me the last 200 lines of `docker logs pdf_automation` and a screenshot of the UI (if available). I can help adjust selectors or timing.

---

If you'd like, I can also produce a small `run.ps1` wrapper that automates `docker load` + `docker run` with placeholders filled in for you to distribute to the recipient. Would you like that now?