"""DPAPI Windows : blobs liés à l'utilisateur Windows courant. Aucun repli en clair."""
import ctypes
import os
from pathlib import Path


def _dpapi(data, decrypt=False):
    if os.name != "nt":
        raise RuntimeError("La protection persistante des secrets nécessite Windows (DPAPI).")
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    buf = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)))
    target = Blob()
    crypt = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    protect = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    protect.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                       ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    protect.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if not protect(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(target.pbData, target.cbData)
    finally:
        kernel.LocalFree(target.pbData)


def protect(data):
    return _dpapi(data)


def unprotect(data):
    return _dpapi(data, True)


def save_secret(path, data):
    path = Path(path)
    encrypted = protect(data)  # fail before creating any file
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_bytes(encrypted)
    temp.replace(path)
