#!/usr/bin/python3

'''
Written by: Isak Kjerstad.
Purpose: standalone advanced file system test.
Date: 24.05.22
'''

import unittest
import config as cfg
from sim_comms import run_commands, validate_output, construct_multi_command, cat_write

class TestSpecialCases(unittest.TestCase):
    '''
    Advanced file system tests to validate that inodes, data blocks,
    directory blocks, bitmaps and so on works correctly. The tests does
    not cover all cases, but should give a good indication on correct behaviour.
    All tests in this class expects that simple functionality already works.
    '''

    def setUp(self):
        cfg.compile()

    def test_cat_multiblock(self):
        ''' Test read and write with more than one data block. '''

        stringList = []

        # Create a string list with unique words.
        for num in range(0, 100):
            stringList.append("Hello World! Check out myWord_" + str(num))

        # Writes more than 512 bytes to a file.
        error = cat_write("myTextFile", stringList)
        msg = "Cat multi-block write error: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Check output when reading the file.
        output = run_commands(["more myTextFile", "stat myTextFile"])

        # Validate the stat command output, mainly check file size.
        error = validate_output(output, ["myTextFile:", "1", "0", "3290"])
        msg = "Cat invalid file size with more: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Get list of words from stringList.
        searchWords = []
        for string in stringList:
            for word in string.split():
                searchWords.append(word)

        # Validate the more command output, expect to find the text. 
        error = validate_output(output, searchWords)
        msg = "Invalid multi-block file read: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Truncate the large file with a new input.
        error = cat_write("myTextFile", ["The file has been truncated!"])
        msg = "Error truncating multi-block file: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Check size of the truncated file.
        output = run_commands(["stat myTextFile"])
        error = validate_output(output, ["myTextFile:", "1", "0", "29"])
        msg = "Wrong size of truncated multi-block file: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Read and verify the output of the truncated file.
        output = run_commands(["more myTextFile"])
        error = validate_output(output, ["The", "file", "has", "been", "truncated!"])
        msg = "Invalid multi-block truncated file read: {}".format(error)
        self.assertEqual(error, 0, msg)

    def test_multi_level_dirs(self):
        ''' Verify that the file system works with multi-level directories. '''
        
        depth = 50
        cdStr = "cd /"
        multiCmd = ""

        # Create command and cd strings.
        for dir in range(0, depth+1):
            cdStr += "d" + str(dir) + "/"
            multiCmd += "mkdir d{}".format(dir) + "\n" + "cd d{}".format(dir) + "\n"

        # Create two additional directories in the last directory.
        multiCmd += "mkdir myFolder1" + "\n" + "mkdir myFolder2" + "\n"

        # Build the large directory three.
        output = run_commands([multiCmd])
        error = validate_output(output, [])
        msg = "Failed to create multi-level directories: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Attempt to list out the last directory.
        multiCmd = construct_multi_command([cdStr, "ls"])
        output = run_commands([multiCmd])
        error = validate_output(output, [".", "..", "myFolder1", "myFolder2"])
        msg = "Failed to read multi-level directory: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Create a file two directories down from the largest entry.
        multiCmd = construct_multi_command([cdStr, "cd ..", "cd ..", "cat myFile"])
        output = run_commands([multiCmd])
        error = validate_output(output, [])
        msg = "Failed to create a file in a multi-level directory: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Locate and print the given file, check result.
        multiCmd = construct_multi_command([cdStr, "cd ..", "cd ..", "more myFile"])
        output = run_commands([multiCmd])
        error = validate_output(output, ["myFile"])
        msg = "Failed to open a file in a multi-level directory: {}".format(error)
        self.assertEqual(error, 0, msg)

    def test_inodes_and_directs(self):
        '''
        Test that inodes are freed and handeled correctly by the file system.
        In addition, test that the direct pointers work as expected.
        '''

        dirs = 200
        multiCmd = ""
        dirNames = []

        # Build command for creating 200 directories.
        for dir in range(3, dirs+1):
            multiCmd += "mkdir d{}".format(dir) + "\n"
            dirNames.append("d{}".format(dir))

        # Create all the directories.
        output = run_commands([multiCmd])
        error = validate_output(output, [])
        msg = "Failed to create 200 directories: {}".format(error)
        self.assertEqual(error, 0, msg)

        # List all directories.
        output = run_commands(["ls"])
        error = validate_output(output, dirNames)
        msg = "Failed to list all 200 directories: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Attempt to create one more directory, should fail.
        output = run_commands(["mkdir d201"])
        error = validate_output(output, [])
        msg = "Exceeded the direct pointer limit: {}".format(error)
        self.assertEqual(error, -17, msg)

        # Remove and create the last directory.
        output = run_commands(["rmdir d200", "mkdir d200", "ls"])
        error = validate_output(output, ["d200"])
        msg = "Remove does not free direct pointers: {}".format(error)
        self.assertEqual(error, 0, msg)
        
        # Enter a directory and create 50 more directories, uses all inodes.
        multiCmd = "cd d173\n"
        dirNames = []
        subDirs = 50

        # Build command for creating 50 directories.
        for subDir in range(3, subDirs+1):
            multiCmd += "mkdir sd{}".format(subDir) + "\n"
            dirNames.append("sd{}".format(subDir))

        # Create more directories.
        output = run_commands([multiCmd])
        error = validate_output(output, [])
        msg = "Failed to create 50 directories in sub-directory: {}".format(error)
        self.assertEqual(error, 0, msg)

        # List all directories.
        multiCmd = construct_multi_command(["cd d173", "ls"])
        output = run_commands([multiCmd])
        error = validate_output(output, dirNames)
        msg = "Failed to list all 50 sub-directories: {}".format(error)
        self.assertEqual(error, 0, msg)

        # Attempt to create one more directory, should fail.
        multiCmd = construct_multi_command(["cd d173", "mkdir sd51"])
        output = run_commands([multiCmd])
        error = validate_output(output, [])
        msg = "Exceeded the data block limit: {}".format(error)
        self.assertEqual(error, -16, msg)

        # Remove and create the last sub-directory.
        multiCmd = construct_multi_command(["cd d173", "rmdir sd50", "mkdir sd50", "ls"])
        output = run_commands([multiCmd])
        error = validate_output(output, ["sd50"])
        msg = "Remove does not free data blocks: {}".format(error)
        self.assertEqual(error, 0, msg)

    def test_bitmaps(self):
        ''' Test that bitmaps does not cause any errors. '''

        # Command for making directories.
        multiCmdMkdirs = construct_multi_command(["mkdir dirOne",
                                                "mkdir dirTwo",
                                                "mkdir dirThree",
                                                "mkdir dirFour",
                                                "mkdir dirFive",
                                                "mkdir dirSix"])

        # Command for removing directories.
        multiCmdRmdirs = construct_multi_command(["rmdir dirOne",
                                                "rmdir dirTwo",
                                                "rmdir dirThree",
                                                "rmdir dirFour",
                                                "rmdir dirFive",
                                                "rmdir dirSix"])

        # Attempt to exhaust bitmap/data blocks.
        for steps in range(0, 50):
            
            # Create directories
            output = run_commands([multiCmdMkdirs])
            error = validate_output(output, [])
            msg = "Could not create directories: {}".format(error)
            self.assertEqual(error, 0, msg)

            # Remove directories, test free.
            output = run_commands([multiCmdRmdirs])
            error = validate_output(output, [])
            msg = "Could not remove directories: {}".format(error)
            self.assertEqual(error, 0, msg)

        # Check empty but valid root folder.
        output = run_commands(["ls"])
        error = validate_output(output, [".", ".."])
        msg = "Root directory is damaged: {}".format(error)
        self.assertEqual(error, 0, msg)

    def test_cd_too_root(self):
        ''' Check that changing directory to root works. '''

        # Attempt to cd from a folder back to root.
        run_commands(["mkdir onRoot", "mkdir myDir"])
        multiCmd = construct_multi_command(["cd myDir", "cd /", "ls"])
        output = run_commands([multiCmd])
        error = validate_output(output, ["onRoot"])
        msg = "Changing directory to root does not work: {}".format(error)
        self.assertEqual(error, 0, msg)

    def tearDown(self):
        cfg.cleanup()

if __name__ == '__main__':
    unittest.main()