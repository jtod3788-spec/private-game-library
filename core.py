"""Local game library storage and executable discovery."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


APP_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "PrivateGameLibrary"
LIBRARY_FILE = APP_DIR / "library.json"
IGNORED_DIRS = {
    "$recycle.bin", ".git", "__macosx", "_commonredist", "commonredist",
    "directx", "dotnet", "engine", "installer", "installers", "prerequisites",
    "redist", "redistributables", "support", "vcredist", "webview2",
}
BAD_NAMES = {
    "crashhandler", "crashreport", "crashreporter", "dxsetup", "easyanticheat",
    "eac", "install", "installer", "setup", "uninstall", "unins000",
    "updater", "update", "vc_redist", "vcredist", "unitycrashhandler32",
    "unitycrashhandler64", "ue4prereqsetup_x64", "ue4prereqsetup_x86",
}
BAD_FRAGMENTS = ("crash", "unins", "redist", "prereq", "anticheat", "update", "setup")


@dataclass(frozen=True)
class Candidate:
    path: Path
    score: int


def _words(value: str) -> set[str]:
    return set(re.findall(r"[\w]+", value.casefold().replace("_", " ")))


def find_executables(folder: Path, max_depth: int = 4) -> list[Candidate]:
    folder = folder.expanduser().resolve()
    if not folder.is_dir():
        raise ValueError("مجلد اللعبة غير موجود.")

    game_words = _words(folder.name) - {"game", "games", "win64", "win32"}
    candidates: list[Candidate] = []
    for root, dirs, files in os.walk(folder, followlinks=False):
        current = Path(root)
        depth = len(current.relative_to(folder).parts)
        dirs[:] = sorted(
            d for d in dirs
            if depth < max_depth and d.casefold() not in IGNORED_DIRS
            and not (current / d).is_symlink()
        )
        for name in files:
            if not name.casefold().endswith(".exe"):
                continue
            path = current / name
            if path.is_symlink():
                continue
            stem = path.stem.casefold()
            if stem in BAD_NAMES or any(part in stem for part in BAD_FRAGMENTS):
                continue
            exe_words = _words(path.stem)
            score = 100 - 15 * depth
            score += 35 * len(game_words & exe_words)
            if game_words and game_words <= exe_words:
                score += 45
            if "game" in exe_words:
                score += 8
            if "launcher" in exe_words:
                score -= 18
            if "shipping" in exe_words:
                score += 12
            candidates.append(Candidate(path, score))
    return sorted(candidates, key=lambda c: (-c.score, len(c.path.parts), str(c.path).casefold()))


def load_library(path: Path = LIBRARY_FILE) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError
        result = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if all(isinstance(item.get(key), str) for key in ("name", "folder", "executable")):
                result.append({key: item[key] for key in ("name", "folder", "executable")})
        return result
    except (OSError, ValueError, json.JSONDecodeError):
        raise ValueError("ملف المكتبة غير صالح أو لا يمكن قراءته.")


def save_library(games: list[dict[str, str]], path: Path = LIBRARY_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(games, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def is_inside(executable: Path, folder: Path) -> bool:
    try:
        executable.resolve().relative_to(folder.resolve())
        return True
    except ValueError:
        return False


def launch(game: dict[str, str]) -> None:
    folder = Path(game["folder"])
    executable = Path(game["executable"])
    if not folder.is_dir() or not executable.is_file() or not is_inside(executable, folder):
        raise ValueError("ملف تشغيل اللعبة غير موجود داخل مجلدها. عدّل اختيار الملف.")
    if executable.suffix.casefold() != ".exe":
        raise ValueError("يمكن تشغيل ملفات EXE فقط.")
    if sys.platform != "win32":
        raise OSError("تشغيل الألعاب متاح على Windows فقط.")
    subprocess.Popen([str(executable)], cwd=str(executable.parent), close_fds=True)
