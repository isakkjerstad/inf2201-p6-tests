#!/usr/bin/python3

'''
Written by: Isak Kjerstad.
Purpose: standalone test for general shell functions.
Date: 24.05.22
'''

import unittest
import config as cfg
from sim_comms import run_commands, validate_output, construct_multi_command

class TestShellFunctions(unittest.TestCase):
    ''' Short tests of all the different file system shell commands. '''

    def setUp(self):
        cfg.compile()

    def test_mkdir(self):
        ''' Testing with main focus on the mkdir command. '''

        # Construct a set of mkdir commands to run at once.
        multiLineInput = construct_multi_command(["mkdir myDir",
                                                 "cd myDir",
                                                 "mkdir dirOne",
                                                 "mkdir dirTwo",
                                                 "mkdir dirThree",
                                                 "ls"])

        # Retrieve output mainly from the last ls command.
        shellOutput = run_commands([multiLineInput])

        # Expecting no errors and to find the given directories.
        errorCode = validate_output(shellOutput, ["dirOne",
                                                    "dirTwo",
                                                    "dirThree",
                                                    "..", "."])

        # Should cause no errors if all directories exist.
        msg = "Error with mkdir: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # The directory should still exist in root.
        shellOutput = run_commands(["ls"])
        errorCode = validate_output(shellOutput, [".", "..", "myDir"])
        msg = "Error with mkdir, not persistent: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)
    
    def test_cd_relative(self):
        ''' Testing with main focus on the cd command, with relative paths. '''

        # Create a 5-level directory containing three directories.
        multiLineInput = construct_multi_command(["mkdir one",
                                                    "cd one",
                                                    "mkdir two",
                                                    "cd two",
                                                    "mkdir three",
                                                    "cd three",
                                                    "mkdir four",
                                                    "cd four",
                                                    "mkdir five",
                                                    "cd five",
                                                    "mkdir findMe1",
                                                    "mkdir findMe2",
                                                    "mkdir findMe3"])

        # Create directory three with no errors.
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, [])
        msg = "Error with mkdir or cd: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # Test cd with relative paths.
        multiLineInput = construct_multi_command(["cd one",
                                                    "cd two",
                                                    "cd three",
                                                    "cd four",
                                                    "cd five",
                                                    "ls"])
        
        # Expect to find all the "findMe" directories.
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, ["findMe1", "findMe2", "findMe3"])
        msg = "Error with cd on relative paths: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

    def test_cd_absolute(self):
        ''' Testing with main focus on the cd command, with absolute paths. '''

        # Create a 5-level directory containing three directories.
        multiLineInput = construct_multi_command(["mkdir one",
                                                    "cd one",
                                                    "mkdir two",
                                                    "cd two",
                                                    "mkdir three",
                                                    "cd three",
                                                    "mkdir four",
                                                    "cd four",
                                                    "mkdir five",
                                                    "cd five",
                                                    "mkdir findMe1",
                                                    "mkdir findMe2",
                                                    "mkdir findMe3"])

        # Create directory three with no errors.
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, [])
        msg = "Error with mkdir or cd: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # Test cd with absolute paths.
        multiLineInput = construct_multi_command(["cd /one/two/three/four/five", "ls"])
        
        # Expect to find all the "findMe" directories.
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, ["findMe1", "findMe2", "findMe3"])
        msg = "Error with cd on absolute paths: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)
    
    def test_rmdir(self):
        ''' Testing with main focus on the rmdir command. '''

        # Create and verify a directory to later remove.
        multiLineInput = construct_multi_command(["mkdir remove_me", "ls"])
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, ["remove_me"])
        msg = "Error creating directory: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # Check that removed directory does not exists.
        multiLineInput = construct_multi_command(["rmdir remove_me", "ls"])
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, ["remove_me"])
        msg = "Error removed directory still exists: {}".format(errorCode)
        self.assertEqual(errorCode, -1, msg)

    def test_ls(self):
        ''' Testing with main focus on the ls command. '''

        # Create three directories, and list everything in root.
        multiLineInput = construct_multi_command(["mkdir one", "mkdir two", "mkdir three", "ls"])
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, [".", "..", "one", "two", "three"])

        msg = "Error ls has unexpected behaviour: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

    def test_pwd(self):
        ''' Testing with main focus on the pwd command. '''

        multiLineInput = construct_multi_command(["mkdir mnt",
                                                    "cd mnt",
                                                    "mkdir users",
                                                    "cd users",
                                                    "mkdir ikj023",
                                                    "cd ikj023",
                                                    "mkdir Documents",
                                                    "mkdir Desktop",
                                                    "mkdir Downloads"])

        # Create a directory structure for pwd.
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, [])
        msg = "Error could not create dir. structure: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

        # Check that pwd returns the current working directory.
        multiLineInput = construct_multi_command(["cd mnt/users/ikj023/Documents", "pwd"])
        shellOutput = run_commands([multiLineInput])
        errorCode = validate_output(shellOutput, ["/mnt/users/ikj023/Documents"])
        msg = "Error pwd does not work: {}".format(errorCode)
        self.assertEqual(errorCode, 0, msg)

    def test_cat(self):
        ''' Testing with main focus on the cat command. '''

        # Create three files in the root directory.
        run_commands(["cat file1", "cat file2", "cat file3"])

        # Verify that cat creates the files above.
        output = run_commands(["ls"])
        error = validate_output(output, ["file1", "file2", "file3"])
        msg = "Error cat does not work: {}".format(error)
        self.assertEqual(error, 0, msg)

    def test_more(self):
        ''' Testing with main focus on the more command. '''

        # Create a file and open it afterwards.
        run_commands(["cat myFile123"])
        output = run_commands(["more myFile123"])

        # The file should contain it's own name.
        error = validate_output(output, ["myFile123"])
        msg = "Error more does not work: {}".format(error)
        self.assertEqual(error, 0, msg)

    def test_ln(self):
        ''' Testing with main focus on the ln command. '''

        # Create one directory and one file in root.
        run_commands(["mkdir myDir", "cat myFile123"])

        # Attempt to link a file, and check for any errors.
        multicmd = construct_multi_command(["cd myDir", "ln myLink /myFile123"])
        output = run_commands([multicmd])
        error = validate_output(output, [])
        msg = "Error link does not work: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Validate that the link is working.
        multicmd = construct_multi_command(["cd myDir", "more myLink"])
        output = run_commands([multicmd])
        error = validate_output(output, ["myFile123"])
        msg = "Error invalid link data: {}".format(error)
        self.assertEqual(error, 0, msg)

    def test_rm(self):
        ''' Testing with main focus on the rm command. '''

        # Create a file to delete.
        run_commands(["cat myFile"])

        # Attempt to delete the file, check if it still exists.
        multicmd = construct_multi_command(["rm myFile", "ls"])
        output = run_commands([multicmd])
        error = validate_output(output, ["myFile"])
        msg = "Error file not deleted: {}".format(error)
        self.assertEqual(error, -1, msg)

    def test_stat(self):
        ''' Testing with main focus on the stat command. '''
        
        # Create one file and one directory.
        run_commands(["cat file", "mkdir folder", "ln link1 file", "ln link2 file"])

        # Expect file with two links and five bytes in size.
        output = run_commands(["stat file"])
        error = validate_output(output, ["1", "2", "5"])
        msg = "Error stat not working: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Expect directory with two entries.
        output = run_commands(["stat folder"])
        error = validate_output(output, ["2", "0", "40"])
        msg = "Error stat not working: {}".format(error)
        self.assertEqual(error, 0, msg)

    def tearDown(self):
        cfg.cleanup()

if __name__ == '__main__':
    unittest.main()