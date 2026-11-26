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
  - The statistics to check (e.g., `rms_x`, `energy`), or values in a JSON file the run writes.
  - The type of check (e.g., `avg`).
  - The tolerance allowed for the test to pass.
- **`reference/`**: A subdirectory containing the reference output files (e.g., `<TestName>.stat`, or the JSON files the `.rt` names) used to validate the current run.

## Make a Reference

Each test needs to provide a reference solution under `RegressionTests/test-dir/reference/`. Please generate the reference with the provided script `bin/makeReference.sh`. In order to use it, add `bin/` to `PATH` and set `OPALX_EXE_PATH` to the directory containing the `opalx` binary (not the top-level build directory and not the binary itself):
```bash
# From inside the top level build/ directory, point OPALX_EXE_PATH at the directory that contains `opalx`
export OPALX_EXE_PATH="$(pwd)/src"

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
Then, in the test directory, add the `.rt` file (which defines which statistics from the `.stat` output are checked and with what tolerance), e.g.:
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
Here you can use all the flags that are available in the `.stat` file and use either `avg` or `last` as the type of check. `#` starts a comment; use it to say why a tolerance was chosen.

A test can also check numbers in a JSON file that the run writes, such as the closed-orbit result of `COF, OUTPUT="orbit.json"`. A line names the file, a path into it and the tolerance:
```rt
orbit.json root.orbits.0.optics.full_tunes.horizontal_radial 1E-9
```
The path is dot-separated and starts with `root`, the whole document; every further part is an object key or, inside a list, the index of an entry (`orbits.0` is the first orbit). The value at the path must be a number, so a single array entry such as `root.orbits.0.solution.section_coordinates.1` works, a whole array does not. The check passes when the value differs from the one in `reference/orbit.json` by less than the tolerance. `makeReference.sh` copies every JSON file the run writes into `reference/`; a test may consist of JSON checks only (see `DBA-COF-JSON`). Your test directory tree should now look like this:
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


## Ring and cyclotron regression cases

The six [PR 544 tracking cases](docs/pr-544-regressions.md) cover DBA COF launches,
cyclotron coasting and RF stopping, and MIDPOINT/PRESTEP space charge using only
final `.stat` comparisons. The guide records their tolerances, reference
provenance, limitations, and the command to run all 89 checks.

## FFT2D5 curved-orbit validation

The [uniform-field ellipsoid cases](docs/fft2d5-uniform-b.md) add zero-space-charge
and 1 pC half-turn tracking controls. Their test-local `validate.py` checks every
time step against an independent covariance model. Direct-launch CI runners
must invoke that hook in addition to their conventional `.rt` baseline checks;
last/average comparisons alone do not enforce the all-step physics criterion.
