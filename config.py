import os
import sys
import concurrent.futures as cf
from configparser import ConfigParser

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

cfg = ConfigParser()
cfg.read("config.ini")

DISPLAY = cfg["DISPLAY"]
ASPECT = (int(DISPLAY.get("width", "800")), int(DISPLAY.get("height", "600")))
FPS = int(DISPLAY.get("fps", "60"))
BGD = (0, 150, 0)
PROC_POOL = cf.ProcessPoolExecutor()
MENU_FONT = ("Calibri", 30)
