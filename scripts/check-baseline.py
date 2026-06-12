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
SOURCE_URL_HTTPS_PLAN = ROOT / "docs/plans/2026-06-10-source-url-https.md"
SOURCE_OUTPUT_PLAN = ROOT / "docs/plans/2026-06-09-source-output-file-handle-cleanup.md"
EXCLUSION_CASE_PLAN = ROOT / "docs/plans/2026-06-09-exclusion-domain-case-normalization.md"
OUTPUT_PATH_PLAN = ROOT / "docs/plans/2026-06-09-output-subfolder-validation.md"
CI_PLAN = ROOT / "docs/plans/2026-06-10-ci-baseline.md"
SOURCE_HOSTNAME_PLAN = ROOT / "docs/plans/2026-06-10-source-hostname-validation.md"
NETWORK_BOUNDARY_PLAN = ROOT / "docs/plans/2026-06-12-source-network-boundary.md"
CI_POLICY_PLAN = ROOT / "docs/plans/2026-06-12-ci-policy-hardening.md"
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


def check_output_subfolder_validation(failures):
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

    validator = namespace["is_safe_output_subfolder"]
    for output_path in ["", ".", "generated", "generated/mobile"]:
        require(validator(output_path), f"--output should accept safe subfolder {output_path or '<root>'}", failures)

    for output_path in ["../outside", "generated/../outside", "/tmp/hosts", r"C:\hosts", r"\windows\hosts", r"\\server\share"]:
        require(not validator(output_path), f"--output should reject unsafe subfolder {output_path}", failures)


def check_source_hostname_validation(failures):
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

    normalize = namespace["normalize_rule"]
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        hostname, rule = normalize("0.0.0.0 WWW.Example.COM", "0.0.0.0", False)
        require(hostname == "www.example.com" and rule == "0.0.0.0 www.example.com\n",
                "normalize_rule must preserve valid source hostnames in lowercase",
                failures)

        for invalid_hostname in [
                "bad_domain.com", "example..com", "-example.com", "example-.com",
                "a" * 64 + ".com", ("a" * 63 + ".") * 4 + "com"]:
            hostname, rule = normalize(
                "0.0.0.0 " + invalid_hostname, "0.0.0.0", False)
            require(hostname is None and rule is None,
                    f"normalize_rule must reject malformed source hostname {invalid_hostname}",
                    failures)


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

        def read(self, size=-1):
            require(size == namespace["MAX_SOURCE_DOWNLOAD_BYTES"] + 1,
                    "get_file_by_url must bound source response reads", failures)
            return b"0.0.0.0 example.test\n"

        def geturl(self):
            return "https://example.test/hosts"

        def close(self):
            self.closed = True

    response = FakeResponse()

    def fake_open_source_url(url, timeout):
        require(url == "https://example.test/hosts", "get_file_by_url must fetch the requested URL", failures)
        require(timeout == namespace["SOURCE_DOWNLOAD_TIMEOUT_SECONDS"],
                "get_file_by_url must keep the bounded timeout", failures)
        return response

    namespace["open_source_url"] = fake_open_source_url
    result = namespace["get_file_by_url"]("https://example.test/hosts")
    require(result == "0.0.0.0 example.test\n",
            "get_file_by_url must decode fetched host data",
            failures)
    require(response.closed,
            "get_file_by_url must close response objects after reading",
            failures)


def check_source_fetch_requires_https_host(failures):
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

    def fake_open_source_url(url, timeout):
        attempted_fetches.append((url, timeout))
        raise AssertionError("malformed source URL should not be fetched")

    namespace["open_source_url"] = fake_open_source_url
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        for invalid_url in [
                "https://", "http://example.test/hosts",
                "https://user:secret@example.test/hosts",
                "https://user@:443/hosts", "https://bad_.example/hosts",
                "https://example.test:bad/hosts", "https://127.0.0.1/hosts",
                "https://example.test/host list"]:
            namespace["get_file_by_url"](invalid_url)
    require(not attempted_fetches,
            "get_file_by_url must reject malformed or untrusted source URLs before fetching",
            failures)
    require("secret" not in output.getvalue(),
            "rejected source URLs must not expose embedded credentials in logs",
            failures)


def check_source_redirect_and_size_boundaries(failures):
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

    handler = namespace["HTTPSOnlyRedirectHandler"]()
    for invalid_redirect in [
            "http://example.test/hosts", "https://user@example.test/hosts",
            "https://127.0.0.1/hosts"]:
        try:
            handler.redirect_request(None, None, 302, "Found", {}, invalid_redirect)
        except ValueError:
            pass
        else:
            failures.append(f"source redirect must reject {invalid_redirect}")

    class OversizedResponse:
        def __init__(self):
            self.closed = False

        def geturl(self):
            return "https://example.test/hosts"

        def read(self, size=-1):
            return b"x" * size

        def close(self):
            self.closed = True

    response = OversizedResponse()
    namespace["MAX_SOURCE_DOWNLOAD_BYTES"] = 4
    namespace["open_source_url"] = lambda url, timeout: response
    with contextlib.redirect_stdout(io.StringIO()):
        result = namespace["get_file_by_url"]("https://example.test/hosts")
    require(result is None, "oversized source responses must fail closed", failures)
    require(response.closed, "oversized source responses must still close", failures)


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

    namespace = {
        "__file__": str(ROOT / "updateFile.py"),
        "__name__": "hosts_updatefile_baseline",
    }
    try:
        exec(compile(read("updateFile.py"), str(ROOT / "updateFile.py"), "exec"), namespace)
        source_url_is_valid = namespace["is_valid_source_url"]
    except Exception as error:
        failures.append(f"updateFile.py source URL validator must load: {error}")
        return

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
            require(source_url_is_valid(source_url),
                    f"{config_name}/{source.get('name', '<unnamed>')} url must be credential-free HTTPS with a valid DNS host: {source_url}",
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
        ".github/CODEOWNERS",
        ".gitignore",
        ".github/workflows/check.yml",
        "AGENTS.md",
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
        "docs/plans/2026-06-10-source-url-https.md",
        "docs/plans/2026-06-09-source-output-file-handle-cleanup.md",
        "docs/plans/2026-06-09-exclusion-domain-case-normalization.md",
        "docs/plans/2026-06-09-output-subfolder-validation.md",
        "docs/plans/2026-06-10-ci-baseline.md",
        "docs/plans/2026-06-10-source-hostname-validation.md",
        "docs/plans/2026-06-12-source-network-boundary.md",
        "docs/plans/2026-06-12-ci-policy-hardening.md",
    ]

    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    parse_xml("docs/readme-overview.svg", failures)
    check_python_compile(failures)
    check_exclusion_regex_escaping(failures)
    check_exclusion_domain_validation(failures)
    check_output_subfolder_validation(failures)
    check_source_hostname_validation(failures)
    check_source_fetch_closes_response(failures)
    check_source_fetch_requires_https_host(failures)
    check_source_redirect_and_size_boundaries(failures)
    check_source_data_files_close_on_parse_failure(failures)
    check_source_output_files_close_on_write_failure(failures)
    check_hosts_file(failures)
    check_readme_data(failures)

    updater = read("updateFile.py")
    require("def is_valid_source_url" in updater and "HTTPSOnlyRedirectHandler" in updater and
            "MAX_SOURCE_DOWNLOAD_BYTES = 32 * 1024 * 1024" in updater and
            "SOURCE_DOWNLOAD_TIMEOUT_SECONDS = 30" in updater,
            "updateFile.py must enforce strict HTTPS source and response boundaries",
            failures)
    require("open_source_url(url, timeout=SOURCE_DOWNLOAD_TIMEOUT_SECONDS)" in updater,
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
    require("is_safe_output_subfolder" in updater and "parser.error(\"--output must be a relative subfolder without parent traversal\")" in updater,
            "updateFile.py must reject unsafe output subfolders before writing generated hosts files",
            failures)
    require("is_valid_source_hostname(hostname)" in updater and "hostname_format_regex" in updater,
            "updateFile.py must reject malformed upstream hostnames before output",
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
    source_url_https_plan = SOURCE_URL_HTTPS_PLAN.read_text(encoding="utf-8") if SOURCE_URL_HTTPS_PLAN.exists() else ""
    source_output_plan = SOURCE_OUTPUT_PLAN.read_text(encoding="utf-8") if SOURCE_OUTPUT_PLAN.exists() else ""
    exclusion_case_plan = EXCLUSION_CASE_PLAN.read_text(encoding="utf-8") if EXCLUSION_CASE_PLAN.exists() else ""
    output_path_plan = OUTPUT_PATH_PLAN.read_text(encoding="utf-8") if OUTPUT_PATH_PLAN.exists() else ""
    ci_plan = CI_PLAN.read_text(encoding="utf-8") if CI_PLAN.exists() else ""
    workflow = read(".github/workflows/check.yml")
    source_hostname_plan = SOURCE_HOSTNAME_PLAN.read_text(encoding="utf-8") if SOURCE_HOSTNAME_PLAN.exists() else ""
    network_boundary_plan = NETWORK_BOUNDARY_PLAN.read_text(encoding="utf-8") if NETWORK_BOUNDARY_PLAN.exists() else ""
    ci_policy_plan = CI_POLICY_PLAN.read_text(encoding="utf-8") if CI_POLICY_PLAN.exists() else ""
    require(".PHONY: build check lint test" in makefile and "lint test build: check" in makefile,
            "Makefile must expose lint, test, and build aliases for the local baseline",
            failures)
    expected_workflow = """name: Check

on:
  pull_request:
  push:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        python-version: [\"3.10\", \"3.12\", \"3.14\"]
    steps:
      - name: Check out repository
        uses: actions/checkout@9f698171ed81b15d1823a05fc7211befd50c8ae0 # v6.0.3
        with:
          persist-credentials: false

      - name: Set up Python
        uses: actions/setup-python@83679a892e2d95755f2dac6acb0bfd1e9ac5d548 # v6.1.0
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run baseline
        run: make check
"""
    workflow_files = sorted((ROOT / ".github/workflows").glob("*"))
    require(workflow_files == [ROOT / ".github/workflows/check.yml"],
            "check.yml must remain the only hosted workflow", failures)
    require(workflow == expected_workflow,
            "GitHub Actions must match the canonical credential-free Python matrix", failures)
    require(read(".github/CODEOWNERS") == "* @garethpaul\n",
            "CODEOWNERS must assign repository-wide ownership", failures)
    require("make lint" in readme and "make test" in readme and "make build" in readme and "make check" in readme and "readmeData.json" in readme and "updateFile.py" in readme and "exclusion" in readme.lower() and "plain domains" in readme.lower() and "lowercase" in readme.lower() and "response cleanup" in readme.lower() and "source metadata file handles" in readme.lower() and "source output file handles" in readme.lower() and "source urls require https schemes and hosts" in readme.lower() and "GitHub Actions" in readme and "output subfolders" in readme.lower(),
            "README must document static verification, source metadata, and updater usage",
            failures)
    require("scripts/check-baseline.py" in vision and "make lint" in vision and "make test" in vision and "make build" in vision and "provenance" in vision.lower() and "plain domains" in vision.lower() and "lowercase" in vision.lower() and "response cleanup" in vision.lower() and "source metadata file handles" in vision.lower() and "source output file handles" in vision.lower() and "source urls use https" in vision.lower() and "include hosts" in vision.lower() and "GitHub Actions" in vision and "output subfolders" in vision.lower(),
            "VISION must describe baseline validation and provenance guardrails",
            failures)
    require("false positive" in security.lower() and "source metadata" in security.lower() and "response cleanup" in security.lower() and "source output file handles" in security.lower() and "source urls must use https" in security.lower() and "output subfolders" in security.lower(),
            "SECURITY must document false-positive and source metadata review expectations",
            failures)
    require("GitHub Actions" in changes and "https source" in changes.lower() and "timeout" in changes.lower() and "generated hosts" in changes.lower() and "exclusion" in changes.lower() and "plain domains" in changes.lower() and "lowercase" in changes.lower() and "response" in changes.lower() and "source metadata file handles" in changes.lower() and "source output file handles" in changes.lower() and "source urls" in changes.lower() and "output subfolders" in changes.lower() and "make lint" in changes and "make test" in changes and "make build" in changes,
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
    require("status: completed" in source_url_https_plan,
            "source URL HTTPS plan must be marked completed",
            failures)
    require("status: completed" in source_output_plan,
            "source output file-handle cleanup plan must be marked completed",
            failures)
    require("status: completed" in exclusion_case_plan,
            "exclusion domain case-normalization plan must be marked completed",
            failures)
    require("status: completed" in output_path_plan,
            "output subfolder validation plan must be marked completed",
            failures)
    require("status: completed" in ci_plan,
            "CI baseline plan must be marked completed",
            failures)
    require("status: completed" in source_hostname_plan and "make check" in source_hostname_plan,
            "source hostname validation plan must be completed and record verification",
            failures)
    require("status: completed" in network_boundary_plan and "hostile network mutations" in network_boundary_plan.lower(),
            "source network boundary plan must record completed mutation verification",
            failures)
    require("status: completed" in ci_policy_plan and "hostile workflow mutations" in ci_policy_plan.lower(),
            "CI policy plan must record completed mutation verification",
            failures)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("hosts generated-data baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
