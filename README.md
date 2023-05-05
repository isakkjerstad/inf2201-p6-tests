# INF-2201 P6 FILE SYSTEM TEST SUITE:
Testing suite for project six in INF-2201 (operating systems) at UiT.
## Instructions:
Run the automated tests by following the steps below.
- Download the code and place the ``` test ``` folder outside your ``` src ``` directory.
- In ``` config.py ``` ensure that ``` EXEC_NAME ``` matches the name of the shell simulator executable file.
- Install libraries using: ``` pip3 install -r requirements.txt ``` within the ``` test ``` folder.
- Run ``` python3 main.py ``` to begin testing your file system.
## How does the testing work?
The testing suite compiles, runs and executes commands in the shell simulator. Expected output is checked
based on specific input to the shell simulator. See the source code files for details.
### Note:
- See error codes in the ``` validate_output ``` method in the ``` sim_comms.py ``` file.
- Your file system must follow Linux FS conventions (i.e. "." and ".." etc.).
