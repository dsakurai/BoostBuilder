#!/usr/bin/env python3

from sys import argv
import glob
import subprocess
import re
from pathlib import Path

boost_lib_dir = argv[1]

for filename in glob.glob(boost_lib_dir + '/libboost_*.dylib'):
    # Fix the name
    result = subprocess.run(["install_name_tool", "-id", filename, filename])
    if result.returncode != 0:
        raise Exception("failed to fix library name in a .dylib file")

    # `@loader_path/.` is apparently already installed by boost, but `@loader_path` instead
    # makes linking work at runtime on macOS...
    result = subprocess.run(["install_name_tool", "-add_rpath", r"@loader_path", filename])
    if result.returncode != 0:
        raise Exception("install_name_tool failed to add rpath for file " + filename)

    # Fix the library dependency within boost
    analysis_result = subprocess.run(["otool", "-L", filename], capture_output=True, text=True)
    if analysis_result.returncode != 0:
        raise Exception("otool failed to analyze path references in a .dylib file")

    for name in analysis_result.stdout.split('\n'):
        matches = re.search(r'(bin\.v2.*dylib)\s', name)
        if matches:
            path = matches.group(1)
            path = Path(path)
            if not path.exists():
                raise Exception("Failed to parse otool output into a file name" + str(path))
            name = path.name
            install_result = subprocess.run(["install_name_tool", "-change", str(path), r"@rpath/" + name, filename])
            if install_result.returncode != 0:
                raise Exception("Failed to fix library name with install_name_tool")

