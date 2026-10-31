"""Create or update the Steam Workshop collection through the running Steam client.

Uses a Steamworks 1.5x steam_api64.dll whose versioned accessors (SteamAPI_SteamUGC_v021)
guarantee the flat functions match the interface layout. CK3's own DLL is too old for that.
ISteamUGC: CreateItem with the collection file type, then AddDependency(collection, mod) for
each mod in load order.
"""
from __future__ import annotations

import ctypes
import os
import sys
import time
from ctypes import c_bool, c_char_p, c_int, c_uint32, c_uint64, c_void_p
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DLL = Path(r"F:\SteamLibrary\steamapps\common\GarrysMod\bin\win64\steam_api64.dll")
APP_ID = 1158310
FILE_TYPE_COLLECTION = 2
VISIBILITY_PUBLIC = 0
TITLE = "Josheyer's Historical Modpack"
ID_FILE = ROOT / "collection_id.txt"

CREATE_ITEM_RESULT = (3403, 24)
SUBMIT_ITEM_UPDATE_RESULT = (3404, 16)
ADD_DEPENDENCY_RESULT = (3412, 24)


class Steam:
    def __init__(self) -> None:
        os.chdir(ROOT)
        (ROOT / "steam_appid.txt").write_text(str(APP_ID))
        self.api = ctypes.CDLL(str(DLL))
        a = self.api
        a.SteamAPI_InitFlat.restype = c_int
        a.SteamAPI_InitFlat.argtypes = [ctypes.c_char_p]
        err = ctypes.create_string_buffer(1024)
        if a.SteamAPI_InitFlat(err) != 0:
            raise SystemExit(f"SteamAPI init failed: {err.value.decode(errors='replace')}")
        a.SteamAPI_SteamUGC_v021.restype = c_void_p
        a.SteamAPI_SteamUtils_v010.restype = c_void_p
        self.ugc = a.SteamAPI_SteamUGC_v021()
        self.utils = a.SteamAPI_SteamUtils_v010()
        if not self.ugc or not self.utils:
            raise SystemExit("could not get ISteamUGC / ISteamUtils")

        a.SteamAPI_ISteamUGC_CreateItem.restype = c_uint64
        a.SteamAPI_ISteamUGC_CreateItem.argtypes = [c_void_p, c_uint32, c_int]
        a.SteamAPI_ISteamUGC_StartItemUpdate.restype = c_uint64
        a.SteamAPI_ISteamUGC_StartItemUpdate.argtypes = [c_void_p, c_uint32, c_uint64]
        for name in ("SetItemTitle", "SetItemDescription", "SetItemPreview"):
            fn = getattr(a, f"SteamAPI_ISteamUGC_{name}")
            fn.restype = c_bool
            fn.argtypes = [c_void_p, c_uint64, c_char_p]
        a.SteamAPI_ISteamUGC_SetItemVisibility.restype = c_bool
        a.SteamAPI_ISteamUGC_SetItemVisibility.argtypes = [c_void_p, c_uint64, c_int]
        a.SteamAPI_ISteamUGC_SubmitItemUpdate.restype = c_uint64
        a.SteamAPI_ISteamUGC_SubmitItemUpdate.argtypes = [c_void_p, c_uint64, c_char_p]
        a.SteamAPI_ISteamUGC_AddDependency.restype = c_uint64
        a.SteamAPI_ISteamUGC_AddDependency.argtypes = [c_void_p, c_uint64, c_uint64]
        a.SteamAPI_ISteamUtils_IsAPICallCompleted.restype = c_bool
        a.SteamAPI_ISteamUtils_IsAPICallCompleted.argtypes = [c_void_p, c_uint64, ctypes.POINTER(c_bool)]
        a.SteamAPI_ISteamUtils_GetAPICallResult.restype = c_bool
        a.SteamAPI_ISteamUtils_GetAPICallResult.argtypes = [
            c_void_p, c_uint64, c_void_p, c_int, c_int, ctypes.POINTER(c_bool)
        ]

    def wait(self, call: int, result: tuple[int, int], timeout: float = 120) -> bytes:
        callback_id, size = result
        failed = c_bool(False)
        deadline = time.time() + timeout
        while not self.api.SteamAPI_ISteamUtils_IsAPICallCompleted(self.utils, call, ctypes.byref(failed)):
            self.api.SteamAPI_RunCallbacks()
            if time.time() > deadline:
                raise SystemExit(f"timed out waiting for call {call}")
            time.sleep(0.1)
        buf = ctypes.create_string_buffer(size)
        ok = self.api.SteamAPI_ISteamUtils_GetAPICallResult(
            self.utils, call, buf, size, callback_id, ctypes.byref(failed)
        )
        if not ok or failed.value:
            raise SystemExit(f"call {call} failed (callback {callback_id})")
        return buf.raw

    def create_collection(self) -> int:
        raw = self.wait(self.api.SteamAPI_ISteamUGC_CreateItem(self.ugc, APP_ID, FILE_TYPE_COLLECTION), CREATE_ITEM_RESULT)
        result = int.from_bytes(raw[0:4], "little")
        file_id = int.from_bytes(raw[8:16], "little")
        if result != 1:
            raise SystemExit(f"CreateItem failed with EResult {result}")
        if raw[16]:
            print("Steam says the Workshop legal agreement still needs to be accepted.")
        return file_id

    def update(self, file_id: int, description: str, preview: Path, note: str) -> None:
        a = self.api
        handle = a.SteamAPI_ISteamUGC_StartItemUpdate(self.ugc, APP_ID, file_id)
        a.SteamAPI_ISteamUGC_SetItemTitle(self.ugc, handle, TITLE.encode())
        a.SteamAPI_ISteamUGC_SetItemDescription(self.ugc, handle, description.encode("utf-8"))
        a.SteamAPI_ISteamUGC_SetItemPreview(self.ugc, handle, str(preview).encode())
        a.SteamAPI_ISteamUGC_SetItemVisibility(self.ugc, handle, VISIBILITY_PUBLIC)
        raw = self.wait(a.SteamAPI_ISteamUGC_SubmitItemUpdate(self.ugc, handle, note.encode()), SUBMIT_ITEM_UPDATE_RESULT)
        result = int.from_bytes(raw[0:4], "little")
        if result != 1:
            raise SystemExit(f"SubmitItemUpdate failed with EResult {result}")

    def add_child(self, collection: int, child: int) -> int:
        raw = self.wait(self.api.SteamAPI_ISteamUGC_AddDependency(self.ugc, collection, child), ADD_DEPENDENCY_RESULT)
        return int.from_bytes(raw[0:4], "little")

    def close(self) -> None:
        self.api.SteamAPI_Shutdown()
        (ROOT / "steam_appid.txt").unlink(missing_ok=True)


def main() -> None:
    add_items = "--metadata-only" not in sys.argv
    description = (ROOT / "description.txt").read_text(encoding="utf-8").strip()
    order = [int(x) for x in (ROOT / "playset" / "collection_order.txt").read_text().split()]
    steam = Steam()
    try:
        if ID_FILE.exists():
            collection = int(ID_FILE.read_text().split()[0])
        else:
            collection = steam.create_collection()
            ID_FILE.write_text(f"{collection}\nhttps://steamcommunity.com/sharedfiles/filedetails/?id={collection}\n")
        print("collection", collection)
        steam.update(collection, description, ROOT / "preview.jpg", "Collection page and load order")
        print("metadata updated")
        if add_items:
            for i, mod in enumerate(order, 1):
                result = steam.add_child(collection, mod)
                print(f"{i:3}/{len(order)} {mod} -> {'ok' if result == 1 else f'EResult {result}'}")
    finally:
        steam.close()


if __name__ == "__main__":
    main()
