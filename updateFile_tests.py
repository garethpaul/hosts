import unittest

import updateFile


class FakeResponse(object):
    def read(self):
        return b"payload"


class GetFileByUrlTest(unittest.TestCase):
    def setUp(self):
        self.original_urlopen = updateFile.urlopen

    def tearDown(self):
        updateFile.urlopen = self.original_urlopen

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


if __name__ == "__main__":
    unittest.main()
