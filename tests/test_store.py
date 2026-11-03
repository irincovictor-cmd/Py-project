"""Run with: python -m unittest discover -s tests -v"""
import json
import tempfile
import unittest
from pathlib import Path

from store import ReportError, ReportStore


class ReportStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "reports.json"
        self.store = ReportStore(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_add_and_summary(self):
        first = self.store.add("pc-01", "Keyboard broken")
        second = self.store.add("PC-02", "No display")
        self.assertEqual((first, second), ("R001", "R002"))
        self.assertEqual(self.store.reports[first]["computer"], "PC-01")
        self.assertEqual(self.store.summary(), (2, 2, 0))

    def test_empty_fields_rejected(self):
        for computer, issue in (("", "Broken keyboard"), ("PC-01", " ")):
            with self.subTest(computer=computer, issue=issue):
                with self.assertRaises(ReportError):
                    self.store.add(computer, issue)
        self.assertEqual(self.store.summary(), (0, 0, 0))

    def test_computer_format_rejected(self):
        for computer in ("Station A", "PC-", "PC-AB"):
            with self.subTest(computer=computer):
                with self.assertRaises(ReportError):
                    self.store.add(computer, "No display")

    def test_update_and_filter(self):
        key = self.store.add("PC-01", "Mouse issue")
        self.store.update_status(key, "Resolved")
        self.assertEqual(self.store.summary(), (1, 0, 1))
        self.assertEqual(len(self.store.search(status="Resolved")), 1)
        self.assertEqual(len(self.store.search(status="Pending")), 0)

    def test_search(self):
        self.store.add("PC-04", "Keyboard not working")
        self.assertEqual(len(self.store.search("pc-04")), 1)
        self.assertEqual(len(self.store.search("keyboard")), 1)
        self.assertEqual(self.store.search("R999"), [])

    def test_delete(self):
        key = self.store.add("PC-01", "Broken monitor")
        self.store.delete(key)
        self.assertEqual(self.store.summary(), (0, 0, 0))
        with self.assertRaises(ReportError):
            self.store.delete(key)

    def test_json_persistence_and_next_id(self):
        self.store.add("PC-01", "No audio")
        loaded = ReportStore(self.path)
        self.assertEqual(loaded.summary(), (1, 1, 0))
        self.assertEqual(loaded.add("PC-02", "Mouse broken"), "R002")
        self.assertEqual(len(json.loads(self.path.read_text(encoding="utf-8"))), 2)

    def test_corrupt_json_rejected(self):
        self.path.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(ReportError):
            ReportStore(self.path)

    def test_invalid_status_rejected(self):
        key = self.store.add("PC-01", "No display")
        with self.assertRaises(ReportError):
            self.store.update_status(key, "Unknown")
        self.assertEqual(self.store.reports[key]["status"], "Pending")


if __name__ == "__main__":
    unittest.main()
