#!/usr/bin/env python3

import unittest
import os
from tests import common, config

class TestDWALK(common.TestCase):
    """Tests for dwalk"""

    def setUp(self): 
        # set up unique directory information for this test
        self.basepath = os.path.join(config.test_dir, self.__class__.__name__, self._testMethodName)
        self.file1 = os.path.join(self.basepath, "file1")
        self.file2 = os.path.join(self.basepath, "file2")
        self.file3 = os.path.join(self.basepath, "file3")
        self.file4 = os.path.join(self.basepath, "file4")
        self.file5 = os.path.join(self.basepath, "file5")

        common.create_empty_files(self.file1)
        for file, byte_size in {self.file2: "5M", self.file3: "20", self.file4: "15M", self.file5: "5M"}.items():
            self.run_local_successfully("dd", "if=/dev/urandom", f"of={file}", f"bs={byte_size}", "count=1")

        self.output_file = os.path.join(self.basepath, "output")

    def test_print_summary(self):
        """Print summary information of a directory"""

        # run dwalk
        dwalk_result = self.run_distributed_successfully("dwalk", "--print", self.basepath)

        # CHECK: all files printed
        for file in [self.basepath, self.file1, self.file2, self.file3, self.file4, self.file5]:
            self.assertIn(file, dwalk_result.stdout)

    def test_sort(self):
        """Sort by file size, then by name"""

        # run dwalk
        dwalk_result = self.run_distributed_successfully("dwalk", "-t", "-o", self.output_file, "--sort", "size,name", self.basepath)

        # get output
        with open(self.output_file) as file:
            lines = file.readlines()

        # CHECK: correct order is printed
        for idx, file in enumerate([self.file1, self.file3, self.basepath, self.file2, self.file5, self.file4]):
            self.assertIn(file, lines[idx])

    def test_distribution(self):
        """Print the file distribution for specified histogram based on the size field from the top level directory"""

        # run dwalk
        dwalk_result = self.run_distributed_successfully("dwalk", "--distribution", "size:0,20,10M", self.basepath)

        # CHECK: distribution output is correct
        self.assertRegex(dwalk_result.stdout, r"\[\s*0\.000\s+B\s+-\s*0\.000\s+B\s+\)\s+1")
        self.assertRegex(dwalk_result.stdout, r"\[\s*0\.000\s+B\s+-\s*20\.000\s+B\s+\)\s+1")
        self.assertRegex(dwalk_result.stdout, r"\[\s*20\.000\s+B\s+-\s*10\.000\s+MiB\s+\)\s+3")
        self.assertRegex(dwalk_result.stdout, r"\[\s*10\.000\s+MiB\s+-\s*MAX\s+\)\s+1")

if __name__ == "__main__":
    unittest.main()
