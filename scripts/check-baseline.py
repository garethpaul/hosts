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
MAKE_GATES_PLAN = ROOT / "docs/plans/2026-06-09-make-gate-aliases.md"
FETCH_PLAN = ROOT / "docs/plans/2026-06-09-source-fetch-response-cleanup.md"
SOURCE_DATA_PLAN = ROOT / "docs/plans/2026-06-09-source-data-file-handle-cleanup.md"
SOURCE_URL_HOST_PLAN = ROOT / "docs/plans/2026-06-09-source-url-host-validation.md"
SOURCE_OUTPUT_PLAN = ROOT / "docs/plans/2026-06-09-source-output-file-handle-cleanup.md"
EXCLUSION_CASE_PLAN = ROOT / "docs/plans/2026-06-09-exclusion-domain-case-normalization.md"
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

    uppercase_regexes = namespace["exclude_domain"](
        "Example.COM", r"([a-zA-Z\d-]+\.){0,}", [])
    require(uppercase_regexes[0].search("example.com"),
            "exclude_domain must normalize custom exclusion domains to lowercase",
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


def check_source_fetch_requires_host(failures):
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

    attempted_fetches = []

    def fake_urlopen(url, timeout):
        attempted_fetches.append((url, timeout))
        raise AssertionError("malformed source URL should not be fetched")

    namespace["urlopen"] = fake_urlopen
    with contextlib.redirect_stdout(io.StringIO()):
        namespace["get_file_by_url"]("https://")
    require(not attempted_fetches,
            "get_file_by_url must reject HTTP(S) source URLs without a host before fetching",
            failures)


def check_source_data_files_close_on_parse_failure(failures):
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

    class FakeSourceDataFile:
        def __init__(self):
            self.closed = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.closed = True
            return False

        def read(self):
            return "{"

    opened_files = []

    def fake_open(path, mode="r"):
        require(path == "source/update.json",
                "update_sources_data must open source metadata paths returned by recursive_glob",
                failures)
        require(mode == "r",
                "update_sources_data must read source metadata in text mode",
                failures)
        source_data_file = FakeSourceDataFile()
        opened_files.append(source_data_file)
        return source_data_file

    namespace["recursive_glob"] = lambda root, filename: ["source/update.json"]
    namespace["open"] = fake_open

    try:
        namespace["update_sources_data"](
            [],
            datapath="data",
            extensions=[],
            extensionspath="extensions",
            sourcedatafilename="update.json")
    except ValueError:
        pass
    else:
        failures.append("update_sources_data fixture must raise on malformed source metadata JSON")

    require(opened_files and opened_files[0].closed,
            "update_sources_data must close source metadata files when JSON parsing fails",
            failures)


def check_source_output_files_close_on_write_failure(failures):
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

    class FakeSourceDataFile:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def read(self):
            return '{"url": "https://example.test/hosts"}'

    class FakeHostsFile:
        def __init__(self):
            self.closed = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.closed = True
            return False

    opened_outputs = []

    def fake_open(path, mode="r"):
        if path == "source/update.json" and mode == "r":
            return FakeSourceDataFile()
        if str(path).endswith("source/hosts") and mode == "wb":
            hosts_file = FakeHostsFile()
            opened_outputs.append(hosts_file)
            return hosts_file
        raise AssertionError("unexpected open call: {0} {1}".format(path, mode))

    def fake_write_data(hosts_file, updated_file):
        raise IOError("simulated write failure")

    namespace["recursive_glob"] = lambda root, filename: ["source/update.json"]
    namespace["open"] = fake_open
    namespace["get_file_by_url"] = lambda url: "0.0.0.0 example.test\n"
    namespace["write_data"] = fake_write_data

    with contextlib.redirect_stdout(io.StringIO()):
        namespace["update_all_sources"]("update.json", "hosts")

    require(opened_outputs and opened_outputs[0].closed,
            "update_all_sources must close generated source hosts files when writes fail",
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
            parsed_source_url = urlparse(source_url)
            require(parsed_source_url.scheme in ("http", "https") and parsed_source_url.netloc,
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
        "docs/plans/2026-06-09-make-gate-aliases.md",
        "docs/plans/2026-06-08-exclusion-regex-guard.md",
        "docs/plans/2026-06-08-exclusion-domain-validation.md",
        "docs/plans/2026-06-09-source-fetch-response-cleanup.md",
        "docs/plans/2026-06-09-source-data-file-handle-cleanup.md",
        "docs/plans/2026-06-09-source-url-host-validation.md",
        "docs/plans/2026-06-09-source-output-file-handle-cleanup.md",
        "docs/plans/2026-06-09-exclusion-domain-case-normalization.md",
    ]

    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    parse_xml("docs/readme-overview.svg", failures)
    check_python_compile(failures)
    check_exclusion_regex_escaping(failures)
    check_exclusion_domain_validation(failures)
    check_source_fetch_closes_response(failures)
    check_source_fetch_requires_host(failures)
    check_source_data_files_close_on_parse_failure(failures)
    check_source_output_files_close_on_write_failure(failures)
    check_hosts_file(failures)
    check_readme_data(failures)

    updater = read("updateFile.py")
    require("urlparse(url)" in updater and 'parsed_url.scheme not in ("http", "https") or not parsed_url.netloc' in updater,
            "updateFile.py must reject unsupported source URL schemes and missing hosts",
            failures)
    require("urlopen(url, timeout=30)" in updater,
            "updateFile.py must fetch source URLs with a timeout",
            failures)
    require('with open(source, "r") as update_file:' in updater and
            'with open(update_file_path, "r") as update_file:' in updater,
            "updateFile.py must close source metadata files after JSON reads",
            failures)
    require('"wb") as hosts_file:' in updater,
            "updateFile.py must close generated source hosts files after writes",
            failures)
    require("re.escape(" in updater,
            "updateFile.py must escape custom exclusion domains before compiling regexes",
            failures)
    require("normalized_domain = domain.lower()" in updater and "re.escape(normalized_domain)" in updater,
            "updateFile.py must normalize custom exclusion domains before compiling regexes",
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
    makefile = read("Makefile")
    plan = PLAN.read_text(encoding="utf-8") if PLAN.exists() else ""
    make_gates_plan = MAKE_GATES_PLAN.read_text(encoding="utf-8") if MAKE_GATES_PLAN.exists() else ""
    exclusion_plan = read("docs/plans/2026-06-08-exclusion-regex-guard.md")
    exclusion_validation_plan = read("docs/plans/2026-06-08-exclusion-domain-validation.md")
    fetch_plan = FETCH_PLAN.read_text(encoding="utf-8") if FETCH_PLAN.exists() else ""
    source_data_plan = SOURCE_DATA_PLAN.read_text(encoding="utf-8") if SOURCE_DATA_PLAN.exists() else ""
    source_url_host_plan = SOURCE_URL_HOST_PLAN.read_text(encoding="utf-8") if SOURCE_URL_HOST_PLAN.exists() else ""
    source_output_plan = SOURCE_OUTPUT_PLAN.read_text(encoding="utf-8") if SOURCE_OUTPUT_PLAN.exists() else ""
    exclusion_case_plan = EXCLUSION_CASE_PLAN.read_text(encoding="utf-8") if EXCLUSION_CASE_PLAN.exists() else ""
    require(".PHONY: build check lint test" in makefile and "lint test build: check" in makefile,
            "Makefile must expose lint, test, and build aliases for the local baseline",
            failures)
    require("make lint" in readme and "make test" in readme and "make build" in readme and "make check" in readme and "readmeData.json" in readme and "updateFile.py" in readme and "exclusion" in readme.lower() and "plain domains" in readme.lower() and "lowercase" in readme.lower() and "response cleanup" in readme.lower() and "source metadata file handles" in readme.lower() and "source output file handles" in readme.lower() and "source urls require http(s) schemes and hosts" in readme.lower(),
            "README must document static verification, source metadata, and updater usage",
            failures)
    require("scripts/check-baseline.py" in vision and "make lint" in vision and "make test" in vision and "make build" in vision and "provenance" in vision.lower() and "plain domains" in vision.lower() and "lowercase" in vision.lower() and "response cleanup" in vision.lower() and "source metadata file handles" in vision.lower() and "source output file handles" in vision.lower() and "source urls include hosts" in vision.lower(),
            "VISION must describe baseline validation and provenance guardrails",
            failures)
    require("false positive" in security.lower() and "source metadata" in security.lower() and "response cleanup" in security.lower() and "source output file handles" in security.lower() and "source urls" in security.lower(),
            "SECURITY must document false-positive and source metadata review expectations",
            failures)
    require("timeout" in changes.lower() and "generated hosts" in changes.lower() and "exclusion" in changes.lower() and "plain domains" in changes.lower() and "lowercase" in changes.lower() and "response" in changes.lower() and "source metadata file handles" in changes.lower() and "source output file handles" in changes.lower() and "source urls" in changes.lower() and "make lint" in changes and "make test" in changes and "make build" in changes,
            "CHANGES must record updater timeout and generated hosts baseline updates",
            failures)
    require("__pycache__/" in gitignore and "*.py[cod]" in gitignore and ".env" in gitignore,
            ".gitignore must exclude Python caches and local environment files",
            failures)
    require("status: completed" in plan,
            "plan must be marked completed",
            failures)
    require("status: completed" in make_gates_plan,
            "make gate aliases plan must be marked completed",
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
    require("status: completed" in source_data_plan,
            "source data file-handle cleanup plan must be marked completed",
            failures)
    require("status: completed" in source_url_host_plan,
            "source URL host validation plan must be marked completed",
            failures)
    require("status: completed" in source_output_plan,
            "source output file-handle cleanup plan must be marked completed",
            failures)
    require("status: completed" in exclusion_case_plan,
            "exclusion domain case-normalization plan must be marked completed",
            failures)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("hosts generated-data baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
