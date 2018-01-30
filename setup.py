import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os","binascii","sqlite3","contextlib","locale","tempfile","platform",
"subprocess","datetime","random","pandas", "jinja2", "weasyprint"], "excludes": ["numpy"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Gerador",
        version = "0.1",
        description = "Gerador de Autenticações Bancarias",
        options = {"build_exe": build_exe_options},
        executables = [Executable("gerador.py", base=base)])