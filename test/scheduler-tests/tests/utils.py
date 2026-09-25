#!/usr/bin/env python3

import subprocess

def run(command):
    print(" ".join(command))

    result = subprocess.run(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True
    )

    print(result.stdout)

    return result
