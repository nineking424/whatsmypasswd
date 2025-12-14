import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import get_settings


class CryptoService:
    def __init__(self):
        settings = get_settings()
        self._fernet = self._create_fernet(settings.encryption_key)

    def _create_fernet(self, key: str) -> Fernet:
        """Create Fernet instance from encryption key."""
        # Derive a proper Fernet key from the provided key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"whatsmypasswd_salt",  # Fixed salt for consistency
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        return Fernet(derived_key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64 encoded ciphertext."""
        if not plaintext:
            return ""
        encrypted = self._fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64 encoded ciphertext and return plaintext."""
        if not ciphertext:
            return ""
        encrypted = base64.urlsafe_b64decode(ciphertext.encode())
        return self._fernet.decrypt(encrypted).decode()

    def encrypt_dict(self, data: dict) -> str:
        """Encrypt a dictionary as JSON string."""
        if not data:
            return ""
        json_str = json.dumps(data, ensure_ascii=False)
        return self.encrypt(json_str)

    def decrypt_dict(self, ciphertext: str) -> dict:
        """Decrypt to a dictionary from encrypted JSON string."""
        if not ciphertext:
            return {}
        json_str = self.decrypt(ciphertext)
        return json.loads(json_str)


# Singleton instance
_crypto_service: CryptoService | None = None


def get_crypto_service() -> CryptoService:
    global _crypto_service
    if _crypto_service is None:
        _crypto_service = CryptoService()
    return _crypto_service
