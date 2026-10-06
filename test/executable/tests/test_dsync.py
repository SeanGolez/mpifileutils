#!/usr/bin/env python3

import unittest
import os
from tests import common, config, dcp_dsync_common_tests

class TestDSYNC(dcp_dsync_common_tests.CommonTests):
    """Tests for dsync"""

    def setUp(self):
        # set up unique directory and output file information for this test
        super().setUp()

        # for common tests
        self.cp_cmd = "dsync"

if __name__ == "__main__":
    unittest.main()