import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core


class CoreTests(unittest.TestCase):
    def test_detection_ignores_setup_and_redist(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            folder = Path(tmp) / "Cool Game"
            folder.mkdir()
            (folder / "Cool Game.exe").touch()
            (folder / "launcher.exe").touch()
            (folder / "setup.exe").touch()
            redist = folder / "_CommonRedist"
            redist.mkdir()
            (redist / "Cool Game.exe").touch()

            found = core.find_executables(folder)
            self.assertEqual(found[0].path.name, "Cool Game.exe")
            self.assertEqual(len(found), 2)

    def test_library_round_trip_and_launch_path_check(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            folder = root / "Game"
            folder.mkdir()
            exe = folder / "Game.exe"
            exe.touch()
            game = {"name": "Game", "folder": str(folder), "executable": str(exe)}
            storage = root / "library.json"
            core.save_library([game], storage)
            self.assertEqual(core.load_library(storage), [game])

            outside = root / "Other.exe"
            outside.touch()
            game["executable"] = str(outside)
            with self.assertRaises(ValueError):
                core.launch(game)

            game["executable"] = str(exe)
            with patch.object(core.sys, "platform", "win32"), patch.object(core.subprocess, "Popen") as popen:
                core.launch(game)
            popen.assert_called_once_with([str(exe)], cwd=str(folder), close_fds=True)


if __name__ == "__main__":
    unittest.main()
