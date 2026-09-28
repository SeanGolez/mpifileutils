#!/usr/bin/env python3

import subprocess
import os
from tests import config

def run_local(*command):
    command = list(map(str, command))
    print(f"Running: {' '.join(command)}")

    result = subprocess.run(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True
    )
    
    print("--- COMMAND STDOUT START ---")
    print(result.stdout)
    print("---- COMMAND STDOUT END ----")

    return result

def run_distributed(*command):
    return run_local(*config.run_cmd, *command)

def create_empty_directories(*directories):
    for dirpath in directories:
        os.makedirs(dirpath, exist_ok=True)
    
def create_empty_files(*files):
    for filepath in files:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        open(filepath, 'w').close()
