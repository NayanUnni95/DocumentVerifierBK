import hashlib
import json

from typing import Union
from django.contrib.auth.hashers import make_password, check_password


class Hash:
    @staticmethod
    def encrypt_password(password: str):
        return make_password(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str):
        return check_password(password, hashed_password)


class HashingUtils:
    """
    Utility class for generating deterministic hashes
    for documents or structured data.
    """

    @staticmethod
    def sha256_from_text(text: str) -> str:
        """
        Generate SHA256 hash from plain text.
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def sha256_from_bytes(data: bytes) -> str:
        """
        Generate SHA256 hash from binary data (PDF, image, etc).
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha256_from_json(data: Union[dict, list]) -> str:
        """
        Deterministic hashing for structured OCR data.
        """
        normalized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def sha256_file(file_path: str) -> str:
        """
        Generate SHA256 hash for a file.
        """
        hash_sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)

        return hash_sha256.hexdigest()