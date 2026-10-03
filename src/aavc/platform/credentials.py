from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from typing import Any, Protocol


class CredentialStore(Protocol):
    def set_secret(self, reference: str, secret: str) -> None:
        """Store a secret by opaque reference."""

    def get_secret(self, reference: str) -> str:
        """Resolve a secret by opaque reference."""

    def delete_secret(self, reference: str) -> None:
        """Delete a stored secret."""


class MemoryCredentialStore:
    """Deterministic test store. Never persist this in production."""

    def __init__(self) -> None:
        self._values: dict[str, str] = {}

    def set_secret(self, reference: str, secret: str) -> None:
        _validate_reference(reference)
        if not secret:
            raise ValueError("secret must not be empty")
        self._values[reference] = secret

    def get_secret(self, reference: str) -> str:
        _validate_reference(reference)
        try:
            return self._values[reference]
        except KeyError:
            raise KeyError(reference) from None

    def delete_secret(self, reference: str) -> None:
        _validate_reference(reference)
        self._values.pop(reference, None)


class WindowsCredentialStore:
    """Windows Credential Manager store for generic AAVC secrets."""

    _CRED_TYPE_GENERIC = 1
    _CRED_PERSIST_LOCAL_MACHINE = 2
    _ERROR_NOT_FOUND = 1168

    def __init__(self, *, namespace: str = "AI-Automatic-Video-Composer") -> None:
        clean = namespace.strip().strip("/")
        if not clean:
            raise ValueError("namespace must not be empty")
        self._namespace = clean

    def set_secret(self, reference: str, secret: str) -> None:
        _validate_reference(reference)
        if not secret:
            raise ValueError("secret must not be empty")
        api, credential_type = self._load_api()
        blob = secret.encode("utf-8")
        buffer = (ctypes.c_ubyte * len(blob)).from_buffer_copy(blob)
        credential = credential_type()
        credential.Flags = 0
        credential.Type = self._CRED_TYPE_GENERIC
        credential.TargetName = self._target(reference)
        credential.Comment = "AAVC provider credential"
        credential.CredentialBlobSize = len(blob)
        credential.CredentialBlob = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))
        credential.Persist = self._CRED_PERSIST_LOCAL_MACHINE
        credential.AttributeCount = 0
        credential.Attributes = None
        credential.TargetAlias = None
        credential.UserName = reference
        if not api.CredWriteW(ctypes.byref(credential), 0):
            raise OSError(ctypes.get_last_error(), "CredWriteW failed")

    def get_secret(self, reference: str) -> str:
        _validate_reference(reference)
        api, credential_type = self._load_api()
        pointer = ctypes.POINTER(credential_type)()
        if not api.CredReadW(
            self._target(reference),
            self._CRED_TYPE_GENERIC,
            0,
            ctypes.byref(pointer),
        ):
            error = ctypes.get_last_error()
            if error == self._ERROR_NOT_FOUND:
                raise KeyError(reference)
            raise OSError(error, "CredReadW failed")
        try:
            credential = pointer.contents
            raw = ctypes.string_at(
                credential.CredentialBlob,
                credential.CredentialBlobSize,
            )
            return raw.decode("utf-8")
        finally:
            api.CredFree(pointer)

    def delete_secret(self, reference: str) -> None:
        _validate_reference(reference)
        api, _ = self._load_api()
        if not api.CredDeleteW(self._target(reference), self._CRED_TYPE_GENERIC, 0):
            error = ctypes.get_last_error()
            if error != self._ERROR_NOT_FOUND:
                raise OSError(error, "CredDeleteW failed")

    def _target(self, reference: str) -> str:
        return f"{self._namespace}/{reference}"

    @staticmethod
    def _load_api() -> tuple[Any, Any]:
        if os.name != "nt":
            raise OSError("Windows Credential Manager is only available on Windows")

        class Credential(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", ctypes.c_void_p),
                ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]

        api = ctypes.WinDLL("Advapi32.dll", use_last_error=True)
        api.CredWriteW.argtypes = [ctypes.POINTER(Credential), wintypes.DWORD]
        api.CredWriteW.restype = wintypes.BOOL
        api.CredReadW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.POINTER(ctypes.POINTER(Credential)),
        ]
        api.CredReadW.restype = wintypes.BOOL
        api.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
        api.CredDeleteW.restype = wintypes.BOOL
        api.CredFree.argtypes = [ctypes.c_void_p]
        api.CredFree.restype = None
        return api, Credential


def _validate_reference(reference: str) -> None:
    if not reference or reference.strip() != reference:
        raise ValueError("credential reference must be a non-empty trimmed string")
    if any(char in reference for char in "\r\n\0"):
        raise ValueError("credential reference contains invalid control characters")
