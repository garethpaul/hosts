import io
import socket
import sys
import unittest

import updateFile


class FakeResponse(object):
    def read(self):
        return b"payload"


class GetFileByUrlTest(unittest.TestCase):
    def setUp(self):
        self.original_urlopen = updateFile.urlopen
        self.original_stdout = sys.stdout

    def tearDown(self):
        updateFile.urlopen = self.original_urlopen
        sys.stdout = self.original_stdout

    def test_get_file_by_url_passes_timeout(self):
        calls = []

        def fake_urlopen(url, timeout=None):
            calls.append((url, timeout))
            return FakeResponse()

        updateFile.urlopen = fake_urlopen

        result = updateFile.get_file_by_url("https://example.test/hosts")

        self.assertEqual(result, "payload")
        self.assertEqual(
            calls,
            [("https://example.test/hosts", updateFile.URL_TIMEOUT_SECONDS)],
        )

    def test_get_file_by_url_handles_socket_timeout(self):
        def fake_urlopen(_url, timeout=None):
            raise socket.timeout("stalled")

        updateFile.urlopen = fake_urlopen
        sys.stdout = io.StringIO()

        result = updateFile.get_file_by_url("https://example.test/hosts")

        self.assertIsNone(result)
        self.assertIn("Timed out getting file", sys.stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
