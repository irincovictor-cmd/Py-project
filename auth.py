"""Local user accounts for a single-computer classroom prototype."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
from pathlib import Path


class AccountError(ValueError):
    pass


class AccountStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.users = {}
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("Invalid user file.")
                for username, account in data.items():
                    if not isinstance(account, dict) or account.get("role") not in ("admin", "staff"):
                        raise ValueError("Invalid user entry.")
                    if not isinstance(account.get("salt"), str) or not isinstance(account.get("hash"), str):
                        raise ValueError("Invalid password entry.")
                self.users = data
            except (OSError, ValueError, UnicodeError) as exc:
                raise AccountError(f"Cannot open users.json: {exc}") from exc

    @staticmethod
    def validate(username: str, password: str) -> str:
        username = username.strip().lower()
        if not (3 <= len(username) <= 30) or not all(c.isascii() and (c.isalnum() or c == "_") for c in username):
            raise AccountError("Username must contain 3-30 letters, numbers or underscores.")
        if len(password) < 8:
            raise AccountError("Password must have at least 8 characters.")
        return username

    @staticmethod
    def digest(password: str, salt: bytes) -> str:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 300_000).hex()

    def _save(self, updated: dict) -> None:
        temp = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".users-", suffix=".tmp", delete=False) as f:
                temp = Path(f.name)
                json.dump(updated, f, indent=2)
                f.write("\n")
            os.replace(temp, self.path)
        except OSError as exc:
            raise AccountError(f"Unable to save accounts: {exc}") from exc
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)
        self.users = updated

    def create(self, username: str, password: str, role: str, *, actor_role: str | None = None) -> None:
        username = self.validate(username, password)
        if role not in ("admin", "staff"):
            raise AccountError("Invalid role.")
        if not self.users:
            if role != "admin" or actor_role is not None:
                raise AccountError("The first account must be an administrator.")
        elif actor_role != "admin":
            raise AccountError("Only an administrator can create accounts.")
        if username in self.users:
            raise AccountError("Username already exists.")
        salt = os.urandom(16)
        record = {"role": role, "salt": salt.hex(), "hash": self.digest(password, salt)}
        updated = dict(self.users)
        updated[username] = record
        self._save(updated)

    def authenticate(self, username: str, password: str) -> str | None:
        account = self.users.get(username.strip().lower())
        if not account:
            return None
        try:
            calculated = self.digest(password, bytes.fromhex(account["salt"]))
            return account["role"] if hmac.compare_digest(calculated, account["hash"]) else None
        except (ValueError, TypeError):
            return None
