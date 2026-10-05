#!/usr/bin/env python3

import unittest
import random
import os
from tests import common, config

class TestDCP(common.TestCase):
    """Tests for dcp"""

    def setUp(self):
        # set up unique directory and output file information for this test
        self.src_dirpath = os.path.join(config.test_dir, self.__class__.__name__, f"src_{self._testMethodName}")
        self.dest_dirpath = os.path.join(config.test_dir, self.__class__.__name__, f"dest_{self._testMethodName}")

    def test_copy_0(self):
        """Copy file with no holes"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")

        # create file with no holes
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=4M", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=4M", "seek=1", "count=1")

        # run dcp 
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 8388608)

    def test_copy_1(self):
        """Copy file with a front 4K hole"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")

        # create file with a front 4K hole
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=4K", "seek=1", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=4k", "seek=2", "count=1")

        # run dcp 
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 8192)

    def test_copy_2(self):
        """Copy file with a middle 1G hole"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")

        # create file with a middle 1G hole
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=1M", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=1M", "seek=1025", "count=1")

        # run dcp 
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 2097152)

    def test_copy_3(self):
        """Copy file with an end 1G hole"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")
        
        # create file with an end 1G hole
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=1M", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=1M", "seek=1025", "count=0")

        # run dcp 
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 1048576)

    def test_copy_4(self):
        """Copy file with a front 4M, middle 1G, end 1G hole"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")
        
        # create file with a front 4M, middle 1G, end 1G hole
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=4M", "seek=1", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=4M", "seek=258", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={os.path.join(self.src_dirpath, "tempfile")}", "bs=4M", "seek=515", "count=0")

        # run dcp 
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 8388608)
 
def is_in_lustre(path):
    if common.run_local("lfs", "df", path).returncode == 0:
        return True
    return False

def get_total_written_bytes(filepath):
    file_size = os.path.getsize(filepath)
    written_bytes = 0
    offset = 0

    with open(filepath, "rb") as file:
        fd = file.fileno()

        while offset < file_size:
            try:
                data_offset = os.lseek(fd, offset, os.SEEK_DATA)
            except OSError:
                break

            try:
                hole_offset = os.lseek(fd, data_offset, os.SEEK_HOLE)
            except OSError:
                hole_offset = file_size

            written_bytes += hole_offset - data_offset
            offset = hole_offset

    return written_bytes

if __name__ == "__main__":
    unittest.main()
