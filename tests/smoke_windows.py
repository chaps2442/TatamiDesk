"""Test rapide des appels Windows (lance par GitHub Actions sur un serveur Windows)."""
import os
import sys
import runpy
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
here = os.path.dirname(os.path.abspath(__file__))
m = runpy.run_path(os.path.join(here, "..", "tatamidesk.pyw"), run_name="smoke")

from PySide6.QtWidgets import QApplication  # noqa: E402
app = QApplication(sys.argv)
ok = True


def check(name, cond, detail=""):
    global ok
    print(("OK   " if cond else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    ok = ok and bool(cond)


notepad = os.path.join(os.environ["WINDIR"], "System32", "notepad.exe")
ic = m["win_file_icon"](notepad)
check("icone d'un .exe via le shell", ic is not None and not ic.isNull())

ic2 = m["icon_from_file"](notepad, 0)
check("icone extraite d'un .exe (PrivateExtractIcons)", ic2 is not None and not ic2.isNull())

tmp = tempfile.mkdtemp()
url = os.path.join(tmp, "Jeu.url")
with open(url, "w", encoding="utf-8") as f:
    f.write(f"[InternetShortcut]\nURL=steam://rungameid/1\nIconFile={notepad}\nIconIndex=0\n")
ic3 = m["win_url_icon"](url)
check("icone lue dans un raccourci .url", ic3 is not None and not ic3.isNull())

check("pywin32 disponible pour le menu Windows", m["ShellMenu"].available())
try:
    import win32gui
    from win32com.shell import shell, shellcon
    folder_path, name = os.path.split(url)
    desktop = shell.SHGetDesktopFolder()
    _, pidl_f, _ = desktop.ParseDisplayName(0, None, folder_path)
    folder = desktop.BindToObject(pidl_f, None, shell.IID_IShellFolder)
    _, pidl_i, _ = folder.ParseDisplayName(0, None, name)
    cm = folder.GetUIObjectOf(0, [pidl_i], shell.IID_IContextMenu, 0)
    hmenu = win32gui.CreatePopupMenu()
    cm.QueryContextMenu(hmenu, 0, 1, 0x6FFF, shellcon.CMF_NORMAL)
    n = win32gui.GetMenuItemCount(hmenu)
    check("menu contextuel Windows construit", n > 3, f"{n} entrees")
    win32gui.DestroyMenu(hmenu)
    hwnd = m["ShellMenu"]._window()
    check("fenetre du menu Windows creee", bool(hwnd))
except Exception as ex:
    check("menu contextuel Windows construit", False, repr(ex))

try:
    m["desktop_windows"]()
    m["desktop_icons_visible"]()
    check("lecture de l'etat des icones du bureau", True)
except Exception as ex:
    check("lecture de l'etat des icones du bureau", False, repr(ex))

for key in ("recycle", "computer"):
    sic = m["special_icon"](key)
    check(f"icone speciale {key}", sic is not None and not sic.isNull())

print("RESULTAT :", "tout est bon" if ok else "des erreurs")
sys.exit(0 if ok else 1)
