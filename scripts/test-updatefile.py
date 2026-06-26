#!/usr/bin/env python3

import importlib.util
import os
from pathlib import Path
import shutil
import stat
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_updater():
    spec = importlib.util.spec_from_file_location(
        "hosts_updatefile_tests", ROOT / "updateFile.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.updater = load_updater()

    def test_backup_path_swap_cannot_overwrite_symlink_target(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            destination = directory / "hosts"
            destination.write_text("recovery data\n", encoding="utf-8")
            victim = directory / "victim"
            victim.write_text("must survive\n", encoding="utf-8")
            original_copy = self.updater.shutil.copy

            def swap_then_copy(source, backup_path):
                os.remove(backup_path)
                os.symlink(str(victim), backup_path)
                return original_copy(source, backup_path)

            self.updater.shutil.copy = swap_then_copy
            try:
                backup_path = self.updater.create_hosts_backup(str(destination))
            finally:
                self.updater.shutil.copy = original_copy

            self.assertEqual(victim.read_text(encoding="utf-8"), "must survive\n")
            self.assertFalse(Path(backup_path).is_symlink())
            self.assertEqual(
                Path(backup_path).read_text(encoding="utf-8"),
                "recovery data\n")

    def test_output_directory_symlink_swap_is_rejected_at_staging(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            repository = root / "repository"
            outside = root / "outside"
            repository.mkdir()
            outside.mkdir()
            output = repository / "generated"
            output.mkdir()

            self.updater.BASEDIR_PATH = str(repository)
            self.assertTrue(self.updater.is_safe_output_subfolder("generated"))
            output.rmdir()
            output.symlink_to(outside, target_is_directory=True)

            with self.assertRaises(ValueError):
                self.updater.create_staged_hosts_file(str(output))
            self.assertEqual(list(outside.iterdir()), [])

    def test_publication_rejects_symlink_destination(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            self.updater.BASEDIR_PATH = str(directory)
            victim = directory / "victim"
            victim.write_text("must survive\n", encoding="utf-8")
            destination = directory / "hosts"
            destination.symlink_to(victim)
            staged = self.updater.create_staged_hosts_file(str(directory))
            staged.write(b"replacement\n")

            with self.assertRaises(ValueError):
                self.updater.publish_hosts_file(staged, str(destination), True)

            self.assertTrue(destination.is_symlink())
            self.assertEqual(victim.read_text(encoding="utf-8"), "must survive\n")
            self.assertFalse(Path(staged.name).exists())

    def test_publication_preserves_destination_owner(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            self.updater.BASEDIR_PATH = str(directory)
            destination = directory / "hosts"
            destination.write_text("old\n", encoding="utf-8")
            destination_stat = destination.stat()
            staged = self.updater.create_staged_hosts_file(str(directory))
            staged.write(b"new\n")
            ownership_calls = []
            original_fchown = self.updater.os.fchown

            def record_fchown(file_descriptor, uid, gid):
                ownership_calls.append((uid, gid))
                return original_fchown(file_descriptor, uid, gid)

            self.updater.os.fchown = record_fchown
            try:
                self.updater.publish_hosts_file(
                    staged, str(destination), False)
            finally:
                self.updater.os.fchown = original_fchown

            self.assertIn(
                (destination_stat.st_uid, destination_stat.st_gid),
                ownership_calls)

    def test_atomic_writers_sync_file_and_parent_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            destinations = [
                (directory / "readmeData.json",
                 lambda path: self.updater.write_json_file_atomically(
                     str(path), {"base": {"entries": 1}})),
                (directory / "source-hosts",
                 lambda path: self.updater.write_source_file_atomically(
                     str(path), "0.0.0.0 example.test\n")),
            ]

            for destination, writer in destinations:
                fsync_types = []
                original_fsync = self.updater.os.fsync

                def record_fsync(file_descriptor):
                    mode = os.fstat(file_descriptor).st_mode
                    fsync_types.append(
                        "directory" if stat.S_ISDIR(mode) else "file")
                    return original_fsync(file_descriptor)

                self.updater.os.fsync = record_fsync
                try:
                    writer(destination)
                finally:
                    self.updater.os.fsync = original_fsync

                self.assertEqual(fsync_types, ["file", "directory"])


class ParsingBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.updater = load_updater()

    def test_multiple_aliases_are_canonicalized_and_filtered_independently(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            self.updater.settings = {
                "numberofrules": 0,
                "whitelistfile": str(directory / "missing-whitelist"),
                "exclusions": ["blocked.example"],
                "targetip": "0.0.0.0",
                "keepdomaincomments": False,
            }
            merge_file = tempfile.NamedTemporaryFile(mode="w+b")
            merge_file.write(
                b"127.0.0.1 First.Example blocked.example second.example # source\n")
            final_file = tempfile.NamedTemporaryFile(mode="w+b")

            self.updater.remove_dups_and_excl(merge_file, [], final_file)
            final_file.seek(0)
            output = final_file.read().decode("utf-8")
            final_file.close()

            self.assertEqual(
                output,
                "0.0.0.0 first.example\n0.0.0.0 second.example\n")
            self.assertEqual(self.updater.settings["numberofrules"], 2)

    def test_ipv6_loopback_in_comment_does_not_drop_ipv4_rule(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            self.updater.settings = {
                "numberofrules": 0,
                "whitelistfile": str(directory / "missing-whitelist"),
                "exclusions": [],
                "targetip": "0.0.0.0",
                "keepdomaincomments": True,
            }
            merge_file = tempfile.NamedTemporaryFile(mode="w+b")
            merge_file.write(
                b"0.0.0.0 ads.example # IPv6 mirror uses ::1\n")
            final_file = tempfile.NamedTemporaryFile(mode="w+b")

            self.updater.remove_dups_and_excl(merge_file, [], final_file)
            final_file.seek(0)
            output = final_file.read().decode("utf-8")
            final_file.close()

            self.assertEqual(
                output,
                "0.0.0.0 ads.example # IPv6 mirror uses ::1\n")
            self.assertEqual(self.updater.settings["numberofrules"], 1)


if __name__ == "__main__":
    unittest.main()
