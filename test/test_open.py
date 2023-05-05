#!/usr/bin/python3

'''
Written by: Isak Kjerstad.
Purpose: standalone test for fs_open.
Date: 24.05.22
'''

import unittest
import config as cfg
from sim_comms import run_commands, validate_output

class TestOpen(unittest.TestCase):
    ''' Test fs_open functionality with different shell commands. '''

    def setUp(self):
        cfg.compile()

    def test_ls_simple(self):
        '''
        Simple test of ls on a new file system.
        Used to verify successful compiling, and as a
        baseline example for all the other tests.
        '''

        # Run ls with a new file system.
        shellOutput = run_commands(["ls"])

        # No errors should occour, and dots should be present.
        errorCode = validate_output(shellOutput, [".", ".."])

        # Generate an error message.
        msg = "File system error: {}".format(errorCode)

        # Raise error if any of the commands has failed.
        self.assertEqual(errorCode, 0, msg)

    def test_truncate(self):
        '''
        Test open with truncate on a file.
        '''

        # Create file to later truncate.
        shellOutput = run_commands(["cat trunc_file"])
        errorCode = validate_output(shellOutput, [])
        msg = "Error creating file: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # Try to truncate existing file.
        shellOutput = run_commands(["cat trunc_file"])
        errorCode = validate_output(shellOutput, [])
        msg = "Error truncating file: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # Verify content of truncated file.
        shellOutput = run_commands(["more trunc_file"])
        errorCode = validate_output(shellOutput, ["trunc_file"])
        msg = "Error invalid truncated file: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

    def test_ls_advanced(self):
        '''
        Stress test ls by making a lot of files. This
        also indirectly tests open, cat and close.
        '''

        catCommands = []        # Commands to run.
        expectedFiles = []      # Expected ls result.

        # Use more than one 512 byte block in root.
        for num in range(3, 50+1):
            catCommands.append("cat myFile_" + str(num))
            expectedFiles.append("myFile_" + str(num))

        # Create the files with cat.
        shellOutput = run_commands(catCommands)

        # Creating the files should not cause any errors.
        errorCode = validate_output(shellOutput, [])
        msg = "Error creating files: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # List directory with newly created files.
        shellOutput = run_commands(["ls"])

        # All created files should be present.
        errorCode = validate_output(shellOutput, expectedFiles)
        msg = "Error listing files: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # Try to open some of the files. All of them should be found.
        shellOutput = run_commands(["more myFile_3", "more myFile_24", "more myFile_50"])
        errorCode = validate_output(shellOutput, ["myFile_3", "myFile_24", "myFile_50"])
        msg = "Invalid or broken files: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

    def test_open_invalid_name(self):
        '''
        Attempt to open a non-existing file.
        Check for correct behaviour.
        '''

        # Attempt to read a non-existing file.
        shellOutput = run_commands(["more non_existing"])
        errorCode = validate_output(shellOutput, [])

        # Should cause a file does not exist error.
        msg = "File system did not handle error: {}".format(errorCode)
        self.assertEqual(errorCode, -5, msg)

    def test_too_long_name_open(self):
        '''
        Attempt to open a file with a too
        long name. Checks error handeling.
        '''

        # Attempt to open a file with a too long name.
        shellOutput = run_commands(["more my_name_is_too_long"])
        errorCode = validate_output(shellOutput, [])

        # Should cause a name too long error.
        msg = "File system did not handle error: {}".format(errorCode)
        self.assertEqual(errorCode, -4, msg)

    def test_too_long_name_create(self):
        '''
        Attempt to create a file with a too
        long name. Checks error handeling.
        '''
        
        # Attempt to create a file with a too long name.
        shellOutput = run_commands(["cat my_name_is_too_long"])
        errorCode = validate_output(shellOutput, [])

        # Should cause a name too long error.
        msg = "File system did not handle error: {}".format(errorCode)
        self.assertEqual(errorCode, -4, msg)

    def tearDown(self):
        cfg.cleanup()

if __name__ == '__main__':
    unittest.main()