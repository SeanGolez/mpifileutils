#!/usr/bin/env python3

import unittest
import random
import os
from tests import common, config

class TestDCHMOD(unittest.TestCase):
    """Tests for dchmod"""

    def setUp(self):
        # set up file tree to test on
        self.tmp_tree_base = os.path.join(config.test_dir, self.__class__.__name__, f"tmp_{self._testMethodName}")

        common.create_empty_directories(os.path.join(self.tmp_tree_base, "tmp0", "tmp1", "tmp2"))
        common.create_empty_files(os.path.join(self.tmp_tree_base, "tmp0", "tmp0_file"), os.path.join(self.tmp_tree_base, "tmp0", "tmp1", "tmp1_file"))

    def test_octal_mode(self):
        """Use octal mode to change permissions"""

        # run dchmod with a random valid octal mode between 700 - 777
        octal = "7" + str(random.randrange(0, 8)) + str(random.randrange(0, 8))
        dchmod_result = common.run_distributed("dchmod", "-v", "--mode", octal, self.tmp_tree_base)

        # CHECK: dchmod success
        self.assertEqual(dchmod_result.returncode, 0, msg=dchmod_result.stderr)

        # CHECK: all permissions were set correctly
        permissions_map = get_tree_permissions(self.tmp_tree_base)
        incorrect_permissions = [path for path, permission in permissions_map.items() if permission != octal]
        self.assertFalse(incorrect_permissions, msg=f"Permission not set on {incorrect_permissions}")

    def test_exclude(self):
        """Change permissions on all items except those whose path match regex"""

        # run dchmod with symbolic syntax equivalent to 761
        dchmod_result = common.run_distributed("dchmod", "--exclude", f".*{os.sep}tmp1{os.sep}.*", "--mode", "u+rwx,g+rw,g-x,o+x,o-rw", self.tmp_tree_base)

        # CHECK: dchmod success
        self.assertEqual(dchmod_result.returncode, 0, msg=dchmod_result.stderr)

        # CHECK: all permissions were set correctly
        permissions_map = get_tree_permissions(self.tmp_tree_base)
        incorrect_permissions = [path for path, permission in permissions_map.items()
            if (f"{os.sep}tmp1{os.sep}" in path and permission == "761") 
            or (f"{os.sep}tmp1{os.sep}" not in path and permission != "761")
        ]
        self.assertFalse(incorrect_permissions, msg=f"Permission incorrectly set on {incorrect_permissions}")

    def test_match(self):
        """Change permissions on items whose name match regex"""

        # run dchmod with symbolic syntax equivalent to 761
        dchmod_result = common.run_distributed("dchmod", "--name", "--match", ".*_file$", "--mode", "u+rwx,g+rw,g-x,o+x,o-rw", self.tmp_tree_base)

        # CHECK: dchmod success
        self.assertEqual(dchmod_result.returncode, 0, msg=dchmod_result.stderr)

        # CHECK: all permissions were set correctly
        permissions_map = get_tree_permissions(self.tmp_tree_base)
        incorrect_permissions = [path for path, permission in permissions_map.items()
            if (path.endswith("file") and permission != "761") 
            or (not path.endswith("file") and permission == "761")
        ]
        self.assertFalse(incorrect_permissions, msg=f"Permission incorrectly set on {incorrect_permissions}")

def get_tree_permissions(root_dir):
    permissions_map = dict()
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            fullpath = os.path.join(dirpath, dirname)
            permissions_map[fullpath] = f"{os.stat(fullpath).st_mode & 0o777:o}"

        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            permissions_map[fullpath] = f"{os.stat(fullpath).st_mode & 0o777:o}"

    return permissions_map

if __name__ == "__main__":
    unittest.main()
