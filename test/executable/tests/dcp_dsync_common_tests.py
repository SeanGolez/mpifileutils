#!/usr/bin/env python3

import os
from tests import common, config

class CommonTests(common.TestCase):
    # Child setUp() requires self.cp_cmd to be defined

    def setUp(self):
        # set up unique directory and output file information for this test
        self.src_dirpath = os.path.join(config.test_dir, self.__class__.__name__, f"src_{self._testMethodName}")
        self.dest_dirpath = os.path.join(config.test_dir, self.__class__.__name__, f"dest_{self._testMethodName}")
        self.src_tempfilepath = os.path.join(self.src_dirpath, "tempfile")
        self.src_tempfilepath_symlink = os.path.join(self.src_dirpath, "tempfile_symlink")
        self.dest_tempfilepath = os.path.join(self.dest_dirpath, "tempfile")
        self.dest_tempfilepath_symlink = os.path.join(self.dest_dirpath, "tempfile_symlink")

    def test_copy_0(self):
        """Copy file with no holes"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")

        # create file with no holes
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=4M", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=4M", "seek=1", "count=1")

        # run self.cp_cmd with sparse option
        self.run_distributed_successfully(self.cp_cmd, "--sparse", self.src_tempfilepath, self.dest_tempfilepath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(self.dest_tempfilepath), 8388608, msg="Incorrect total written bytes in copied file.")

    def test_copy_1(self):
        """Copy file with a front 4K hole"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")

        # create file with a front 4K hole
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=4K", "seek=1", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=4k", "seek=2", "count=1")

        # run self.cp_cmd with sparse option 
        self.run_distributed_successfully(self.cp_cmd, "--sparse", self.src_tempfilepath, self.dest_tempfilepath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(self.dest_tempfilepath), 8192, msg="Incorrect total written bytes in copied file.")

    def test_copy_2(self):
        """Copy file with a middle 1G hole"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")

        # create file with a middle 1G hole
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=1M", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=1M", "seek=1025", "count=1")

        # run self.cp_cmd with sparse option
        self.run_distributed_successfully(self.cp_cmd, "--sparse", self.src_tempfilepath, self.dest_tempfilepath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(self.dest_tempfilepath), 2097152, msg="Incorrect total written bytes in copied file.")

    def test_copy_3(self):
        """Copy file with an end 1G hole"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")
        
        # create file with an end 1G hole
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=1M", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=1M", "seek=1025", "count=0")

        # run self.cp_cmd with sparse option
        self.run_distributed_successfully(self.cp_cmd, "--sparse", self.src_tempfilepath, self.dest_tempfilepath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(self.dest_tempfilepath), 1048576, msg="Incorrect total written bytes in copied file.")

    def test_copy_4(self):
        """Copy file with a front 4M, middle 1G, end 1G hole"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)

        # Skip test on Lustre filesystem
        if any(is_in_lustre(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination is on Lustre.")
        
        # create file with a front 4M, middle 1G, end 1G hole
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=4M", "seek=1", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=4M", "seek=258", "count=1")
        self.run_local_successfully("dd", "if=/dev/urandom", f"of={self.src_tempfilepath}", "bs=4M", "seek=515", "count=0")

        # run self.cp_cmd with sparse option
        self.run_distributed_successfully(self.cp_cmd, "--sparse", self.src_tempfilepath, self.dest_tempfilepath)

        # CHECK: total written bytes is correct
        self.assertEqual(get_total_written_bytes(self.dest_tempfilepath), 8388608, msg="Incorrect total written bytes in copied file.")

    def test_symlink_copy(self):
        """Symlink copy"""
        
        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_random_files(self.src_tempfilepath)

        # create a symlink to that file
        os.symlink(self.src_tempfilepath, self.src_tempfilepath_symlink)

        # run self.cp_cmd
        self.run_distributed_successfully(self.cp_cmd, self.src_tempfilepath_symlink, self.dest_tempfilepath_symlink)

        # CHECK: symlink was preserved in dest
        self.assertTrue(os.path.islink(self.dest_tempfilepath_symlink), msg="Copied file is not a symlink.")

    def test_symlink_dereference_copy(self):
        """Symlink copy with dereference"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_random_files(self.src_tempfilepath)

        # create a symlink to that file
        os.symlink(self.src_tempfilepath, self.src_tempfilepath_symlink)

        # run self.cp_cmd with dereference option
        self.run_distributed_successfully(self.cp_cmd, "--dereference", self.src_tempfilepath_symlink, self.dest_tempfilepath_symlink)

        # CHECK: symlink was dereferenced in dest
        self.assertFalse(os.path.islink(self.dest_tempfilepath_symlink), msg="Copied file is a symlink.")

    def test_symlink_no_dereference_copy(self):
        """Symlink copy with no dereference, does not follow symlink"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_random_files(self.src_tempfilepath)

        # create a symlink to that file
        os.symlink(self.src_tempfilepath, self.src_tempfilepath_symlink)

        # delete the file
        os.remove(self.src_tempfilepath)

        # run self.cp_cmd with no dereference option
        self.run_distributed_successfully(self.cp_cmd, "--no-dereference", self.src_tempfilepath_symlink, self.dest_tempfilepath_symlink)

        # CHECK: symlink was preserved in dest
        self.assertTrue(os.path.islink(self.dest_tempfilepath_symlink), msg="Copied file is not a symlink.")

        # run self.cp_cmd, should fail
        self.run_distributed_with_failure(self.cp_cmd, self.src_tempfilepath_symlink, self.dest_tempfilepath_symlink)

    def test_xattr_copy(self):
        """Copy user xattrs"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_empty_files(self.src_tempfilepath)

        # Skip test if user xattrs not allowed
        if any(not user_xattrs_allowed(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination does not permit user xattrs.")
        
        # Set an attribute
        os.setxattr(self.src_tempfilepath, b"user.test", b"test")

        # run self.cp_cmd
        self.run_distributed_successfully(self.cp_cmd, self.src_tempfilepath, self.dest_tempfilepath)

        # CHECK: user xattr is preserved in dest
        self.assertIn("user.test", os.listxattr(self.dest_tempfilepath), msg="User xattr not preserved in copied file.")

    def test_no_xattr_copy(self):
        """Copy none of user xattrs"""

        # set up directories/files to test on
        common.create_empty_directories(self.src_dirpath, self.dest_dirpath)
        common.create_empty_files(self.src_tempfilepath)

        # Skip test if user xattrs not allowed
        if any(not user_xattrs_allowed(path) for path in (self.src_dirpath, self.dest_dirpath)):
            self.skipTest("Source or destination does not permit user xattrs.")
        
        # Set an attribute
        os.setxattr(self.src_tempfilepath, b"user.test", b"test")

        # run self.cp_cmd, with no xattrs copy
        self.run_distributed_successfully(self.cp_cmd, "--xattrs", "none", self.src_tempfilepath, self.dest_tempfilepath)

        # CHECK: user xattr is not copied in dest
        self.assertNotIn("user.test", os.listxattr(self.dest_tempfilepath), msg="User xattr preserved in copied file.")

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
