# Regression Tests Repository

This repository contains regression tests for the OPALX project.

## Directory Structure

The tests are organized under the `RegressionTests/` directory. Each subdirectory represents a specific test case.

### Test Case Structure

Each test case folder (e.g., `RegressionTests/FodoCell/`) generally contains the following files:

- **`<TestName>.in`**: The input file for the simulation (e.g., `FodoCell.in`).
- **`<TestName>.local`**: A shell script to execute the simulation locally. It typically sets up the environment and calls the executable with `mpirun`.
- **`<TestName>.rt`**: The regression test definition file. This file specifies:
  - The name/description of the test.
  - The statistics to check (e.g., `rms_x`, `energy`).
  - The type of check (e.g., `avg`).
  - The tolerance allowed for the test to pass.
- **`reference/`**: A subdirectory containing the reference output files (e.g., `<TestName>.stat`) used to validate the current run.

## Make a Reference

Each test needs to provide a reference solution under `RegressionTests/test-dir/reference/`. Please generate the reference with the provided script `bin/makeReference.sh`. In order to use it, add `bin/` to `PATH` and set the build directory as an env: 
```bash
# From inside the top level build/ directory set OPALX_EXE_PATH
export OPALX_EXE_PATH="$(pwd)/src/opalx"

# From inside the top level regression-tests-x/ directory, add to PATH:
export PATH="$(pwd)/bin:$PATH"
```
Next, place the input file in a new test directory, e.g.:
```text
RegressionTests/
└── FodoCell/
    └── FodoCell.in
```
Note that you can add whatever you need in this directory (like fieldmaps). Only the folder name "`reference`" is reserved. Then, run the script:
```bash
cd .../FodoCell
makeReference.sh # Will automatically pick up the .in file
```
Then, in the test directory, add the `.rt` file (which defines after which parameters the input file is tested against), e.g.:
```rt
"Add one line of meaningful explanation of your test"
stat "rms_x" avg 1E-5
stat "rms_y" avg 1E-5
stat "rms_s" avg 1E-5
stat "emit_x" avg 1E-5
stat "emit_y" avg 1E-5
stat "emit_s" avg 1E-5
stat "energy" avg 1E-5
```
Here you can use all the flags that are available in the `.stat` file and use either `avg` or `last` as the type of check. Your test directory tree should now look like this:
```text
RegressionTests/
└── FodoCell/
    ├── FodoCell.in
    ├── FodoCell.local
    ├── FodoCell.rt
    └── reference/
        └── ...
```
Note that the `.local` file determines how the test is executed. It's auto-generated and generally doesn't need to be touched. Content inside the `reference/` folder is also auto-generated and should not be modified manually.

