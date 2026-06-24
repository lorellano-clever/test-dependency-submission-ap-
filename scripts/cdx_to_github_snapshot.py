#!/usr/bin/env python3
"""
Convert a CycloneDX JSON SBOM into a GitHub Dependency Submission API snapshot.

Usage inside GitHub Actions:
  python scripts/cdx_to_github_snapshot.py \
    --input downloaded-sbom.cdx.json \
    --output snapshot.json

Required in GitHub Actions:
  GITHUB_SHA
  GITHUB_REF
  GITHUB_REPOSITORY
  GITHUB_RUN_ID
  GITHUB_WORKFLOW
  GITHUB_JOB
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def get_component_key(component: dict) -> str:
    """Stable key used inside the snapshot resolved map."""
    purl = component.get("purl") or component.get("bom-ref")
    if purl:
        return purl

    group = component.get("group")
    name = component.get("name")
    version = component.get("version")

    if group and name and version:
        return f"{group}:{name}@{version}"
    if name and version:
        return f"{name}@{version}"
    if name:
        return name

    raise ValueError(f"Component without purl/bom-ref/name: {component}")


def get_package_url(component: dict) -> str:
    """GitHub strongly benefits from PURL because it can map ecosystem/name/version."""
    purl = component.get("purl") or component.get("bom-ref")
    if not purl or not purl.startswith("pkg:"):
        raise ValueError(
            f"Component must include a valid Package URL (purl). Component: {component}"
        )
    return purl


def map_scope(component_scope: str | None) -> str:
    """
    GitHub snapshot dependencies usually use runtime or development.
    CycloneDX commonly uses required/optional/excluded.
    """
    if component_scope in ("development", "dev", "test"):
        return "development"
    return "runtime"


def build_snapshot(sbom: dict, sbom_filename: str, source_location: str, sha: str, ref: str) -> dict:
    components = sbom.get("components", [])
    if not components:
        raise ValueError("CycloneDX SBOM has no components[] array.")

    resolved = {}

    for component in components:
        if component.get("type") != "library":
            continue

        package_url = get_package_url(component)
        key = get_component_key(component)

        resolved[key] = {
            "package_url": package_url,
            "relationship": "direct",
            "scope": map_scope(component.get("scope")),
        }

    if not resolved:
        raise ValueError("No library components with valid purl were found.")

    repository = os.getenv("GITHUB_REPOSITORY", "OWNER/REPO")
    run_id = os.getenv("GITHUB_RUN_ID", "local-run")
    workflow = os.getenv("GITHUB_WORKFLOW", "external-sbom-dependency-submission")
    job = os.getenv("GITHUB_JOB", "submit-external-sbom")

    return {
        "version": 0,
        "sha": sha,
        "ref": ref,
        "job": {
            "id": str(run_id),
            "correlator": f"{workflow}_{job}_{source_location}",
        },
        "detector": {
            "name": "external-sbom-cyclonedx-converter",
            "version": "1.0.0",
            "url": f"https://github.com/{repository}",
        },
        "scanned": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manifests": {
            source_location: {
                "name": sbom_filename,
                "file": {
                    "source_location": source_location,
                },
                "resolved": resolved,
            }
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CycloneDX JSON SBOM path")
    parser.add_argument("--output", required=True, help="GitHub dependency snapshot JSON output path")
    parser.add_argument("--sha", default=os.getenv("GITHUB_SHA"), help="Git commit SHA")
    parser.add_argument("--ref", default=os.getenv("GITHUB_REF", "refs/heads/main"), help="Git ref")
    parser.add_argument("--source-location", default=None, help="Logical source location shown in GitHub")
    args = parser.parse_args()

    if not args.sha:
        raise SystemExit("Missing commit SHA. Run in GitHub Actions or pass --sha <commit_sha>.")

    input_path = Path(args.input)
    sbom = json.loads(input_path.read_text(encoding="utf-8"))

    source_location = args.source_location or input_path.name
    snapshot = build_snapshot(
        sbom=sbom,
        sbom_filename=input_path.name,
        source_location=source_location,
        sha=args.sha,
        ref=args.ref,
    )

    output_path = Path(args.output)
    output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    print(f"Snapshot generated: {output_path}")
    print(f"Dependencies submitted in snapshot: {len(next(iter(snapshot['manifests'].values()))['resolved'])}")


if __name__ == "__main__":
    main()
