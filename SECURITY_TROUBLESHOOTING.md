# Security & Troubleshooting Notes

- Never store real credentials in source control.
- Use app passwords or dedicated service accounts for SMTP access.
- For Power BI access prefer service principals / Azure AD apps instead of user's password.
- If Playwright download fails:
  - Inspect page manually to find correct selectors.
  - Increase timeouts or use slower pacing to allow JS to finish.
  - Consider exporting a report as a PDF manually to inspect the generated request.
- If SMTP fails:
  - Verify credentials and check if MFA or app-passwords are required.
  - Check firewall or outbound port blocking (port 587).
  - Review logs in OUTPUT_DIR/automation.log for details.
