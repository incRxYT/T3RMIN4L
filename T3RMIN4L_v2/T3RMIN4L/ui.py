"""ui.py — T3RMIN4L v2 UI (customtkinter)."""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
from typing import Optional
import customtkinter as ctk

import themes as th
import quicktheme as qt
import background as bg
import backup as bk
import settings as st

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PALETTE = {
    "bg":       "#05050d",
    "surface":  "#0d0d1a",
    "card":     "#111122",
    "border":   "#1e1e3a",
    "accent":   "#00ffcc",
    "accent2":  "#bd93f9",
    "accent3":  "#ff5555",
    "text":     "#e8e8f0",
    "muted":    "#6666aa",
    "input_bg": "#0a0a18",
}

FONT_MONO  = ("Consolas", 12)
FONT_TITLE = ("Consolas", 19, "bold")
FONT_BTN   = ("Consolas", 11, "bold")
FONT_SMALL = ("Consolas", 9)


# ── Reusable widgets ──────────────────────────────────────────────────────────

class GlowLabel(ctk.CTkLabel):
    def __init__(self, master, text, color=None, font=None, **kw):
        super().__init__(master, text=text,
                         text_color=color or PALETTE["accent"],
                         font=font or FONT_MONO, **kw)


class Divider(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, height=1, fg_color=PALETTE["border"], **kw)


class NeonBtn(ctk.CTkButton):
    def __init__(self, master, text, command=None, color=None, width=140, **kw):
        c = color or PALETTE["accent"]
        super().__init__(master, text=text, command=command, width=width,
                         fg_color="transparent", border_width=1, border_color=c,
                         text_color=c, hover_color=c + "22",
                         font=FONT_BTN, corner_radius=4, **kw)


class SmallBtn(ctk.CTkButton):
    def __init__(self, master, text, command=None, color=None, width=80, **kw):
        c = color or PALETTE["muted"]
        super().__init__(master, text=text, command=command, width=width, height=26,
                         fg_color="transparent", border_width=1, border_color=c,
                         text_color=c, hover_color=c + "22",
                         font=FONT_SMALL, corner_radius=3, **kw)


# ── Color swatch strip ────────────────────────────────────────────────────────

class SwatchStrip(ctk.CTkFrame):
    FIELDS = [
        "black", "red", "green", "yellow", "blue", "purple", "cyan", "white",
        "brightBlack", "brightRed", "brightGreen", "brightYellow",
        "brightBlue", "brightPurple", "brightCyan", "brightWhite",
    ]

    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._swatches: list[tk.Canvas] = []
        for _ in self.FIELDS:
            c = tk.Canvas(self, width=18, height=18, bd=0,
                          highlightthickness=0, bg=PALETTE["bg"])
            c.pack(side="left", padx=1)
            self._swatches.append(c)

    def update(self, scheme: dict):
        for i, field in enumerate(self.FIELDS):
            color = scheme.get(field, "#222233")
            try:
                self._swatches[i].configure(bg=color)
                self._swatches[i].delete("all")
                self._swatches[i].create_rectangle(0, 0, 18, 18, fill=color, outline="")
            except Exception:
                pass


# ── Terminal mock preview ─────────────────────────────────────────────────────

class TerminalPreview(ctk.CTkFrame):
    LINES = [
        ("$ ", "cursor", "git status", "fg"),
        ("On branch ", "dim", "main", "green"),
        ("nothing to commit, working tree clean", "white", "", ""),
        ("$ ", "cursor", "ls -la", "fg"),
        ("drwxr-xr-x  user  staff  ", "blue", "4.0K .", "cyan"),
        ("$ ", "cursor", "echo 'T3RMIN4L v2'", "fg"),
        ("T3RMIN4L v2", "purple", "", ""),
        ("$ ", "cursor", "_", "cursor"),
    ]

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=PALETTE["card"],
                         border_width=1, border_color=PALETTE["border"],
                         corner_radius=6, **kw)
        bar = ctk.CTkFrame(self, fg_color=PALETTE["surface"], height=28, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        for col in ("#ff5555", "#f1fa8c", "#50fa7b"):
            ctk.CTkFrame(bar, width=10, height=10, fg_color=col,
                         corner_radius=5).pack(side="left", padx=(6, 2), pady=9)
        ctk.CTkLabel(bar, text="Windows Terminal — Preview",
                     text_color=PALETTE["muted"], font=FONT_SMALL).pack(side="left", padx=8)

        self._text = tk.Text(self, bg=PALETTE["bg"], fg=PALETTE["text"],
                             font=("Consolas", 11), bd=0, highlightthickness=0,
                             insertbackground=PALETTE["accent"], state="disabled",
                             wrap="none", padx=10, pady=8, cursor="arrow",
                             selectbackground=PALETTE["border"])
        self._text.pack(fill="both", expand=True)
        self._scheme: dict = {}
        self._render()

    def _resolve(self, key: str) -> str:
        s = self._scheme
        m = {
            "cursor": s.get("cursorColor", PALETTE["accent"]),
            "fg":     s.get("foreground",  PALETTE["text"]),
            "dim":    s.get("brightBlack", PALETTE["muted"]),
            "green":  s.get("green",       "#50fa7b"),
            "cyan":   s.get("cyan",        "#8be9fd"),
            "blue":   s.get("blue",        "#6272a4"),
            "purple": s.get("purple",      "#bd93f9"),
            "white":  s.get("white",       "#f8f8f2"),
        }
        return m.get(key, PALETTE["text"])

    def _render(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(bg=self._scheme.get("background", PALETTE["bg"]))
        for t1, c1, t2, c2 in self.LINES:
            col1 = self._resolve(c1)
            col2 = self._resolve(c2)
            tag1 = f"t_{c1}_{t1}"
            tag2 = f"t_{c2}_{t2}"
            self._text.tag_configure(tag1, foreground=col1)
            self._text.tag_configure(tag2, foreground=col2)
            self._text.insert("end", t1, tag1)
            if t2:
                self._text.insert("end", t2, tag2)
            self._text.insert("end", "\n")
        self._text.configure(state="disabled")

    def apply(self, scheme: dict):
        self._scheme = scheme
        self._render()


# ── Quick Theme pane ──────────────────────────────────────────────────────────

class QuickThemePane(ctk.CTkFrame):
    def __init__(self, master, on_preview, on_save, **kw):
        super().__init__(master, fg_color=PALETTE["card"],
                         border_width=1, border_color=PALETTE["border"],
                         corner_radius=6, **kw)
        self._on_preview = on_preview
        self._on_save    = on_save

        hdr = ctk.CTkFrame(self, fg_color=PALETTE["surface"], height=32, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        GlowLabel(hdr, "⚡ QUICK THEME", font=("Consolas", 11, "bold"),
                  color=PALETTE["accent2"]).pack(side="left", padx=12, pady=6)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=10, pady=8)

        self._editor = tk.Text(
            body, bg=PALETTE["input_bg"], fg=PALETTE["text"], font=FONT_MONO,
            bd=0, highlightthickness=1, highlightcolor=PALETTE["border"],
            highlightbackground=PALETTE["border"],
            insertbackground=PALETTE["accent"], wrap="none", padx=8, pady=6, undo=True)
        self._editor.pack(fill="both", expand=True)
        self._editor.insert("1.0", qt.EXAMPLE_THEME)
        self._editor.bind("<KeyRelease>", lambda _: self._preview())

        self._err = ctk.CTkLabel(body, text="", text_color=PALETTE["accent3"],
                                  font=FONT_SMALL, anchor="w", wraplength=340)
        self._err.pack(fill="x", pady=(4, 0))

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x", pady=(6, 0))
        SmallBtn(btn_row, "Preview", command=self._preview,
                 color=PALETTE["accent2"]).pack(side="left", padx=(0, 6))
        SmallBtn(btn_row, "Clear", command=lambda: self._editor.delete("1.0", "end"),
                 color=PALETTE["muted"]).pack(side="left")

        name_row = ctk.CTkFrame(body, fg_color="transparent")
        name_row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(name_row, text="Name:", text_color=PALETTE["muted"],
                     font=FONT_SMALL).pack(side="left", padx=(0, 6))
        self._name = ctk.StringVar(value="My Theme")
        ctk.CTkEntry(name_row, textvariable=self._name, width=170,
                     fg_color=PALETTE["input_bg"], border_color=PALETTE["border"],
                     text_color=PALETTE["text"], font=FONT_MONO).pack(side="left")
        NeonBtn(name_row, "Save", command=self._save,
                color=PALETTE["accent"], width=90).pack(side="right")

    def _preview(self):
        parsed, errors = qt.parse_quick_theme(self._editor.get("1.0", "end"))
        self._err.configure(text=("⚠  " + errors[0]) if errors else "")
        self._on_preview(qt.to_wt_scheme("__preview__", parsed))

    def _save(self):
        parsed, errors = qt.parse_quick_theme(self._editor.get("1.0", "end"))
        if errors:
            self._err.configure(text="⚠  " + " | ".join(errors[:2]))
            return
        name = self._name.get().strip() or "My Theme"
        scheme = qt.to_wt_scheme(name, parsed)
        overrides = qt.quick_theme_to_profile_overrides(parsed)
        self._on_save(scheme, overrides)
        self._err.configure(text=f"✓  Saved '{name}'")

    def load_scheme(self, scheme: dict):
        alias_rev = {v: k for k, v in qt.ALIASES.items()}
        fields = [
            "background", "foreground", "cursorColor", "selectionBackground",
            "black", "red", "green", "yellow", "blue", "purple", "cyan", "white",
            "brightBlack", "brightRed", "brightGreen", "brightYellow",
            "brightBlue", "brightPurple", "brightCyan", "brightWhite",
        ]
        lines = [f"{alias_rev.get(f, f)}: {scheme[f]};" for f in fields if f in scheme]
        self._editor.delete("1.0", "end")
        self._editor.insert("1.0", "\n".join(lines))
        self._name.set(scheme.get("name", "Edited Theme"))
        self._err.configure(text="")


# ── Background pane ───────────────────────────────────────────────────────────

class BackgroundPane(ctk.CTkFrame):
    def __init__(self, master, on_apply, on_remove, recent_path: Optional[str] = None, **kw):
        super().__init__(master, fg_color=PALETTE["card"],
                         border_width=1, border_color=PALETTE["border"],
                         corner_radius=6, **kw)
        self._on_apply  = on_apply
        self._on_remove = on_remove
        self._image_path: Optional[Path] = Path(recent_path) if recent_path else None

        hdr = ctk.CTkFrame(self, fg_color=PALETTE["surface"], height=32, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        GlowLabel(hdr, "🖼  BACKGROUND", font=("Consolas", 11, "bold"),
                  color=PALETTE["accent"]).pack(side="left", padx=12, pady=6)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=10)

        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self._path_var = ctk.StringVar(
            value=self._image_path.name if self._image_path else "No image selected")
        ctk.CTkLabel(row, textvariable=self._path_var, text_color=PALETTE["muted"],
                     font=FONT_SMALL, anchor="w").pack(side="left", fill="x", expand=True)
        SmallBtn(row, "Browse…", command=self._browse, color=PALETTE["accent"]).pack(side="right")

        self._warn = ctk.CTkLabel(body, text="", text_color="#f1fa8c",
                                   font=FONT_SMALL, anchor="w", wraplength=340)
        self._warn.pack(fill="x", pady=(4, 0))

        Divider(body).pack(fill="x", pady=8)

        def lbl(t): ctk.CTkLabel(body, text=t, text_color=PALETTE["muted"],
                                  font=FONT_SMALL, anchor="w").pack(fill="x")

        lbl("Opacity")
        self._opacity = ctk.CTkSlider(body, from_=0, to=1, number_of_steps=20,
                                       progress_color=PALETTE["accent"],
                                       button_color=PALETTE["accent"])
        self._opacity.set(0.5)
        self._opacity.pack(fill="x", pady=(2, 8))

        lbl("Stretch Mode")
        self._stretch = ctk.CTkOptionMenu(body, values=bg.STRETCH_MODES,
                                           fg_color=PALETTE["input_bg"],
                                           button_color=PALETTE["border"],
                                           text_color=PALETTE["text"], font=FONT_SMALL)
        self._stretch.set("uniformToFill")
        self._stretch.pack(fill="x", pady=(2, 8))

        lbl("Alignment")
        self._align = ctk.CTkOptionMenu(body, values=bg.ALIGNMENT_OPTIONS,
                                         fg_color=PALETTE["input_bg"],
                                         button_color=PALETTE["border"],
                                         text_color=PALETTE["text"], font=FONT_SMALL)
        self._align.set("center")
        self._align.pack(fill="x", pady=(2, 8))

        tog = ctk.CTkFrame(body, fg_color="transparent")
        tog.pack(fill="x", pady=4)
        self._blur    = ctk.BooleanVar(value=False)
        self._acrylic = ctk.BooleanVar(value=False)
        for text, var in (("Blur", self._blur), ("Acrylic", self._acrylic)):
            ctk.CTkCheckBox(tog, text=text, variable=var, text_color=PALETTE["text"],
                            font=FONT_SMALL, checkmark_color=PALETTE["accent"],
                            border_color=PALETTE["border"]).pack(side="left", padx=(0, 16))

        Divider(body).pack(fill="x", pady=8)
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")
        NeonBtn(btn_row, "Apply Background", command=self._apply,
                color=PALETTE["accent"], width=160).pack(side="left")
        SmallBtn(btn_row, "Remove", command=self._remove,
                 color=PALETTE["accent3"]).pack(side="right")

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif"), ("All Files", "*.*")])
        if not path:
            return
        self._image_path = Path(path)
        self._path_var.set(self._image_path.name)
        self._warn.configure(
            text=("⚠  GIF animations aren't supported — first frame will be used."
                  if bg.is_gif(self._image_path) else ""))

    def _apply(self):
        if not self._image_path:
            messagebox.showwarning("No Image", "Select an image first.")
            return
        valid, msg = bg.validate_image(self._image_path)
        if not valid:
            messagebox.showerror("Invalid Image", msg)
            return
        result = bg.build_background_config(
            self._image_path, opacity=self._opacity.get(),
            stretch=self._stretch.get(), alignment=self._align.get(),
            blur=self._blur.get(), acrylic=self._acrylic.get())
        if result["warning"]:
            self._warn.configure(text=result["warning"])
        self._on_apply(result["config"], str(self._image_path))

    def _remove(self):
        self._on_remove()

    def get_path(self) -> Optional[str]:
        return str(self._image_path) if self._image_path else None


# ── Backup window ─────────────────────────────────────────────────────────────

class BackupWindow(ctk.CTkToplevel):
    def __init__(self, master, settings_path: Optional[Path], on_restore, **kw):
        super().__init__(master, **kw)
        self.title("T3RMIN4L — Backup Manager")
        self.geometry("540x440")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["bg"])
        self._settings_path = settings_path
        self._on_restore    = on_restore

        GlowLabel(self, "BACKUP MANAGER", font=("Consolas", 14, "bold")).pack(pady=(20, 4))
        Divider(self).pack(fill="x", padx=20, pady=8)

        self._list = ctk.CTkScrollableFrame(self, fg_color=PALETTE["surface"],
                                             corner_radius=4, height=270)
        self._list.pack(fill="x", padx=20)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=14)
        NeonBtn(row, "Create Backup Now", command=self._create,
                color=PALETTE["accent"]).pack(side="left", padx=8)
        NeonBtn(row, "Close", command=self.destroy,
                color=PALETTE["muted"]).pack(side="left", padx=8)

        self._refresh()

    def _refresh(self):
        for w in self._list.winfo_children():
            w.destroy()
        if not self._settings_path:
            ctk.CTkLabel(self._list, text="settings.json not found.",
                         text_color=PALETTE["muted"], font=FONT_SMALL).pack(pady=10)
            return
        summaries = bk.backup_summary(self._settings_path)
        if not summaries:
            ctk.CTkLabel(self._list, text="No backups yet.",
                         text_color=PALETTE["muted"], font=FONT_SMALL).pack(pady=10)
            return
        for s in summaries:
            r = ctk.CTkFrame(self._list, fg_color=PALETTE["card"], corner_radius=4)
            r.pack(fill="x", pady=3, padx=4)
            ctk.CTkLabel(r, text=s["date"], text_color=PALETTE["text"],
                         font=FONT_SMALL).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(r, text=f"{s['size_kb']} KB", text_color=PALETTE["muted"],
                         font=FONT_SMALL).pack(side="left", padx=6)
            SmallBtn(r, "Restore", command=lambda p=s["path"]: self._restore(p),
                     color=PALETTE["accent"]).pack(side="right", padx=8, pady=4)

    def _create(self):
        if not self._settings_path:
            return
        dest = bk.create_backup(self._settings_path)
        if dest:
            messagebox.showinfo("Backup Created", f"Saved: {dest.name}")
            self._refresh()

    def _restore(self, path: Path):
        if messagebox.askyesno("Restore", f"Restore '{path.name}'?\nThis overwrites current settings."):
            if bk.restore_backup(path, self._settings_path):
                messagebox.showinfo("Restored", "Restart Windows Terminal to apply.")
                self._on_restore()
            else:
                messagebox.showerror("Error", "Could not restore backup.")


# ── Rename dialog ─────────────────────────────────────────────────────────────

class RenameDialog(ctk.CTkToplevel):
    def __init__(self, master, current_name: str, on_confirm, **kw):
        super().__init__(master, **kw)
        self.title("Rename Theme")
        self.geometry("360x160")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["bg"])
        self._on_confirm = on_confirm

        ctk.CTkLabel(self, text="New theme name:", text_color=PALETTE["text"],
                     font=FONT_SMALL).pack(pady=(20, 6))
        self._var = ctk.StringVar(value=current_name)
        ctk.CTkEntry(self, textvariable=self._var, width=300,
                     fg_color=PALETTE["input_bg"], border_color=PALETTE["border"],
                     text_color=PALETTE["text"], font=FONT_MONO).pack()

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=16)
        NeonBtn(row, "Confirm", command=self._confirm,
                color=PALETTE["accent"], width=110).pack(side="left", padx=8)
        NeonBtn(row, "Cancel", command=self.destroy,
                color=PALETTE["muted"], width=90).pack(side="left", padx=8)

    def _confirm(self):
        name = self._var.get().strip()
        if name:
            self._on_confirm(name)
        self.destroy()


# ── Sidebar ───────────────────────────────────────────────────────────────────

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_select, **kw):
        super().__init__(master, fg_color=PALETTE["surface"], width=220,
                         corner_radius=0, **kw)
        self.pack_propagate(False)
        self._on_select = on_select
        self._selected: Optional[str] = None
        self._btns: dict[str, ctk.CTkButton] = {}

        # Logo
        hdr = ctk.CTkFrame(self, fg_color=PALETTE["bg"], height=52, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        GlowLabel(hdr, "T3RMIN4L", font=FONT_TITLE,
                  color=PALETTE["accent"]).pack(side="left", padx=16)
        GlowLabel(hdr, "v2", font=("Consolas", 10),
                  color=PALETTE["muted"]).pack(side="left", pady=(14, 0))

        Divider(self).pack(fill="x")

        # Section labels
        self._make_section("BUILT-IN")
        self._builtin_frame = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                      corner_radius=0, height=200)
        self._builtin_frame.pack(fill="x")

        Divider(self).pack(fill="x", pady=(4, 0))
        self._make_section("CUSTOM")
        self._custom_frame = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                     corner_radius=0)
        self._custom_frame.pack(fill="both", expand=True)

        Divider(self).pack(fill="x")
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", pady=8)
        for label, event in (
            ("⟳  Backups",   "<<OpenBackups>>"),
            ("↑  Import",    "<<ImportTheme>>"),
            ("↓  Export",    "<<ExportTheme>>"),
        ):
            SmallBtn(nav, label, command=lambda e=event: master.event_generate(e),
                     color=PALETTE["muted"], width=190).pack(padx=10, pady=2, fill="x")

    def _make_section(self, label: str):
        ctk.CTkLabel(self, text=label, text_color=PALETTE["muted"],
                     font=("Consolas", 9, "bold"), anchor="w").pack(
            fill="x", padx=14, pady=(8, 2))

    def _make_btn(self, parent, name: str) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            parent, text=name, anchor="w",
            fg_color="transparent", hover_color=PALETTE["border"],
            text_color=PALETTE["text"], font=FONT_SMALL,
            corner_radius=3, height=30,
            command=lambda n=name: self._select(n))
        btn.pack(fill="x", padx=6, pady=1)
        return btn

    def populate(self, builtin_names: list[str], custom_names: list[str]):
        for frame, names in ((self._builtin_frame, builtin_names),
                             (self._custom_frame, custom_names)):
            for w in frame.winfo_children():
                w.destroy()
        self._btns.clear()
        for name in builtin_names:
            self._btns[name] = self._make_btn(self._builtin_frame, name)
        for name in custom_names:
            self._btns[name] = self._make_btn(self._custom_frame, name)

    def _select(self, name: str):
        if self._selected and self._selected in self._btns:
            self._btns[self._selected].configure(
                fg_color="transparent", text_color=PALETTE["text"])
        self._selected = name
        if name in self._btns:
            self._btns[name].configure(fg_color=PALETTE["border"],
                                        text_color=PALETTE["accent"])
        self._on_select(name)

    def select_name(self, name: str):
        if name in self._btns:
            self._select(name)

    def get_selected(self) -> Optional[str]:
        return self._selected


# ── Main App ──────────────────────────────────────────────────────────────────

class T3RMINAL(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("T3RMIN4L v2 — Windows Terminal Theme Manager")
        self.configure(fg_color=PALETTE["bg"])

        # Load persisted state
        self._state = st.load()
        geo = self._state.get("window_geometry", "1100x700")
        self.geometry(geo)
        self.minsize(920, 620)

        self._settings_path: Optional[Path] = th.find_settings_path()
        self._settings: dict = {}
        self._selected_scheme: Optional[dict] = None
        self._custom_names: list[str] = []

        self._load_all()
        self._build_ui()
        self._populate()

        # Restore last selected theme
        last = self._state.get("last_theme")
        if last:
            self._sidebar.select_name(last)

        # Save window size on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.bind("<<OpenBackups>>", lambda _: self._open_backups())
        self.bind("<<ImportTheme>>", lambda _: self._import_theme())
        self.bind("<<ExportTheme>>", lambda _: self._export_theme())

    # ── Data loading ──────────────────────────────────────────────────────────

    def _load_all(self):
        """Load WT settings.json and merge bundled + custom themes."""
        if self._settings_path:
            try:
                self._settings = th.load_settings(self._settings_path)
            except Exception:
                self._settings = {}
        else:
            self._settings = {}

        # Inject bundled themes (don't overwrite existing)
        existing = {s.get("name") for s in th.list_schemes(self._settings)}
        for bt in th.BUNDLED_THEMES:
            if bt["name"] not in existing:
                th.add_or_update_scheme(self._settings, bt)

        # Load custom themes from themes/ folder
        custom = st.load_all_custom_themes()
        self._custom_names = []
        for scheme in custom:
            name = scheme.get("name", "")
            if name not in th.BUNDLED_NAMES:
                th.add_or_update_scheme(self._settings, scheme)
                self._custom_names.append(name)

    def _save_wt(self) -> bool:
        if not self._settings_path:
            messagebox.showwarning("Not Found",
                                   "Windows Terminal settings.json not found.\n"
                                   "Install Windows Terminal and try again.")
            return False
        return th.save_settings(self._settings_path, self._settings)

    def _save_state(self):
        self._state["last_theme"] = (self._selected_scheme.get("name")
                                      if self._selected_scheme else None)
        self._state["window_geometry"] = self.geometry()
        if self._bg_pane.get_path():
            self._state["recent_bg"] = self._bg_pane.get_path()
        st.save(self._state)

    def _on_close(self):
        self._save_state()
        self.destroy()

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._sidebar = Sidebar(self, on_select=self._on_select)
        self._sidebar.pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        main.pack(side="left", fill="both", expand=True)

        # Top action bar
        top = ctk.CTkFrame(main, fg_color=PALETTE["surface"], height=50, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        self._title_lbl = ctk.CTkLabel(top, text="Select a theme →",
                                        text_color=PALETTE["accent"],
                                        font=("Consolas", 13, "bold"))
        self._title_lbl.pack(side="left", padx=16)

        # Action buttons right-to-left
        NeonBtn(top, "▶  Apply", command=self._apply_theme,
                color=PALETTE["accent"], width=110).pack(side="right", padx=8)
        SmallBtn(top, "✕ Remove", command=self._remove_theme,
                 color=PALETTE["accent3"]).pack(side="right", padx=4)
        SmallBtn(top, "Duplicate", command=self._duplicate_theme,
                 color=PALETTE["muted"]).pack(side="right", padx=4)
        SmallBtn(top, "Rename", command=self._rename_theme,
                 color=PALETTE["muted"]).pack(side="right", padx=4)
        SmallBtn(top, "Edit →", command=self._edit_in_quick,
                 color=PALETTE["accent2"]).pack(side="right", padx=4)

        # Content area
        cols = ctk.CTkFrame(main, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=10, pady=10)
        cols.columnconfigure(0, weight=3)
        cols.columnconfigure(1, weight=2)
        cols.rowconfigure(0, weight=2)
        cols.rowconfigure(1, weight=1)

        self._preview = TerminalPreview(cols)
        self._preview.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))

        # Swatch card
        sw_card = ctk.CTkFrame(cols, fg_color=PALETTE["card"],
                                border_width=1, border_color=PALETTE["border"],
                                corner_radius=6, height=50)
        sw_card.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        sw_card.pack_propagate(False)
        sw_inner = ctk.CTkFrame(sw_card, fg_color="transparent")
        sw_inner.pack(expand=True)
        ctk.CTkLabel(sw_inner, text="COLORS  ", text_color=PALETTE["muted"],
                     font=FONT_SMALL).pack(side="left")
        self._swatches = SwatchStrip(sw_inner)
        self._swatches.pack(side="left")

        self._qt_pane = QuickThemePane(cols, on_preview=self._on_quick_preview,
                                        on_save=self._on_quick_save)
        self._qt_pane.grid(row=0, column=1, rowspan=2, sticky="nsew")

        # Bottom bar
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(0, 8))

        self._status = ctk.CTkLabel(bottom, text=self._status_text(),
                                     text_color=PALETTE["muted"],
                                     font=FONT_SMALL, anchor="w")
        self._status.pack(fill="x", padx=4)

        self._bg_visible = False
        self._bg_toggle = SmallBtn(bottom, "🖼  Background Settings",
                                    command=self._toggle_bg, color=PALETTE["accent"])
        self._bg_toggle.pack(anchor="w", pady=4)

        self._bg_pane = BackgroundPane(
            bottom, on_apply=self._apply_background, on_remove=self._remove_background,
            recent_path=self._state.get("recent_bg"))

    def _status_text(self) -> str:
        if self._settings_path:
            return f"✓  {self._settings_path}"
        return "⚠  Windows Terminal not found — theme preview only"

    def _toggle_bg(self):
        if self._bg_visible:
            self._bg_pane.pack_forget()
            self._bg_toggle.configure(text="🖼  Background Settings")
        else:
            self._bg_pane.pack(fill="x", pady=(4, 0))
            self._bg_toggle.configure(text="✕  Hide Background Settings")
        self._bg_visible = not self._bg_visible

    # ── Populate sidebar ──────────────────────────────────────────────────────

    def _populate(self):
        builtin = [t["name"] for t in th.BUNDLED_THEMES]
        self._sidebar.populate(builtin, self._custom_names)

    # ── Theme selection ───────────────────────────────────────────────────────

    def _on_select(self, name: str):
        scheme = th.get_scheme_by_name(self._settings, name)
        if not scheme:
            return
        self._selected_scheme = scheme
        self._title_lbl.configure(text=name)
        self._preview.apply(scheme)
        self._swatches.update(scheme)

    def _on_quick_preview(self, scheme: dict):
        self._preview.apply(scheme)
        self._swatches.update(scheme)

    def _on_quick_save(self, scheme: dict, overrides: dict):
        name = scheme.get("name", "")
        errors = th.validate_scheme(scheme)
        if errors:
            messagebox.showerror("Invalid Theme", "\n".join(errors))
            return
        th.add_or_update_scheme(self._settings, scheme)
        st.save_custom_theme(scheme)
        if name not in self._custom_names:
            self._custom_names.append(name)
        self._populate()
        self._sidebar.select_name(name)
        self._save_wt()
        self._status.configure(text=f"✓  Saved custom theme '{name}'")

    # ── Apply / Remove / Duplicate / Rename ───────────────────────────────────

    def _apply_theme(self):
        if not self._selected_scheme:
            messagebox.showinfo("No Theme", "Select a theme first.")
            return
        name = self._selected_scheme["name"]
        errors = th.validate_scheme(self._selected_scheme)
        if errors:
            if not messagebox.askyesno("Warning",
                                        f"Theme has issues:\n{errors[0]}\n\nApply anyway?"):
                return
        th.apply_scheme_to_default_profile(self._settings, name)
        if self._save_wt():
            self._save_state()
            self._status.configure(
                text=f"✓  Applied '{name}' — restart Windows Terminal to see changes")

    def _remove_theme(self):
        if not self._selected_scheme:
            return
        name = self._selected_scheme["name"]
        if name in th.BUNDLED_NAMES:
            messagebox.showinfo("Built-in", "Built-in themes cannot be removed.")
            return
        if not messagebox.askyesno("Remove Theme", f"Delete '{name}' permanently?"):
            return
        th.remove_scheme(self._settings, name)
        st.delete_custom_theme(name)
        if name in self._custom_names:
            self._custom_names.remove(name)
        self._selected_scheme = None
        self._title_lbl.configure(text="Select a theme →")
        self._populate()
        self._save_wt()
        self._status.configure(text=f"✓  Removed '{name}'")

    def _duplicate_theme(self):
        if not self._selected_scheme:
            return
        name = self._selected_scheme["name"]
        copy = th.duplicate_scheme(self._settings, name)
        if not copy:
            return
        copy_name = copy["name"]
        st.save_custom_theme(copy)
        if copy_name not in self._custom_names:
            self._custom_names.append(copy_name)
        self._populate()
        self._sidebar.select_name(copy_name)
        self._save_wt()
        self._status.configure(text=f"✓  Duplicated as '{copy_name}'")

    def _rename_theme(self):
        if not self._selected_scheme:
            return
        name = self._selected_scheme["name"]
        if name in th.BUNDLED_NAMES:
            messagebox.showinfo("Built-in", "Built-in themes cannot be renamed.")
            return

        def do_rename(new_name: str):
            if not th.rename_scheme(self._settings, name, new_name):
                messagebox.showerror("Rename Failed",
                                     f"'{new_name}' already exists or is invalid.")
                return
            st.rename_custom_theme(name, new_name, self._selected_scheme)
            if name in self._custom_names:
                idx = self._custom_names.index(name)
                self._custom_names[idx] = new_name
            self._selected_scheme["name"] = new_name
            self._populate()
            self._sidebar.select_name(new_name)
            self._title_lbl.configure(text=new_name)
            self._save_wt()
            self._status.configure(text=f"✓  Renamed to '{new_name}'")

        dlg = RenameDialog(self, name, on_confirm=do_rename)
        dlg.grab_set()

    def _edit_in_quick(self):
        if self._selected_scheme:
            self._qt_pane.load_scheme(self._selected_scheme)

    # ── Background ────────────────────────────────────────────────────────────

    def _apply_background(self, config: dict, path_str: str):
        defaults = self._settings.setdefault("profiles", {}).setdefault("defaults", {})
        defaults.update(config)
        self._state["recent_bg"] = path_str
        if self._save_wt():
            self._status.configure(text="✓  Background applied — restart Windows Terminal")

    def _remove_background(self):
        th.remove_background(self._settings)
        self._state["recent_bg"] = None
        if self._save_wt():
            self._status.configure(text="✓  Background removed")

    # ── Import / Export ───────────────────────────────────────────────────────

    def _import_theme(self):
        path = filedialog.askopenfilename(
            title="Import Theme",
            filetypes=[("JSON Theme", "*.json"), ("All Files", "*.*")])
        if not path:
            return
        scheme, errors = th.import_scheme_file(Path(path))
        if errors:
            messagebox.showerror("Import Failed", "\n".join(errors))
            return
        name = scheme["name"]
        th.add_or_update_scheme(self._settings, scheme)
        st.save_custom_theme(scheme)
        if name not in self._custom_names:
            self._custom_names.append(name)
        self._populate()
        self._sidebar.select_name(name)
        self._save_wt()
        self._status.configure(text=f"✓  Imported '{name}'")

    def _export_theme(self):
        if not self._selected_scheme:
            messagebox.showinfo("No Theme", "Select a theme first.")
            return
        name = self._selected_scheme["name"]
        safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
        path = filedialog.asksaveasfilename(
            title="Export Theme", defaultextension=".json",
            initialfile=f"{safe}.json",
            filetypes=[("JSON Theme", "*.json")])
        if path and th.export_scheme(self._selected_scheme, Path(path)):
            self._status.configure(text=f"✓  Exported '{name}'")
        elif path:
            messagebox.showerror("Export Error", "Could not write file.")

    # ── Backups ───────────────────────────────────────────────────────────────

    def _open_backups(self):
        win = BackupWindow(self, self._settings_path, on_restore=self._on_restore)
        win.grab_set()

    def _on_restore(self):
        self._load_all()
        self._populate()
        self._status.configure(text="✓  Settings restored from backup")
