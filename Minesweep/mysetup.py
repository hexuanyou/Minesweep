from distutils.core import setup
import py2exe


options = {"py2exe":{"bundle_files": 3}}
setup(options=options, zipfile=None,
      name = "MspAssist", windows=["./hw/minesweeper/minesweep.py"],
      data_files=[("help", ["./hw/minesweeper/help_for_sweep.txt"])])
