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