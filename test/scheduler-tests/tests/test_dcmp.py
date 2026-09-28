#!/usr/bin/env python3

import subprocess
import unittest
import shutil
import os
from tests import config, utils

# define global constants
DCMP = os.path.join(config.bin_dir, "dcmp")
DCP = os.path.join(config.bin_dir, "dcp")
DWALK = os.path.join(config.bin_dir, "dwalk")

class TestDCMP(unittest.TestCase):
    """Tests for dcmp"""

    def test_expression_0(self):
        """check EXIST=ONLY_SRC"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_0")
        dest_dirpath = os.path.join(config.test_dir, "dest_0")
        output_filepath = os.path.join(config.test_dir, "output_0")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)

        # run dcmp, output entry that exists only in source path
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"EXIST=ONLY_SRC:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile reported
        self.assertIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(os.path.join(src_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)
    
    def test_expression_1(self):
        """check EXIST=ONLY_DEST"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_1")
        dest_dirpath = os.path.join(config.test_dir, "dest_1")
        output_filepath = os.path.join(config.test_dir, "output_1")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(dest_dirpath, "tempfile"), 'w').close()

        # run dcmp, output entry that exists only in destination path
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"EXIST=ONLY_DEST:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile not reported
        self.assertNotIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir is reported
        self.assertIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_2(self):
        """check EXIST=DIFFER"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_2")
        dest_dirpath = os.path.join(config.test_dir, "dest_2")
        output_filepath = os.path.join(config.test_dir, "output_2")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)

        # run dcmp, output entries that differ in existence
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"EXIST=DIFFER:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile is reported
        self.assertIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir is reported
        self.assertIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_3(self):
        """check EXIST=COMMON"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_3")
        dest_dirpath = os.path.join(config.test_dir, "dest_3")
        output_filepath = os.path.join(config.test_dir, "output_3")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(dest_dirpath, "tempfile"), 'w').close()

        # run dcmp, output entries that exist in both paths
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"EXIST=COMMON:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: dest/tempdir not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempfile is reported
        self.assertIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(os.path.join(dest_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_4(self):
        """check TYPE=DIFFER"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_4")
        dest_dirpath = os.path.join(config.test_dir, "dest_4")
        output_filepath = os.path.join(config.test_dir, "output_4")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)
        os.makedirs(os.path.join(dest_dirpath, "tempfile"), exist_ok=True)

        # run dcmp, output entries with different types
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"TYPE=DIFFER:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile is reported
        self.assertIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(os.path.join(src_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(os.path.join(dest_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_5(self):
        """check (EXIST=COMMON) && (TYPE=DIFFER)"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_5")
        dest_dirpath = os.path.join(config.test_dir, "dest_5")
        output_filepath = os.path.join(config.test_dir, "output_5")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)
        os.makedirs(os.path.join(dest_dirpath, "tempfile"), exist_ok=True)

        # run dcmp, output entries that exist in both but have different types
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"EXIST=COMMON@TYPE=DIFFER:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile is reported
        self.assertIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(os.path.join(src_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(os.path.join(dest_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_6(self):
        """check (TYPE=DIFFER) && (EXIST=COMMON)"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_6")
        dest_dirpath = os.path.join(config.test_dir, "dest_6")
        output_filepath = os.path.join(config.test_dir, "output_6")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)
        os.makedirs(os.path.join(dest_dirpath, "tempfile"), exist_ok=True)

        # run dcmp, output entries with different types that exist in both
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"TYPE=DIFFER@EXIST=COMMON:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile is reported
        self.assertIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(os.path.join(src_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(os.path.join(dest_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_7(self):
        """check (TYPE=DIFFER) && (EXIST=DIFFER)"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_7")
        dest_dirpath = os.path.join(config.test_dir, "dest_7")
        output_filepath = os.path.join(config.test_dir, "output_7")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)
        os.makedirs(os.path.join(dest_dirpath, "tempfile"), exist_ok=True)

        # run dcmp, output entries with different types AND differ in existence (none should match)
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"TYPE=DIFFER@EXIST=DIFFER:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile not reported (exists in both, so fails EXIST=DIFFER)
        self.assertNotIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(os.path.join(src_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_8(self):
        """check (EXIST=DIFFER) && (TYPE=DIFFER)"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_8")
        dest_dirpath = os.path.join(config.test_dir, "dest_8")
        output_filepath = os.path.join(config.test_dir, "output_8")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempdir"), exist_ok=True)
        os.makedirs(os.path.join(dest_dirpath, "tempfile"), exist_ok=True)

        # run dcmp, output entries that differ in existence AND have different types (none should match)
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"EXIST=DIFFER@TYPE=DIFFER:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile not reported
        self.assertNotIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(os.path.join(src_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(os.path.join(dest_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_9(self):
        """check (TYPE=DIFFER) || (EXIST=DIFFER)"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_9")
        dest_dirpath = os.path.join(config.test_dir, "dest_9")
        output_filepath = os.path.join(config.test_dir, "output_9")

        # set up directories/files to test on
        os.makedirs(os.path.join(src_dirpath, "tempdir"), exist_ok=True)
        open(os.path.join(src_dirpath, "tempfile"), 'w').close()
        os.makedirs(os.path.join(dest_dirpath, "tempfile"), exist_ok=True)

        # run dcmp, output entries with different types OR differ in existence
        dcmp_result = utils.run(
            config.run_cmd + [
                DCMP, src_dirpath, dest_dirpath, "-o", f"TYPE=DIFFER,EXIST=DIFFER:{output_filepath}"
            ]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # run dwalk over output
        dwalk_result = utils.run(
            config.run_cmd + [
                DWALK, "--print", "--input", output_filepath
            ]
        )

        # CHECK: src/tempfile is reported (type differs)
        self.assertIn(os.path.join(src_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir is reported (exists only in src)
        self.assertIn(os.path.join(src_dirpath, "tempdir"), dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported (type differs)
        self.assertIn(os.path.join(dest_dirpath, "tempfile"), dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_extras_and_differences(self):
        """extras and diff comparison"""

        # set up unique directories for this test
        src_dirpath = os.path.join(config.test_dir, "src_10")
        dest_dirpath = os.path.join(config.test_dir, "dest_10")

        # set up directories/files to test on
        os.makedirs(src_dirpath, exist_ok=True)
        os.makedirs(dest_dirpath, exist_ok=True)

        # create an extra file in src to check counting
        open(os.path.join(src_dirpath, "extrafile.txt"), 'w').close()

        # use dd to create a 100MB file
        dd_create = utils.run(
            ["dd", "if=/dev/zero", f"of={os.path.join(src_dirpath, 'tmptest10')}", "bs=1M", "count=100"]
        )
        # CHECK: dd success
        self.assertEqual(dd_create.returncode, 0, msg=dd_create.stderr)

        # copy the file to destination using dcp
        dcp_copy = utils.run(
            config.run_cmd + [DCP, os.path.join(src_dirpath, "tmptest10"), dest_dirpath]
        )
        # CHECK: dcp success
        self.assertEqual(dcp_copy.returncode, 0, msg=dcp_copy.stderr)

        # run dcmp to check same contents
        dcmp_result = utils.run(
            config.run_cmd + [DCMP, src_dirpath, dest_dirpath]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result.returncode, 0, msg=dcmp_result.stderr)

        # parse dcmp output to verify counts
        output_lines = dcmp_result.stdout.strip().split('\n')

        # Should find that 2 files have same content and 1 extra exists only in src
        found_same = False
        found_extras = False

        for line in output_lines:
            # Check for: "Number of items that exist in both directories and have the same content: 2 (Src: 2 Dest: 2)"
            if 'same content' in line.lower() and '(Src: 2 Dest: 2)' in line:
                found_same = True
            # Check for: "Number of items that exist only in one directory: N/A (Src: 1 Dest: 0)"
            if 'exist only in one directory' in line.lower() and '(Src: 1 Dest: 0)' in line:
                found_extras = True

        # CHECK: found matching files
        self.assertTrue(found_same, msg=f"Did not find expected 2 files with same content in output:\n{dcmp_result.stdout}")

        # CHECK: found extra file in source
        self.assertTrue(found_extras, msg=f"Did not find expected 1 extra file in src in output:\n{dcmp_result.stdout}")

        # now modify byte 0 of the source file to value 57 (ASCII '9')
        with open(os.path.join(src_dirpath, 'tmptest10'), "r+b") as file:
            file.seek(0)
            file.write(b"\x39")
            file.flush()

            file.seek(0)
            modified_byte = file.read(1)

        # CHECK: byte modify success
        self.assertEqual(
            modified_byte,
            b"\x39",
            msg="The first byte was not modified correctly",
        )

        # run dcmp again to check for differences
        dcmp_result2 = utils.run(
            config.run_cmd + [DCMP, src_dirpath, dest_dirpath]
        )

        # CHECK: dcmp success
        self.assertEqual(dcmp_result2.returncode, 0, msg=dcmp_result2.stderr)

        # parse dcmp output to verify it detected the difference
        output_lines2 = dcmp_result2.stdout.strip().split('\n')

        # Should find that 1 file has different content
        found_diff = False

        for line in output_lines2:
            # Check for: "Number of items that exist in both directories and have different contents: 1 (Src: 1 Dest: 1)"
            if 'different contents' in line.lower() and '(Src: 1 Dest: 1)' in line:
                found_diff = True

        # CHECK: found files with different content
        self.assertTrue(found_diff, msg=f"Did not find expected 1 file with different content in output:\n{dcmp_result2.stdout}")

if __name__ == "__main__":
    unittest.main()
