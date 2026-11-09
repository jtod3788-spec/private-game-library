# Private Game Library

A small, offline Windows desktop app for organizing games already installed on your PC. Choose a game's folder, and the app finds a likely `.exe` and adds a **Play** button. The interface is in Arabic.

## Requirements

- Windows 10 or 11
- Python 3 with Tkinter (included with the standard Windows Python installer)
- No third-party Python packages or internet connection

## Run

Double-click `run.pyw` to open the app without a command window. This uses the Windows Python file association. If `.pyw` is not associated with Python on your computer, open a terminal in this folder and run:

```powershell
py -3 app.py
```

Click **أضف لعبة** (Add game) and select the complete game folder. The app chooses a likely executable. If it chooses the wrong one, click **تغيير الملف** (Change executable) on that game's card and select the correct `.exe` from the same folder. Click **العب** (Play) to launch it.

## Privacy and safety

- All scanning happens locally. There is no account, server, telemetry, download, or upload.
- The app stores only game names and local paths in `%LOCALAPPDATA%\PrivateGameLibrary\library.json`. This file is created when you add a game and is **not part of this repository**.
- Removing a game from the library never deletes the game files.
- The automatic choice is a heuristic. Check the displayed executable before first launch. A launched game runs with your Windows user permissions, so add only software you trust.
- No games, game assets, cracks, or DRM bypass tools are included.

## Test

```powershell
py -3 -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
