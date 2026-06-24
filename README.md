# Demo: external SBOM → GitHub Dependency Submission API

This demo simulates the following enterprise flow:

```text
JFrog / Nexus
  ↓
CycloneDX SBOM
  ↓
Converter script
  ↓
GitHub Dependency Submission API snapshot
  ↓
GitHub Dependency Graph
  ↓
Dependabot alerts
```

## Files

- `external-dependencies-simulated.cdx.json`
  - Simulated CycloneDX SBOM exported from JFrog/Nexus.
- `scripts/cdx_to_github_snapshot.py`
  - Converts CycloneDX components into a GitHub dependency snapshot.
- `.github/workflows/submit-external-sbom.yml`
  - GitHub Actions workflow that submits the snapshot to GitHub.

## Setup

1. Commit these files to the repository.
2. Enable Dependency Graph and Dependabot alerts in the repository security settings.
3. Run the workflow manually from **Actions → Submit external SBOM dependencies → Run workflow**.
4. Validate the dependencies in **Insights → Dependency graph** or **Security → Dependabot alerts**.

## Important limitation

This flow is good for proving that GitHub can ingest external dependencies and generate alerts when they match GitHub Advisory Database.

Automatic remediation PRs are not guaranteed when the dependency only exists in an external SBOM/snapshot and there is no editable manifest/lockfile in the repository. Dependabot security updates normally need something concrete to modify, such as `package.json`, `package-lock.json`, `pom.xml`, `go.mod`, etc.
