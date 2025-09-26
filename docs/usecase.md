Case 1: Build Error (Java Maven)

Log:
Could not resolve dependency org.apache.httpcomponents:httpclient:4.5.3

Agent output:

Build failed because dependency httpclient:4.5.3 is not available in central repo.
✅ Solution: Update pom.xml to 4.5.13 (latest stable).

Case 2: Test Failure (Python)

Log:
AssertionError: expected 200 but got 500

Agent output:

Test test_create_user failed due to 500 error from /users endpoint.
Last commit modified user_service.py → likely missing null-check in create_user.
✅ Suggestion: Add validation for empty username.

Case 3: CI Misconfiguration

Log:
Error: The workflow is not valid. .github/workflows/deploy.yml (Line: 12, Col: 15): Unexpected value 'usr'

Agent output:

The CI failed because of a YAML syntax issue in deploy.yml.
At line 12, replace usr with uses.
