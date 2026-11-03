import tempfile
import unittest
from pathlib import Path

from auth import AccountError, AccountStore


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "users.json"
        self.accounts = AccountStore(self.path)

    def tearDown(self):
        self.folder.cleanup()

    def test_first_account_must_be_admin(self):
        with self.assertRaises(AccountError):
            self.accounts.create("staff01", "secretpass123", "staff")
        self.accounts.create("admin01", "secretpass123", "admin")
        self.assertEqual(self.accounts.authenticate("admin01", "secretpass123"), "admin")

    def test_staff_created_by_admin_only(self):
        self.accounts.create("admin01", "secretpass123", "admin")
        with self.assertRaises(AccountError):
            self.accounts.create("staff01", "secretpass123", "staff")
        self.accounts.create("staff01", "secretpass123", "staff", actor_role="admin")
        self.assertEqual(self.accounts.authenticate("staff01", "secretpass123"), "staff")
        self.assertIsNone(self.accounts.authenticate("staff01", "incorrect"))

    def test_duplicate_username_and_short_password(self):
        self.accounts.create("admin01", "secretpass123", "admin")
        with self.assertRaises(AccountError):
            self.accounts.create("admin01", "otherpass123", "staff", actor_role="admin")
        with self.assertRaises(AccountError):
            self.accounts.create("newstaff", "short", "staff", actor_role="admin")

    def test_accounts_load_from_json(self):
        self.accounts.create("admin01", "secretpass123", "admin")
        reopened = AccountStore(self.path)
        self.assertEqual(reopened.authenticate("admin01", "secretpass123"), "admin")


if __name__ == "__main__":
    unittest.main()
