"""ui.py — T3RMIN4L main UI (customtkinter)."""

import json
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional
import customtkinter as ctk

import themes as th
import quicktheme as qt
import background as bg
import backup as bk

# ── Theme ────────────────────────────────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PALETTE = {
    "bg":        "#05050d",
    "surface":   "#0d0d1a",
    "card":      "#111122",
    "border":    "#1e1e3a",
    "accent":    "#00ffcc",
    "accent2":   "#bd93f9",
    "accent3":   "#ff5555",
    "text":      "#e8e8f0",
    "muted":     "#6666aa",
    "input_bg":  "#0a0a18",
}

FONT_MONO  = ("Consolas", 12)
FONT_TITLE = ("Consolas", 20, "bold")
FONT_SUB   = ("Consolas", 10)
FONT_BTN   = ("Consolas", 11, "bold")
FONT_SMALL = ("Consolas", 9)


# ── Helper widgets ────────────────────────────────────────────────────────────

class GlowLabel(ctk.CTkLabel):
    def __init__(self, master, text, color=None, font=None, **kw):
        super().__init__(master, text=text,
                         text_color=color or PALETTE["accent"],
                         font=font or FONT_MONO, **kw)


class DividerLine(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, height=1, fg_color=PALETTE["border"], **kw)


class NeonButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, color=None, width=140, **kw):
        c = color or PALETTE["accent"]
        super().__init__(
            master, text=text, command=command, width=width,
            fg_color="transparent", border_width=1, border_color=c,
            text_color=c, hover_color=c + "22",
            font=FONT_BTN, corner_radius=4, **kw
        )


class SmallBtn(ctk.CTkButton):
    def __init__(self, master, text, command=None, color=None, **kw):
        c = color or PALETTE["muted"]
        super().__init__(
            master, text=text, command=command, width=80, height=26,
            fg_color="transparent", border_width=1, border_color=c,
            text_color=c, hover_color=c + "22",
            font=FONT_SMALL, corner_radius=3, **kw
        )


# ── Color swatch strip ────────────────────────────────────────────────────────

class SchemePreview(ctk.CTkFrame):
    """Horizontal strip of colour swatches for a scheme."""
    COLOR_FIELDS = [
        "black", "red", "green", "yellow",
        "blue", "purple", "cyan", "white",
        "brightBlack", "brightRed", "brightGreen", "brightYellow",
        "brightBlue", "brightPurple", "brightCyan", "brightWhite",
    ]

    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._swatches: list[tk.Canvas] = []
        for _ in self.COLOR_FIELDS:
            c = tk.Canvas(self, width=18, height=18, bd=0, highlightthickness=0,
                          bg=PALETTE["bg"])
            c.pack(side="left", padx=1)
            self._swatches.append(c)

    def update_scheme(self, scheme: dict):
        for i, field in enumerate(self.COLOR_FIELDS):
            color = scheme.get(field, "#222233")
            try:
                self._swatches[i].configure(bg=color)
                self._swatches[i].delete("all")
                self._swatches[i].create_rectangle(0, 0, 18, 18, fill=color, outline="")
            except Exception:
                pass


# ── Terminal mock preview ─────────────────────────────────────────────────────

class TerminalPreview(ctk.CTkFrame):
    """Fake terminal window showing the colour scheme live."""

    SAMPLE_LINES = [
        ("$ ", "accent", "git status", "text"),
        ("On branch ", "muted", "main", "green"),
        ("nothing to commit, working tree clean", "white", "", ""),
        ("$ ", "accent", "ls -la", "text"),
        ("drwxr-xr-x  6 ", "blue", "user  staff", "cyan"),
        ("$ ", "accent", "echo 'T3RMIN4L'", "text"),
        ("T3RMIN4L", "accent2", "", ""),
        ("$ ", "accent", "_", "accent"),
    ]

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=PALETTE["card"],
                         border_width=1, border_color=PALETTE["border"],
                         corner_radius=6, **kw)
        # Title bar
        bar = ctk.CTkFrame(self, fg_color=PALETTE["surface"], height=28, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        for col in ("#ff5555", "#f1fa8c", "#50fa7b"):
            dot = ctk.CTkFrame(bar, width=10, height=10, fg_color=col,
                               corner_radius=5)
            dot.pack(side="left", padx=(6, 2), pady=9)
        ctk.CTkLabel(bar, text="T3RMIN4L — Preview",
                     text_color=PALETTE["muted"], font=FONT_SMALL).pack(side="left", padx=8)
        # Text area
        self._text = tk.Text(self, bg=PALETTE["bg"], fg=PALETTE["text"],
                             font=("Consolas", 11), bd=0, highlightthickness=0,
                             insertbackground=PALETTE["accent"], state="disabled",
                             wrap="none", padx=10, pady=8, cursor="arrow",
                             selectbackground=PALETTE["border"])
        self._text.pack(fill="both", expand=True, padx=0, pady=0)
        self._scheme: dict = {}
        self._render_sample()

    def _tag_color(self, name: str, fallback: str) -> str:
        if not self._scheme:
            return PALETTE.get(name, fallback)
        color_map = {
            "accent":   self._scheme.get("cursorColor",  PALETTE["accent"]),
            "accent2":  self._scheme.get("purple",       PALETTE["accent2"]),
            "text":     self._scheme.get("foreground",   PALETTE["text"]),
            "muted":    self._scheme.get("brightBlack",  PALETTE["muted"]),
            "green":    self._scheme.get("green",        "#50fa7b"),
            "cyan":     self._scheme.get("cyan",         "#8be9fd"),
            "blue":     self._scheme.get("blue",         "#6272a4"),
            "white":    self._scheme.get("white",        "#f8f8f2"),
        }
        return color_map.get(name, fallback)

    def _render_sample(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        bg_color = self._scheme.get("background", PALETTE["bg"]) if self._scheme else PALETTE["bg"]
        self._text.configure(bg=bg_color)
        for parts in self.SAMPLE_LINES:
            if len(parts) == 4:
                t1, c1, t2, c2 = parts
                col1 = self._tag_color(c1, PALETTE["text"])
                col2 = self._tag_color(c2, PALETTE["text"])
                tag1, tag2 = f"c_{c1}_{id(t1)}", f"c_{c2}_{id(t2)}"
                self._text.tag_configure(tag1, foreground=col1)
                self._text.tag_configure(tag2, foreground=col2)
                self._text.insert("end", t1, tag1)
                if t2:
                    self._text.insert("end", t2, tag2)
                self._text.insert("end", "\n")
        self._text.configure(state="disabled")

    def apply_scheme(self, scheme: dict):
        self._scheme = scheme
        self._render_sample()


# ── Quick Theme editor pane ───────────────────────────────────────────────────

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

        self._editor = tk.Text(body, bg=PALETTE["input_bg"], fg=PALETTE["text"],
                               font=FONT_MONO, bd=0, highlightthickness=1,
                               highlightcolor=PALETTE["border"],
                               highlightbackground=PALETTE["border"],
                               insertbackground=PALETTE["accent"],
                               wrap="none", padx=8, pady=6, undo=True)
        self._editor.pack(fill="both", expand=True)
        self._editor.insert("1.0", qt.EXAMPLE_THEME)
        self._editor.bind("<KeyRelease>", self._on_key)

        self._error_label = ctk.CTkLabel(body, text="", text_color=PALETTE["accent3"],
                                          font=FONT_SMALL, anchor="w", wraplength=340)
        self._error_label.pack(fill="x", pady=(4, 0))

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x", pady=(6, 0))
        SmallBtn(btn_row, "Preview", command=self._preview,
                 color=PALETTE["accent2"]).pack(side="left", padx=(0, 6))
        SmallBtn(btn_row, "Clear", command=self._clear,
                 color=PALETTE["muted"]).pack(side="left", padx=(0, 6))

        name_row = ctk.CTkFrame(body, fg_color="transparent")
        name_row.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(name_row, text="Theme name:", text_color=PALETTE["muted"],
                     font=FONT_SMALL).pack(side="left", padx=(0, 6))
        self._name_var = ctk.StringVar(value="My Custom Theme")
        ctk.CTkEntry(name_row, textvariable=self._name_var, width=180,
                     fg_color=PALETTE["input_bg"], border_color=PALETTE["border"],
                     text_color=PALETTE["text"], font=FONT_MONO).pack(side="left")
        NeonButton(name_row, "Save Theme", command=self._save,
                   color=PALETTE["accent"], width=110).pack(side="right")

    def _on_key(self, _event=None):
        # Live preview on edit
        self._preview()

    def _preview(self):
        text = self._editor.get("1.0", "end")
        parsed, errors = qt.parse_quick_theme(text)
        if errors:
            self._error_label.configure(text="⚠  " + errors[0])
        else:
            self._error_label.configure(text="")
        scheme = qt.to_wt_scheme("__preview__", parsed)
        self._on_preview(scheme)

    def _clear(self):
        self._editor.delete("1.0", "end")

    def _save(self):
        text = self._editor.get("1.0", "end")
        parsed, errors = qt.parse_quick_theme(text)
        if errors:
            self._error_label.configure(text="⚠  " + " | ".join(errors[:2]))
            return
        name = self._name_var.get().strip() or "My Custom Theme"
        scheme = qt.to_wt_scheme(name, parsed)
        overrides = qt.quick_theme_to_profile_overrides(parsed)
        self._on_save(scheme, overrides)
        self._error_label.configure(text=f"✓  Saved as '{name}'")

    def load_scheme(self, scheme: dict):
        """Populate editor from an existing scheme dict."""
        lines = []
        color_fields = [
            "background", "foreground", "cursorColor", "selectionBackground",
            "black", "red", "green", "yellow", "blue", "purple", "cyan", "white",
            "brightBlack", "brightRed", "brightGreen", "brightYellow",
            "brightBlue", "brightPurple", "brightCyan", "brightWhite",
        ]
        alias_rev = {v: k for k, v in qt.ALIASES.items()}
        for f in color_fields:
            if f in scheme:
                display = alias_rev.get(f, f)
                lines.append(f"{display}: {scheme[f]};")
        self._editor.delete("1.0", "end")
        self._editor.insert("1.0", "\n".join(lines))
        self._name_var.set(scheme.get("name", "Edited Theme"))


# ── Background pane ───────────────────────────────────────────────────────────

class BackgroundPane(ctk.CTkFrame):
    def __init__(self, master, on_apply, on_remove, **kw):
        super().__init__(master, fg_color=PALETTE["card"],
                         border_width=1, border_color=PALETTE["border"],
                         corner_radius=6, **kw)
        self._on_apply  = on_apply
        self._on_remove = on_remove
        self._image_path: Optional[Path] = None

        hdr = ctk.CTkFrame(self, fg_color=PALETTE["surface"], height=32, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        GlowLabel(hdr, "🖼  BACKGROUND", font=("Consolas", 11, "bold"),
                  color=PALETTE["accent"]).pack(side="left", padx=12, pady=6)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=10)

        # File chooser
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self._path_var = ctk.StringVar(value="No image selected")
        ctk.CTkLabel(row, textvariable=self._path_var, text_color=PALETTE["muted"],
                     font=FONT_SMALL, anchor="w").pack(side="left", fill="x", expand=True)
        SmallBtn(row, "Browse…", command=self._browse,
                 color=PALETTE["accent"]).pack(side="right")

        self._warn_label = ctk.CTkLabel(body, text="", text_color="#f1fa8c",
                                         font=FONT_SMALL, anchor="w", wraplength=340)
        self._warn_label.pack(fill="x", pady=(4, 0))

        DividerLine(body).pack(fill="x", pady=8)

        # Opacity
        def _lbl(text):
            return ctk.CTkLabel(body, text=text, text_color=PALETTE["muted"],
                                font=FONT_SMALL, anchor="w")

        _lbl("Opacity").pack(fill="x")
        self._opacity = ctk.CTkSlider(body, from_=0, to=1, number_of_steps=20,
                                       progress_color=PALETTE["accent"],
                                       button_color=PALETTE["accent"])
        self._opacity.set(0.5)
        self._opacity.pack(fill="x", pady=(2, 8))

        # Stretch
        _lbl("Stretch Mode").pack(fill="x")
        self._stretch = ctk.CTkOptionMenu(body, values=bg.STRETCH_MODES,
                                           fg_color=PALETTE["input_bg"],
                                           button_color=PALETTE["border"],
                                           text_color=PALETTE["text"], font=FONT_SMALL)
        self._stretch.set("uniformToFill")
        self._stretch.pack(fill="x", pady=(2, 8))

        # Alignment
        _lbl("Alignment").pack(fill="x")
        self._align = ctk.CTkOptionMenu(body, values=bg.ALIGNMENT_OPTIONS,
                                         fg_color=PALETTE["input_bg"],
                                         button_color=PALETTE["border"],
                                         text_color=PALETTE["text"], font=FONT_SMALL)
        self._align.set("center")
        self._align.pack(fill="x", pady=(2, 8))

        # Toggles
        tog_row = ctk.CTkFrame(body, fg_color="transparent")
        tog_row.pack(fill="x", pady=4)
        self._blur_var   = ctk.BooleanVar(value=False)
        self._acrylic_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(tog_row, text="Blur", variable=self._blur_var,
                        text_color=PALETTE["text"], font=FONT_SMALL,
                        checkmark_color=PALETTE["accent"],
                        border_color=PALETTE["border"]).pack(side="left", padx=(0, 16))
        ctk.CTkCheckBox(tog_row, text="Acrylic", variable=self._acrylic_var,
                        text_color=PALETTE["text"], font=FONT_SMALL,
                        checkmark_color=PALETTE["accent"],
                        border_color=PALETTE["border"]).pack(side="left")

        DividerLine(body).pack(fill="x", pady=8)
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")
        NeonButton(btn_row, "Apply Background", command=self._apply,
                   color=PALETTE["accent"], width=160).pack(side="left")
        SmallBtn(btn_row, "Remove", command=self._remove,
                 color=PALETTE["accent3"]).pack(side="right")

    def _browse(self):
        filetypes = [("Images", "*.png *.jpg *.jpeg *.gif"), ("All Files", "*.*")]
        path = filedialog.askopenfilename(title="Select Background Image",
                                          filetypes=filetypes)
        if path:
            self._image_path = Path(path)
            self._path_var.set(self._image_path.name)
            if bg.is_gif(self._image_path):
                self._warn_label.configure(
                    text="⚠  Windows Terminal doesn't support animated GIFs.\n"
                         "   The first frame will be extracted automatically.")
            else:
                self._warn_label.configure(text="")

    def _apply(self):
        if not self._image_path:
            messagebox.showwarning("No Image", "Please select an image first.")
            return
        valid, msg = bg.validate_image(self._image_path)
        if not valid:
            messagebox.showerror("Invalid Image", msg)
            return
        result = bg.build_background_config(
            self._image_path,
            opacity=self._opacity.get(),
            stretch=self._stretch.get(),
            alignment=self._align.get(),
            blur=self._blur_var.get(),
            acrylic=self._acrylic_var.get(),
        )
        if result["warning"]:
            self._warn_label.configure(text=result["warning"])
        self._on_apply(result["config"])

    def _remove(self):
        self._on_remove()


# ── Backup pane ───────────────────────────────────────────────────────────────

class BackupPane(ctk.CTkToplevel):
    def __init__(self, master, settings_path: Optional[Path], on_restore, **kw):
        super().__init__(master, **kw)
        self.title("T3RMIN4L — Backups")
        self.geometry("520x420")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["bg"])
        self._settings_path = settings_path
        self._on_restore = on_restore

        GlowLabel(self, "BACKUP MANAGER", font=("Consolas", 14, "bold")).pack(pady=(20, 4))
        DividerLine(self).pack(fill="x", padx=20, pady=8)

        self._list = ctk.CTkScrollableFrame(self, fg_color=PALETTE["surface"],
                                             corner_radius=4, height=260)
        self._list.pack(fill="x", padx=20)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=14)
        NeonButton(btn_row, "Create Backup Now", command=self._create,
                   color=PALETTE["accent"]).pack(side="left", padx=8)
        NeonButton(btn_row, "Close", command=self.destroy,
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
            row = ctk.CTkFrame(self._list, fg_color=PALETTE["card"],
                               corner_radius=4)
            row.pack(fill="x", pady=3, padx=4)
            ctk.CTkLabel(row, text=s["date"], text_color=PALETTE["text"],
                         font=FONT_SMALL).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=f"{s['size_kb']} KB", text_color=PALETTE["muted"],
                         font=FONT_SMALL).pack(side="left", padx=6)
            path = s["path"]
            SmallBtn(row, "Restore", command=lambda p=path: self._restore(p),
                     color=PALETTE["accent"]).pack(side="right", padx=8, pady=4)

    def _create(self):
        if not self._settings_path:
            return
        dest = bk.create_backup(self._settings_path)
        if dest:
            messagebox.showinfo("Backup Created", f"Saved:\n{dest.name}")
            self._refresh()

    def _restore(self, path: Path):
        if messagebox.askyesno("Restore Backup",
                               f"Restore '{path.name}'?\nThis will overwrite your current settings."):
            ok = bk.restore_backup(path, self._settings_path)
            if ok:
                messagebox.showinfo("Restored", "Settings restored. Restart Windows Terminal.")
                self._on_restore()
            else:
                messagebox.showerror("Error", "Could not restore backup.")


# ── Theme list sidebar ────────────────────────────────────────────────────────

class ThemeSidebar(ctk.CTkFrame):
    def __init__(self, master, on_select, **kw):
        super().__init__(master, fg_color=PALETTE["surface"], width=220,
                         corner_radius=0, **kw)
        self.pack_propagate(False)
        self._on_select = on_select
        self._selected: Optional[str] = None
        self._buttons: dict[str, ctk.CTkButton] = {}

        hdr = ctk.CTkFrame(self, fg_color=PALETTE["bg"], height=48, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        GlowLabel(hdr, "T3RMIN4L", font=FONT_TITLE,
                  color=PALETTE["accent"]).pack(side="left", padx=16, pady=12)

        DividerLine(self).pack(fill="x")

        self._section("INSTALLED")
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True)

        DividerLine(self).pack(fill="x")
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", pady=8)
        SmallBtn(nav, "⟳ Backups", command=lambda: master.event_generate("<<OpenBackups>>"),
                 color=PALETTE["muted"]).pack(padx=10, pady=2, fill="x")
        SmallBtn(nav, "↑ Import", command=lambda: master.event_generate("<<ImportTheme>>"),
                 color=PALETTE["muted"]).pack(padx=10, pady=2, fill="x")
        SmallBtn(nav, "↓ Export", command=lambda: master.event_generate("<<ExportTheme>>"),
                 color=PALETTE["muted"]).pack(padx=10, pady=2, fill="x")

    def _section(self, label):
        ctk.CTkLabel(self, text=label, text_color=PALETTE["muted"],
                     font=("Consolas", 9, "bold"), anchor="w").pack(
            fill="x", padx=14, pady=(10, 2))

    def populate(self, scheme_names: list[str]):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._buttons.clear()
        for name in scheme_names:
            btn = ctk.CTkButton(
                self._scroll, text=name, anchor="w",
                fg_color="transparent", hover_color=PALETTE["border"],
                text_color=PALETTE["text"], font=FONT_SMALL,
                corner_radius=3, height=32,
                command=lambda n=name: self._select(n)
            )
            btn.pack(fill="x", padx=6, pady=1)
            self._buttons[name] = btn

    def _select(self, name: str):
        if self._selected and self._selected in self._buttons:
            self._buttons[self._selected].configure(
                fg_color="transparent", text_color=PALETTE["text"])
        self._selected = name
        if name in self._buttons:
            self._buttons[name].configure(
                fg_color=PALETTE["border"], text_color=PALETTE["accent"])
        self._on_select(name)

    def get_selected(self) -> Optional[str]:
        return self._selected


# ── Main App Window ───────────────────────────────────────────────────────────

class T3RMINAL(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("T3RMIN4L — Windows Terminal Theme Manager")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=PALETTE["bg"])

        self._settings_path: Optional[Path] = th.find_settings_path()
        self._settings: dict = {}
        self._all_schemes: list[dict] = []
        self._selected_scheme: Optional[dict] = None

        self._load_settings()
        self._build_ui()
        self._populate_sidebar()

        # Events from sidebar buttons
        self.bind("<<OpenBackups>>", lambda _: self._open_backups())
        self.bind("<<ImportTheme>>", lambda _: self._import_theme())
        self.bind("<<ExportTheme>>", lambda _: self._export_theme())

    # ── Settings I/O ─────────────────────────────────────────────────────────

    def _load_settings(self):
        if self._settings_path:
            try:
                self._settings = th.load_settings(self._settings_path)
            except Exception:
                self._settings = {}
        # Merge bundled themes (only if not already present)
        existing_names = {s.get("name") for s in th.list_schemes(self._settings)}
        for bt in th.BUNDLED_THEMES:
            if bt["name"] not in existing_names:
                th.add_or_update_scheme(self._settings, bt)
        self._all_schemes = th.list_schemes(self._settings)

    def _save(self):
        if not self._settings_path:
            messagebox.showwarning("Not Found",
                                   "Windows Terminal settings.json not found.\n"
                                   "Make sure Windows Terminal is installed.")
            return False
        ok = th.save_settings(self._settings_path, self._settings)
        if not ok:
            messagebox.showerror("Save Error", "Could not write settings.json.")
        return ok

    # ── UI Build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Sidebar
        self._sidebar = ThemeSidebar(self, on_select=self._on_theme_select)
        self._sidebar.pack(side="left", fill="y")

        # Main area
        main = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        main.pack(side="left", fill="both", expand=True)

        # Top bar with scheme actions
        top = ctk.CTkFrame(main, fg_color=PALETTE["surface"], height=50, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        self._scheme_title = ctk.CTkLabel(top, text="Select a theme →",
                                           text_color=PALETTE["accent"],
                                           font=("Consolas", 13, "bold"))
        self._scheme_title.pack(side="left", padx=16)

        self._apply_btn = NeonButton(top, "▶  Apply Theme",
                                      command=self._apply_theme,
                                      color=PALETTE["accent"], width=150)
        self._apply_btn.pack(side="right", padx=8)
        SmallBtn(top, "✕ Remove", command=self._remove_theme,
                 color=PALETTE["accent3"]).pack(side="right", padx=4)
        SmallBtn(top, "Edit →", command=self._edit_in_quick,
                 color=PALETTE["accent2"]).pack(side="right", padx=4)

        # Content columns
        cols = ctk.CTkFrame(main, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=10, pady=10)
        cols.columnconfigure(0, weight=3)
        cols.columnconfigure(1, weight=2)
        cols.rowconfigure(0, weight=2)
        cols.rowconfigure(1, weight=2)

        # Terminal preview (top-left)
        self._preview = TerminalPreview(cols)
        self._preview.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))

        # Swatch strip below preview
        swatch_card = ctk.CTkFrame(cols, fg_color=PALETTE["card"],
                                    border_width=1, border_color=PALETTE["border"],
                                    corner_radius=6, height=50)
        swatch_card.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        swatch_card.pack_propagate(False)
        sw_inner = ctk.CTkFrame(swatch_card, fg_color="transparent")
        sw_inner.pack(expand=True)
        ctk.CTkLabel(sw_inner, text="COLORS  ", text_color=PALETTE["muted"],
                     font=FONT_SMALL).pack(side="left")
        self._swatches = SchemePreview(sw_inner)
        self._swatches.pack(side="left")

        # Quick Theme pane (top-right)
        self._qt_pane = QuickThemePane(cols,
                                        on_preview=self._on_quick_preview,
                                        on_save=self._on_quick_save)
        self._qt_pane.grid(row=0, column=1, rowspan=2, sticky="nsew")

        # Background pane (bottom-left) — in a tab strip
        bg_outer = ctk.CTkFrame(main, fg_color="transparent")
        bg_outer.pack(fill="x", padx=10, pady=(0, 10))

        # Inline status bar
        self._status = ctk.CTkLabel(bg_outer,
                                     text=self._status_text(),
                                     text_color=PALETTE["muted"],
                                     font=FONT_SMALL, anchor="w")
        self._status.pack(fill="x", padx=4)

        # Background pane toggle
        self._bg_visible = False
        self._bg_toggle = SmallBtn(bg_outer, "🖼  Show Background Settings",
                                    command=self._toggle_bg,
                                    color=PALETTE["accent"])
        self._bg_toggle.pack(anchor="w", pady=4)

        self._bg_pane = BackgroundPane(bg_outer,
                                        on_apply=self._apply_background,
                                        on_remove=self._remove_background)

    def _status_text(self) -> str:
        if self._settings_path:
            return f"✓  {self._settings_path}"
        return "⚠  Windows Terminal settings.json not found — changes won't be saved"

    def _toggle_bg(self):
        if self._bg_visible:
            self._bg_pane.pack_forget()
            self._bg_toggle.configure(text="🖼  Show Background Settings")
        else:
            self._bg_pane.pack(fill="x", pady=(4, 0))
            self._bg_toggle.configure(text="✕  Hide Background Settings")
        self._bg_visible = not self._bg_visible

    # ── Populate ──────────────────────────────────────────────────────────────

    def _populate_sidebar(self):
        names = [s.get("name", "?") for s in self._all_schemes]
        self._sidebar.populate(names)

    # ── Theme selection ───────────────────────────────────────────────────────

    def _on_theme_select(self, name: str):
        scheme = th.get_scheme_by_name(self._settings, name)
        if not scheme:
            return
        self._selected_scheme = scheme
        self._scheme_title.configure(text=name)
        self._preview.apply_scheme(scheme)
        self._swatches.update_scheme(scheme)

    def _on_quick_preview(self, scheme: dict):
        self._preview.apply_scheme(scheme)
        self._swatches.update_scheme(scheme)

    def _on_quick_save(self, scheme: dict, overrides: dict):
        th.add_or_update_scheme(self._settings, scheme)
        self._all_schemes = th.list_schemes(self._settings)
        self._populate_sidebar()
        if self._save():
            self._status.configure(text=f"✓  Saved theme '{scheme['name']}'")

    # ── Apply / Remove ────────────────────────────────────────────────────────

    def _apply_theme(self):
        if not self._selected_scheme:
            messagebox.showinfo("No Theme", "Select a theme first.")
            return
        name = self._selected_scheme.get("name", "")
        th.apply_scheme_to_default_profile(self._settings, name)
        if self._save():
            self._status.configure(
                text=f"✓  Applied '{name}' — restart Windows Terminal to see changes")

    def _remove_theme(self):
        if not self._selected_scheme:
            return
        name = self._selected_scheme.get("name", "")
        if name in [t["name"] for t in th.BUNDLED_THEMES]:
            messagebox.showinfo("Built-in Theme", "Cannot remove built-in themes.")
            return
        if messagebox.askyesno("Remove Theme", f"Remove '{name}'?"):
            th.remove_scheme(self._settings, name)
            self._all_schemes = th.list_schemes(self._settings)
            self._selected_scheme = None
            self._scheme_title.configure(text="Select a theme →")
            self._populate_sidebar()
            self._save()

    def _edit_in_quick(self):
        if not self._selected_scheme:
            return
        self._qt_pane.load_scheme(self._selected_scheme)

    # ── Background ────────────────────────────────────────────────────────────

    def _apply_background(self, config: dict):
        defaults = self._settings.setdefault("profiles", {}).setdefault("defaults", {})
        defaults.update(config)
        if self._save():
            self._status.configure(text="✓  Background applied — restart Windows Terminal")

    def _remove_background(self):
        th.remove_background(self._settings)
        if self._save():
            self._status.configure(text="✓  Background removed")

    # ── Import / Export ───────────────────────────────────────────────────────

    def _import_theme(self):
        path = filedialog.askopenfilename(
            title="Import Theme",
            filetypes=[("JSON Theme", "*.json"), ("All Files", "*.*")]
        )
        if not path:
            return
        scheme = th.import_scheme_file(Path(path))
        if not scheme:
            messagebox.showerror("Import Error",
                                 "File is not a valid Windows Terminal color scheme.")
            return
        th.add_or_update_scheme(self._settings, scheme)
        self._all_schemes = th.list_schemes(self._settings)
        self._populate_sidebar()
        if self._save():
            self._status.configure(text=f"✓  Imported '{scheme.get('name', '?')}'")

    def _export_theme(self):
        if not self._selected_scheme:
            messagebox.showinfo("No Theme", "Select a theme first.")
            return
        name = self._selected_scheme.get("name", "theme")
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
        path = filedialog.asksaveasfilename(
            title="Export Theme",
            defaultextension=".json",
            initialfile=f"{safe_name}.json",
            filetypes=[("JSON Theme", "*.json")]
        )
        if not path:
            return
        ok = th.export_scheme(self._selected_scheme, Path(path))
        if ok:
            self._status.configure(text=f"✓  Exported '{name}'")
        else:
            messagebox.showerror("Export Error", "Could not write file.")

    # ── Backups ───────────────────────────────────────────────────────────────

    def _open_backups(self):
        win = BackupPane(self, self._settings_path,
                         on_restore=self._on_restore)
        win.grab_set()

    def _on_restore(self):
        self._load_settings()
        self._populate_sidebar()
        self._status.configure(text="✓  Settings restored from backup")
