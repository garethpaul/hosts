#!/usr/bin/env python3
from pathlib import Path
import ast
import contextlib
import io
import json
import re
import sys
import warnings
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/plans/2026-06-08-hosts-baseline.md"
FETCH_PLAN = ROOT / "docs/plans/2026-06-09-source-fetch-response-cleanup.md"
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


def check_exclusion_regex_escaping(failures):
    namespace = {
        "__file__": str(ROOT / "updateFile.py"),
        "__name__": "hosts_updatefile_baseline",
    }
    source = read("updateFile.py")
    try:
        exec(compile(source, str(ROOT / "updateFile.py"), "exec"), namespace)
    except Exception as error:
        failures.append(f"updateFile.py helpers must load without side effects: {error}")
        return

    regexes = namespace["exclude_domain"]("example.com", r"([a-zA-Z\d-]+\.){0,}", [])
    require(regexes[0].search("example.com"),
            "exclude_domain must still match the requested domain",
            failures)
    require(not regexes[0].search("examplexcom"),
            "exclude_domain must escape user-provided dots to avoid overbroad exclusions",
            failures)


def check_exclusion_domain_validation(failures):
    namespace = {
        "__file__": str(ROOT / "updateFile.py"),
        "__name__": "hosts_updatefile_baseline",
    }
    source = read("updateFile.py")
    try:
        exec(compile(source, str(ROOT / "updateFile.py"), "exec"), namespace)
    except Exception as error:
        failures.append(f"updateFile.py helpers must load without side effects: {error}")
        return

    def is_valid(domain):
        with contextlib.redirect_stdout(io.StringIO()):
            return namespace["is_valid_domain_format"](domain)

    for domain in ["example.com", "ads.example.co.uk"]:
        require(is_valid(domain), f"custom exclusion should accept {domain}", failures)

    for domain in ["", "www.example.com", "http://example.com", "example.com/path", "example com", "*.example.com", "example..com", "-example.com", "example-.com"]:
        require(not is_valid(domain), f"custom exclusion should reject {domain or '<empty>'}", failures)


def check_source_fetch_closes_response(failures):
    namespace = {
        "__file__": str(ROOT / "updateFile.py"),
        "__name__": "hosts_updatefile_baseline",
    }
    source = read("updateFile.py")
    try:
        exec(compile(source, str(ROOT / "updateFile.py"), "exec"), namespace)
    except Exception as error:
        failures.append(f"updateFile.py helpers must load without side effects: {error}")
        return

    class FakeResponse:
        def __init__(self):
            self.closed = False

        def read(self):
            return b"0.0.0.0 example.test\n"

        def close(self):
            self.closed = True

    response = FakeResponse()

    def fake_urlopen(url, timeout):
        require(url == "https://example.test/hosts", "get_file_by_url must fetch the requested URL", failures)
        require(timeout == 30, "get_file_by_url must keep the 30-second timeout", failures)
        return response

    namespace["urlopen"] = fake_urlopen
    result = namespace["get_file_by_url"]("https://example.test/hosts")
    require(result == "0.0.0.0 example.test\n",
            "get_file_by_url must decode fetched host data",
            failures)
    require(response.closed,
            "get_file_by_url must close response objects after reading",
            failures)


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
        "docs/plans/2026-06-08-exclusion-regex-guard.md",
        "docs/plans/2026-06-08-exclusion-domain-validation.md",
        "docs/plans/2026-06-09-source-fetch-response-cleanup.md",
    ]

    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    parse_xml("docs/readme-overview.svg", failures)
    check_python_compile(failures)
    check_exclusion_regex_escaping(failures)
    check_exclusion_domain_validation(failures)
    check_source_fetch_closes_response(failures)
    check_hosts_file(failures)
    check_readme_data(failures)

    updater = read("updateFile.py")
    require("urlparse(url)" in updater and 'parsed_url.scheme not in ("http", "https")' in updater,
            "updateFile.py must reject unsupported source URL schemes",
            failures)
    require("urlopen(url, timeout=30)" in updater,
            "updateFile.py must fetch source URLs with a timeout",
            failures)
    require("re.escape(domain)" in updater,
            "updateFile.py must escape custom exclusion domains before compiling regexes",
            failures)
    require("domain_format_regex" in updater and "example.com" in updater,
            "updateFile.py must validate custom exclusions as plain domains",
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
    exclusion_plan = read("docs/plans/2026-06-08-exclusion-regex-guard.md")
    exclusion_validation_plan = read("docs/plans/2026-06-08-exclusion-domain-validation.md")
    fetch_plan = FETCH_PLAN.read_text(encoding="utf-8") if FETCH_PLAN.exists() else ""
    require("make check" in readme and "readmeData.json" in readme and "updateFile.py" in readme and "exclusion" in readme.lower() and "plain domains" in readme.lower() and "response cleanup" in readme.lower(),
            "README must document static verification, source metadata, and updater usage",
            failures)
    require("scripts/check-baseline.py" in vision and "provenance" in vision.lower() and "plain domains" in vision.lower() and "response cleanup" in vision.lower(),
            "VISION must describe baseline validation and provenance guardrails",
            failures)
    require("false positive" in security.lower() and "source metadata" in security.lower() and "response cleanup" in security.lower(),
            "SECURITY must document false-positive and source metadata review expectations",
            failures)
    require("timeout" in changes.lower() and "generated hosts" in changes.lower() and "exclusion" in changes.lower() and "plain domains" in changes.lower() and "response" in changes.lower(),
            "CHANGES must record updater timeout and generated hosts baseline updates",
            failures)
    require("__pycache__/" in gitignore and "*.py[cod]" in gitignore and ".env" in gitignore,
            ".gitignore must exclude Python caches and local environment files",
            failures)
    require("status: completed" in plan,
            "plan must be marked completed",
            failures)
    require("status: completed" in exclusion_plan,
            "exclusion regex plan must be marked completed",
            failures)
    require("status: completed" in exclusion_validation_plan,
            "exclusion domain validation plan must be marked completed",
            failures)
    require("status: completed" in fetch_plan,
            "source fetch response cleanup plan must be marked completed",
            failures)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("hosts generated-data baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
