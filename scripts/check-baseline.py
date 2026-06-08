#!/usr/bin/env python3
from pathlib import Path
import ast
import json
import re
import warnings
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/plans/2026-06-08-hosts-baseline.md"
HOST_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
HEADER_COUNT_RE = re.compile(r"Number of unique domains:\s*([0-9,]+)")


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def parse_xml(relative_path, failures):
    try:
        ET.parse(str(ROOT / relative_path))
    except ET.ParseError as error:
        failures.append(f"{relative_path} is not well-formed XML: {error}")


def load_json(relative_path, failures):
    try:
        return json.loads(read(relative_path))
    except Exception as error:
        failures.append(f"{relative_path} is not valid JSON: {error}")
        return {}


def check_python_compile(failures):
    source = read("updateFile.py")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", SyntaxWarning)
            compile(source, str(ROOT / "updateFile.py"), "exec")
        ast.parse(source, filename=str(ROOT / "updateFile.py"))
    except Exception as error:
        failures.append(f"updateFile.py must compile without SyntaxWarning: {error}")


def check_hosts_file(failures):
    hosts_text = read("hosts")
    header_match = HEADER_COUNT_RE.search(hosts_text)
    require(header_match is not None, "hosts header must include Number of unique domains", failures)

    block_hosts = []
    malformed = []
    allowed_static_hosts = {
        "localhost",
        "localhost.localdomain",
        "local",
        "broadcasthost",
        "0.0.0.0",
        "sbc",
    }

    for line_number, line in enumerate(hosts_text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split()
        if len(parts) < 2:
            malformed.append(f"line {line_number}: expected address and host")
            continue

        address, hostname = parts[0], parts[1]
        if address == "0.0.0.0" and hostname != "0.0.0.0":
            block_hosts.append(hostname)

        if hostname not in allowed_static_hosts and not HOST_RE.match(hostname):
            malformed.append(f"line {line_number}: malformed host {hostname}")

    if header_match is not None:
        expected_count = int(header_match.group(1).replace(",", ""))
        require(len(block_hosts) == expected_count,
                f"hosts block entry count {len(block_hosts)} must match header {expected_count}",
                failures)

    duplicate_count = len(block_hosts) - len(set(block_hosts))
    require(duplicate_count == 0, f"hosts must not contain duplicate block entries ({duplicate_count} found)", failures)
    require(not malformed, "hosts contains malformed data lines: " + "; ".join(malformed[:5]), failures)
    require("# Date:" in hosts_text and "# Project home page: https://github.com/StevenBlack/hosts" in hosts_text,
            "hosts must keep generated header provenance",
            failures)


def check_readme_data(failures):
    data = load_json("readmeData.json", failures)
    require(isinstance(data, dict), "readmeData.json root must be an object", failures)
    require(len(data) >= 16, "readmeData.json must keep the known alternate metadata sets", failures)

    source_refs = 0
    for config_name, metadata in data.items():
        require(isinstance(metadata, dict), f"{config_name} metadata must be an object", failures)
        require("entries" in metadata and isinstance(metadata.get("entries"), int),
                f"{config_name} must include integer entries", failures)
        require("location" in metadata, f"{config_name} must include location", failures)
        sources = metadata.get("sourcesdata")
        require(isinstance(sources, list), f"{config_name} sourcesdata must be a list", failures)

        for source in sources or []:
            source_refs += 1
            for field in ["name", "url", "frequency", "homeurl", "issues", "description"]:
                require(field in source, f"{config_name} source is missing {field}", failures)

            source_url = source.get("url", "")
            require(urlparse(source_url).scheme in ("http", "https"),
                    f"{config_name}/{source.get('name', '<unnamed>')} url must be HTTP(S): {source_url}",
                    failures)

            for field in ["homeurl", "issues"]:
                value = source.get(field, "")
                if not value or "@" in value and "://" not in value:
                    continue
                require(urlparse(value).scheme in ("http", "https", "mailto"),
                        f"{config_name}/{source.get('name', '<unnamed>')} {field} has unsupported scheme: {value}",
                        failures)

    require(source_refs >= 270, "readmeData.json must keep source provenance records", failures)


def main():
    failures = []
    required_files = [
        ".gitignore",
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "hosts",
        "readmeData.json",
        "updateFile.py",
        "docs/readme-overview.svg",
        "docs/plans/2026-06-08-hosts-baseline.md",
    ]

    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    parse_xml("docs/readme-overview.svg", failures)
    check_python_compile(failures)
    check_hosts_file(failures)
    check_readme_data(failures)

    updater = read("updateFile.py")
    require("urlparse(url)" in updater and 'parsed_url.scheme not in ("http", "https")' in updater,
            "updateFile.py must reject unsupported source URL schemes",
            failures)
    require("urlopen(url, timeout=30)" in updater,
            "updateFile.py must fetch source URLs with a timeout",
            failures)
    require("shell=True" not in updater,
            "updateFile.py must not use shell=True for privileged commands",
            failures)

    readme = read("README.md")
    vision = read("VISION.md")
    security = read("SECURITY.md")
    changes = read("CHANGES.md")
    gitignore = read(".gitignore")
    plan = PLAN.read_text(encoding="utf-8") if PLAN.exists() else ""
    require("make check" in readme and "readmeData.json" in readme and "updateFile.py" in readme,
            "README must document static verification, source metadata, and updater usage",
            failures)
    require("scripts/check-baseline.py" in vision and "provenance" in vision.lower(),
            "VISION must describe baseline validation and provenance guardrails",
            failures)
    require("false positive" in security.lower() and "source metadata" in security.lower(),
            "SECURITY must document false-positive and source metadata review expectations",
            failures)
    require("timeout" in changes.lower() and "generated hosts" in changes.lower(),
            "CHANGES must record updater timeout and generated hosts baseline updates",
            failures)
    require("__pycache__/" in gitignore and "*.py[cod]" in gitignore and ".env" in gitignore,
            ".gitignore must exclude Python caches and local environment files",
            failures)
    require("status: completed" in plan,
            "plan must be marked completed",
            failures)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("hosts generated-data baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
