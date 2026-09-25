#!/usr/bin/env python3

import subprocess
import unittest
import shutil
import os
from tests import config
from tests import utils

# define global constants
DCMP = os.path.join(config.bin_dir, "dcmp")
DWALK = os.path.join(config.bin_dir, "dwalk")
SRC_DIR = os.path.join(config.tmp_dir, "src")
DEST_DIR = os.path.join(config.tmp_dir, "dest")
OUTPUT_FILE = os.path.join(config.tmp_dir, "output")

class TestDCMP(unittest.TestCase):
    """Tests for dcmp"""

    def test_expression_0(self):
        """check EXIST = ONLY_SRC"""

        # cleanup directories after test
        self.addCleanup(shutil.rmtree, SRC_DIR, ignore_errors=True)
        self.addCleanup(shutil.rmtree, DEST_DIR, ignore_errors=True)

        # set up directories to test on
        os.makedirs(os.path.join(SRC_DIR, "tempdir"), exist_ok=True)
        open(os.path.join(SRC_DIR, "tempfile"), 'w').close()
        os.makedirs(os.path.join(DEST_DIR, "tempdir"), exist_ok=True)

        # run dcmp, output entry that exists only in source path
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, SRC_DIR, DEST_DIR, "-o", f"EXIST=ONLY_SRC:{OUTPUT_FILE}"
            ]
        )
        
        # CHECK: dcmp success
        self.assertEqual(
            dcmp_result.returncode,
            0,
            msg=dcmp_result.stderr
        )
        
        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", OUTPUT_FILE
            ]
        )

        # CHECK: src/tempfile reported
        self.assertIn(
            os.path.join(SRC_DIR, "tempfile"),
            dwalk_result.stdout,
            msg=dwalk_result.stderr
        )

        # CHECK: src/tempdir not reported
        self.assertNotIn(
            os.path.join(SRC_DIR, "tempdir"),
            dwalk_result.stdout,
            msg=dwalk_result.stderr
        )

        # CHECK: dest/tempdir not reported
        self.assertNotIn(
            os.path.join(DEST_DIR, "tempdir"),
            dwalk_result.stdout,
            msg=dwalk_result.stderr
        )

if __name__ == "__main__":
    unittest.main()
