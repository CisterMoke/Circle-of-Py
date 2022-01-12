import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {
    "packages": ["numpy", "pygame"],
    "include_files": [('config.ini', 'config.ini'), ('cards', 'cards')]
}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

target = Executable(
    script="main.py",
    base=base,
    target_name="circle",
    icon="snak.ico",
)

setup(
    name = "Circle of Py",
    version = "1.0.0",
    description = "A minimal playing card physics simulator.",
    options = {"build_exe": build_exe_options},
    executables = [target]
)