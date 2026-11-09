"""Private Windows desktop interface for a local game collection."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from core import find_executables, is_inside, launch, load_library, save_library


BG = "#101720"
PANEL = "#192431"
CARD = "#202e3d"
TEXT = "#f1f5f9"
MUTED = "#aebdcb"
ACCENT = "#76c7e8"
BUTTON = "#3c8db3"


class GameLibrary(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("مكتبتي | ألعاب الكمبيوتر")
        self.geometry("1000x650")
        self.minsize(720, 480)
        self.configure(bg=BG)
        try:
            self.games = load_library()
        except ValueError as exc:
            messagebox.showerror("المكتبة", str(exc))
            self.games = []

        header = tk.Frame(self, bg=PANEL, padx=28, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="مكتبتي", font=("Segoe UI", 24, "bold"), fg=TEXT, bg=PANEL).pack(side="right")
        tk.Button(header, text="＋  أضف لعبة", command=self.add_game, font=("Segoe UI", 12, "bold"),
                  bg=BUTTON, fg="white", activebackground=ACCENT, relief="flat", padx=18, pady=9,
                  cursor="hand2").pack(side="left")

        intro = tk.Frame(self, bg=BG, padx=30, pady=22)
        intro.pack(fill="x")
        self.count_label = tk.Label(intro, fg=ACCENT, bg=BG, font=("Segoe UI", 12))
        self.count_label.pack(anchor="e")
        tk.Label(intro, text="ألعابك على هذا الحاسوب فقط", fg=MUTED, bg=BG,
                 font=("Segoe UI", 11)).pack(anchor="e", pady=(4, 0))

        container = tk.Frame(self, bg=BG, padx=28)
        container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scroll = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="left", fill="y")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.cards = tk.Frame(self.canvas, bg=BG)
        self.window = self.canvas.create_window((0, 0), window=self.cards, anchor="nw")
        self.cards.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-int(e.delta / 120), "units"))
        self.render()

    def persist(self) -> bool:
        try:
            save_library(self.games)
            return True
        except OSError as exc:
            messagebox.showerror("تعذر الحفظ", str(exc))
            return False

    def add_game(self) -> None:
        selected = filedialog.askdirectory(title="اختر مجلد اللعبة")
        if not selected:
            return
        folder = Path(selected).resolve()
        if any(Path(g["folder"]).resolve() == folder for g in self.games):
            messagebox.showinfo("موجودة", "هذه اللعبة موجودة في المكتبة.")
            return
        try:
            candidates = find_executables(folder)
        except (OSError, ValueError) as exc:
            messagebox.showerror("تعذر فحص المجلد", str(exc))
            return
        if not candidates:
            messagebox.showwarning("لم أجد اللعبة", "لم أجد ملف تشغيل EXE مناسباً داخل المجلد.")
            return
        self.games.append({"name": folder.name, "folder": str(folder), "executable": str(candidates[0].path)})
        if not self.persist():
            self.games.pop()
            return
        self.render()
        if len(candidates) > 1:
            messagebox.showinfo("تمت الإضافة", f"اخترت تلقائياً: {candidates[0].path.name}\nيمكنك تغيير الملف من بطاقة اللعبة.")

    def play(self, game: dict[str, str]) -> None:
        try:
            launch(game)
        except (OSError, ValueError) as exc:
            messagebox.showerror("تعذر تشغيل اللعبة", str(exc))

    def change_executable(self, game: dict[str, str]) -> None:
        chosen = filedialog.askopenfilename(title="اختر ملف تشغيل اللعبة", initialdir=game["folder"],
                                            filetypes=[("Windows executable", "*.exe")])
        if not chosen:
            return
        path = Path(chosen)
        if path.suffix.casefold() != ".exe" or not is_inside(path, Path(game["folder"])):
            messagebox.showerror("اختيار غير صالح", "اختر ملف EXE من داخل مجلد هذه اللعبة.")
            return
        previous = game["executable"]
        game["executable"] = str(path.resolve())
        if not self.persist():
            game["executable"] = previous
        self.render()

    def remove_game(self, game: dict[str, str]) -> None:
        if not messagebox.askyesno("إزالة من المكتبة", f"إزالة {game['name']} من المكتبة؟\nلن تُحذف ملفات اللعبة."):
            return
        self.games.remove(game)
        if not self.persist():
            self.games.append(game)
        self.render()

    def render(self) -> None:
        for widget in self.cards.winfo_children():
            widget.destroy()
        self.count_label.configure(text=f"{len(self.games)} لعبة في المكتبة")
        if not self.games:
            tk.Label(self.cards, text="مكتبتك فارغة", fg=TEXT, bg=BG,
                     font=("Segoe UI", 21, "bold")).pack(pady=(65, 8))
            tk.Label(self.cards, text="اضغط «أضف لعبة» ثم اختر مجلدها من حاسوبك.", fg=MUTED,
                     bg=BG, font=("Segoe UI", 12)).pack()
            return
        for game in sorted(self.games, key=lambda g: g["name"].casefold()):
            card = tk.Frame(self.cards, bg=CARD, padx=20, pady=16)
            card.pack(fill="x", pady=7)
            details = tk.Frame(card, bg=CARD)
            details.pack(side="right", fill="x", expand=True)
            tk.Label(details, text=game["name"], bg=CARD, fg=TEXT,
                     font=("Segoe UI", 18, "bold"), anchor="e").pack(fill="x")
            tk.Label(details, text=f"ملف التشغيل: {Path(game['executable']).name}", bg=CARD, fg=ACCENT,
                     font=("Segoe UI", 10), anchor="e").pack(fill="x", pady=(5, 0))
            tk.Label(details, text=game["folder"], bg=CARD, fg=MUTED,
                     font=("Segoe UI", 9), anchor="e").pack(fill="x", pady=(4, 0))
            actions = tk.Frame(card, bg=CARD)
            actions.pack(side="left", padx=(0, 18))
            tk.Button(actions, text="العب ▶", command=lambda g=game: self.play(g), bg=BUTTON, fg="white",
                      activebackground=ACCENT, relief="flat", padx=20, pady=8,
                      font=("Segoe UI", 12, "bold"), cursor="hand2").pack(fill="x")
            tk.Button(actions, text="تغيير الملف", command=lambda g=game: self.change_executable(g),
                      bg=CARD, fg=TEXT, activebackground=PANEL, relief="flat",
                      font=("Segoe UI", 9), cursor="hand2").pack(fill="x", pady=(7, 0))
            tk.Button(actions, text="إزالة", command=lambda g=game: self.remove_game(g),
                      bg=CARD, fg=MUTED, activebackground=PANEL, relief="flat",
                      font=("Segoe UI", 9), cursor="hand2").pack(fill="x")


if __name__ == "__main__":
    GameLibrary().mainloop()
