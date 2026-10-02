#!/usr/bin/env python3

import unittest
import os
from tests import common, config

class TestDCMP(common.TestCase):
    """Tests for dcmp"""

    def setUp(self):
        # set up unique directory and output file information for this test
        self.src_dirpath = os.path.join(config.test_dir, self.__class__.__name__, f"src_{self._testMethodName}")
        self.dest_dirpath = os.path.join(config.test_dir, self.__class__.__name__, f"dest_{self._testMethodName}")
        self.output_filepath = os.path.join(config.test_dir, self.__class__.__name__, f"output_{self._testMethodName}")

        self.src_dirpath_tempdir_path = os.path.join(self.src_dirpath, "tempdir")
        self.src_dirpath_tempfile_path = os.path.join(self.src_dirpath, "tempfile")
        self.dest_dirpath_tempdir_path = os.path.join(self.dest_dirpath, "tempdir")
        self.dest_dirpath_tempfile_path = os.path.join(self.dest_dirpath, "tempfile")

    def test_expression_0(self):
        """check EXIST=ONLY_SRC"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath_tempdir_path, self.dest_dirpath_tempdir_path)
        common.create_empty_files(self.src_dirpath_tempfile_path)

        # run dcmp, output entry that exists only in source path
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"EXIST=ONLY_SRC:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile reported
        self.assertIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(self.src_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)
    
    def test_expression_1(self):
        """check EXIST=ONLY_DEST"""

        # set up directories/files to test on
        common.create_empty_directories(self.dest_dirpath_tempdir_path)
        common.create_empty_files(self.src_dirpath_tempfile_path, self.dest_dirpath_tempfile_path)

        # run dcmp, output entry that exists only in destination path
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"EXIST=ONLY_DEST:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile not reported
        self.assertNotIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile not reported
        self.assertNotIn(self.dest_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir is reported
        self.assertIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_2(self):
        """check EXIST=DIFFER"""

        # set up directories/files to test on
        common.create_empty_files(self.src_dirpath_tempfile_path)
        common.create_empty_directories(self.dest_dirpath_tempdir_path)

        # run dcmp, output entries that differ in existence
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"EXIST=DIFFER:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile is reported
        self.assertIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir is reported
        self.assertIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_3(self):
        """check EXIST=COMMON"""

        # set up directories/files to test on
        common.create_empty_directories(self.dest_dirpath_tempdir_path)
        common.create_empty_files(self.src_dirpath_tempfile_path, self.dest_dirpath_tempfile_path)

        # run dcmp, output entries that exist in both paths
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"EXIST=COMMON:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempfile is reported
        self.assertIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(self.dest_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_4(self):
        """check TYPE=DIFFER"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath_tempdir_path, self.dest_dirpath_tempdir_path, self.dest_dirpath_tempfile_path)
        common.create_empty_files(self.src_dirpath_tempfile_path)

        # run dcmp, output entries with different types
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"TYPE=DIFFER:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile is reported
        self.assertIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(self.src_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(self.dest_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_5(self):
        """check (EXIST=COMMON) && (TYPE=DIFFER)"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath_tempdir_path, self.dest_dirpath_tempdir_path, self.dest_dirpath_tempfile_path)
        common.create_empty_files(self.src_dirpath_tempfile_path)

        # run dcmp, output entries that exist in both but have different types
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"EXIST=COMMON@TYPE=DIFFER:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile is reported
        self.assertIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(self.src_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(self.dest_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_6(self):
        """check (TYPE=DIFFER) && (EXIST=COMMON)"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath_tempdir_path, self.dest_dirpath_tempdir_path, self.dest_dirpath_tempfile_path)
        common.create_empty_files(self.src_dirpath_tempfile_path)

        # run dcmp, output entries with different types that exist in both
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"TYPE=DIFFER@EXIST=COMMON:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile is reported
        self.assertIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(self.src_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(self.dest_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_7(self):
        """check (TYPE=DIFFER) && (EXIST=DIFFER)"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath_tempdir_path, self.dest_dirpath_tempdir_path, self.dest_dirpath_tempfile_path)
        common.create_empty_files(self.src_dirpath_tempfile_path)

        # run dcmp, output entries with different types AND differ in existence (none should match)
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"TYPE=DIFFER@EXIST=DIFFER:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile not reported
        self.assertNotIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(self.src_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile not reported
        self.assertNotIn(self.dest_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_8(self):
        """check (EXIST=DIFFER) && (TYPE=DIFFER)"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath_tempdir_path, self.dest_dirpath_tempdir_path, self.dest_dirpath_tempfile_path)
        common.create_empty_files(self.src_dirpath_tempfile_path)

        # run dcmp, output entries that differ in existence AND have different types (none should match)
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"EXIST=DIFFER@TYPE=DIFFER:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile not reported
        self.assertNotIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir not reported
        self.assertNotIn(self.src_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile not reported
        self.assertNotIn(self.dest_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempdir not reported
        self.assertNotIn(self.dest_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_expression_9(self):
        """check (TYPE=DIFFER) || (EXIST=DIFFER)"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath_tempdir_path, self.dest_dirpath_tempfile_path)
        common.create_empty_files(self.src_dirpath_tempfile_path)

        # run dcmp, output entries with different types OR differ in existence
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath, "-o", f"TYPE=DIFFER,EXIST=DIFFER:{self.output_filepath}")

        # run dwalk over output
        dwalk_result = common.run_distributed("dwalk", "--print", "--input", self.output_filepath)

        # CHECK: src/tempfile is reported
        self.assertIn(self.src_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: src/tempdir is reported
        self.assertIn(self.src_dirpath_tempdir_path, dwalk_result.stdout, msg=dwalk_result.stderr)

        # CHECK: dest/tempfile is reported
        self.assertIn(self.dest_dirpath_tempfile_path, dwalk_result.stdout, msg=dwalk_result.stderr)

    def test_extras_and_differences(self):
        """extras and diff comparison"""

        # set up directories/files to test on, extra file in src to check counting
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_empty_files(os.path.join(self.src_dirpath, "extrafile.txt"))

        # use dd to create a 100MB file
        self.run_local_successfully("dd", "if=/dev/zero", f"of={os.path.join(self.src_dirpath, 'tempfile')}", "bs=1M", "count=100")

        # copy the file to destination using dcp
        self.run_distributed_successfully("dcp", self.src_dirpath_tempfile_path, self.dest_dirpath)

        # run dcmp to check same contents
        dcmp_result = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath)

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
        with open(os.path.join(self.src_dirpath, 'tempfile'), "r+b") as file:
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
        dcmp_result2 = self.run_distributed_successfully("dcmp", self.src_dirpath, self.dest_dirpath)

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
