#!/usr/bin/env python3

import unittest
import random
import time
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

        # run dcp with sparse option
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 8388608, msg="Incorrect total written bytes in copied file.")

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

        # run dcp with sparse option 
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 8192, msg="Incorrect total written bytes in copied file.")

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

        # run dcp with sparse option
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 2097152, msg="Incorrect total written bytes in copied file.")

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

        # run dcp with sparse option
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 1048576, msg="Incorrect total written bytes in copied file.")

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

        # run dcp with sparse option
        self.run_distributed_successfully("dcp", "--sparse", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(os.path.join(self.dest_dirpath, "tempfile")), 8388608, msg="Incorrect total written bytes in copied file.")

    def test_symlink_copy(self):
        """Symlink copy"""
        
        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_random_files(os.path.join(self.src_dirpath, "tempfile"))

        # create a symlink to that file
        os.symlink(os.path.join(self.src_dirpath, "tempfile"), os.path.join(self.src_dirpath, "tempfile_symlink"))

        # run dcp
        self.run_distributed_successfully("dcp", os.path.join(self.src_dirpath, "tempfile_symlink"), self.dest_dirpath)

        # CHECK: symlink was preserved in dest
        self.assertTrue(os.path.islink(os.path.join(self.dest_dirpath, "tempfile_symlink")), msg="Copied file is not a symlink.")

    def test_symlink_dereference_copy(self):
        """Symlink copy with dereference"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_random_files(os.path.join(self.src_dirpath, "tempfile"))

        # create a symlink to that file
        os.symlink(os.path.join(self.src_dirpath, "tempfile"), os.path.join(self.src_dirpath, "tempfile_symlink"))

        # run dcp with dereference option
        self.run_distributed_successfully("dcp", "--dereference", os.path.join(self.src_dirpath, "tempfile_symlink"), self.dest_dirpath)

        # CHECK: symlink was dereferenced in dest
        self.assertFalse(os.path.islink(os.path.join(self.dest_dirpath, "tempfile_symlink")), msg="Copied file is a symlink.")

    def test_symlink_no_dereference_copy(self):
        """Symlink copy with no dereference, does not follow symlink"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_random_files(os.path.join(self.src_dirpath, "tempfile"))

        # create a symlink to that file
        os.symlink(os.path.join(self.src_dirpath, "tempfile"), os.path.join(self.src_dirpath, "tempfile_symlink"))

        # delete the file
        os.remove(os.path.join(self.src_dirpath, "tempfile"))

        # run dcp with no dereference option
        self.run_distributed_successfully("dcp", "--no-dereference", os.path.join(self.src_dirpath, "tempfile_symlink"), self.dest_dirpath)

        # CHECK: symlink was preserved in dest
        self.assertTrue(os.path.islink(os.path.join(self.dest_dirpath, "tempfile_symlink")), msg="Copied file is not a symlink.")

        # run dcp, should fail
        self.run_distributed_with_failure("dcp", os.path.join(self.src_dirpath, "tempfile_symlink"), self.dest_dirpath)

    def test_xattr_copy(self):
        """Copy user xattrs"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_empty_files(os.path.join(self.src_dirpath, "tempfile"))

        # Skip test if user xattrs not allowed
        if any(not user_xattrs_allowed(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination does not permit user xattrs.")
        
        # Set an attribute
        os.setxattr(os.path.join(self.src_dirpath, "tempfile"), b"user.test", b"test")

        # run dcp
        self.run_distributed_successfully("dcp", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: user xattr is preserved in dest
        self.assertIn("user.test", os.listxattr(os.path.join(self.dest_dirpath, "tempfile")), msg="User xattr not preserved in copied file.")

    def test_no_xattr_copy(self):
        """Copy none of user xattrs"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_empty_files(os.path.join(self.src_dirpath, "tempfile"))

        # Skip test if user xattrs not allowed
        if any(not user_xattrs_allowed(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination does not permit user xattrs.")
        
        # Set an attribute
        os.setxattr(os.path.join(self.src_dirpath, "tempfile"), b"user.test", b"test")

        # run dcp, with no xattrs copy
        self.run_distributed_successfully("dcp", "--xattrs", "none", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: user xattr is not copied in dest
        self.assertNotIn("user.test", os.listxattr(os.path.join(self.dest_dirpath, "tempfile")), msg="User xattr preserved in copied file.")

    def test_preserve_copy(self):
        """Copy file while preserving permissions, groups, and timestamps"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_empty_files(os.path.join(self.src_dirpath, "tempfile"))

        # set permissions to a random valid octal mode between 700 - 777
        octal = "7" + str(random.randrange(0, 8)) + str(random.randrange(0, 8))
        os.chmod(os.path.join(self.src_dirpath, "tempfile"), int(octal, 8))

        # wait 1 second for timestamps to change if preserve is not working
        time.sleep(1)

        # run dcp, with preserve option
        self.run_distributed_successfully("dcp", "--preserve", os.path.join(self.src_dirpath, "tempfile"), self.dest_dirpath)

        # CHECK: permissions, group, and timestamps are the same
        src_stat = os.stat(os.path.join(self.src_dirpath, "tempfile"))
        dest_stat = os.stat(os.path.join(self.dest_dirpath, "tempfile"))
        self.assertEqual(f"{dest_stat.st_mode & 0o777:o}", octal, msg="Permissions not preserved in copied file.")
        self.assertEqual(dest_stat.st_gid, src_stat.st_gid, msg="Group ID not preserved in copied file.")
        self.assertEqual(dest_stat.st_atime_ns, src_stat.st_atime_ns, msg="Access timestamp not preserved in copied file.")
        self.assertEqual(dest_stat.st_mtime_ns, src_stat.st_mtime_ns, msg="Modification timestamp not preserved in copied file.")

def is_in_lustre(path):
    if common.run_local("lfs", "df", path).returncode == 0:
        return True
    return False

def user_xattrs_allowed(path): 
    if "nouser_xattr" not in common.run_local("grep", common.mount_basename(path), "/proc/mounts").stdout:
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
