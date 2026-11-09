"""Start the desktop app without a console window on Windows."""

from app import GameLibrary


if __name__ == "__main__":
    GameLibrary().mainloop()
