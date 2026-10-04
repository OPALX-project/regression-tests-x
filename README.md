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


## Ring and cyclotron regression cases

The six [PR 544 tracking cases](docs/pr-544-regressions.md) cover DBA COF launches,
cyclotron coasting and RF stopping, and MIDPOINT/PRESTEP space charge using only
final `.stat` comparisons. The guide records their tolerances, reference
provenance, limitations, and the command to run all 89 checks.

## Short BeamBeam regressions

These single-pass, rigid-source cases use only the existing `.in`, `.local`,
`.rt` and `.stat` architecture. HDF5 is disabled. Each case has a fixed
512-particle primary file; electrons and positrons have separate distribution
instances. The launchers use one OpenMP thread per rank, with at most four ranks.

| Case | Selected statistics | MPI ranks | Steps | Assertions |
| --- | --- | ---: | ---: | ---: |
| BeamBeam-OffsetKick | Electron witness, c1 | 1 | 4 | 12 |
| BeamBeam-TimedBirths | Six timed positrons, c2; six electrons also tracked | 1 | 8 | 13 |
| BeamBeam-WitnessMPI | Electron witness, c1; same one-rank reference as the offset case | 4 | 4 | 12 |
| BeamBeam-RigidSource | Ballistic primary, c0, with interacting witnesses | 1 | 4 | 12 |

The launcher copies the selected container's statistics verbatim to the canonical
`<case>.stat` expected by the existing runner. The `.rt` description includes
`[tolerance: absolute]` so OPALX's embedded CI comparator uses the same convention
as NightlyBuildX; older cases retain their existing CI comparison convention.
`last` is an absolute final-value difference; NightlyBuildX's `avg` is
`sqrt(sum((actual-reference)^2))/N`, not a difference of averages.

Witness tolerances are 0.1 nm for positions/sizes and 1e-10 in normalized momentum
p/(mc), resolving the nonzero kick while allowing reduction roundoff. The frozen
primary uses 1 pm and 1e-12 respectively. Time tolerance is 1e-9 ns, energy is
1e-9 MeV, and particle-count tolerance 0.5 rejects any integer loss. The timed
population history also has an `avg` tolerance of 1e-6. These are reproducibility
checks against fixed inputs, not CAIN accuracy claims. Independent analytic E/B,
passive-charge exclusion, mirrored fields and exact fractional birth steps are
tested in OPALX gtest, including two/four-rank field and four-rank birth cases.

References were generated on 2026-10-02 with `bin/makeReference.sh --ranks 1`
in disposable case copies, selecting the indicated `_cN.stat` without changing
numerical contents. OPALX was at `9822ef85e`, with the separately uncommitted
resident-view zero-fill fix in `SpaceChargeFrames.h`; the associated FFT2D5 test
was also uncommitted. Executable SHA-256:
`e16d324edf1f6f7870005457d034cec19558215832517c8b6c37e1d3d54633d0`.
Platform: macOS arm64, Clang 21.1.8, Release/OpenMP, Open MPI 5.0.8;
IPPL `a7e505730a76dd1edc7d0c8b96fb4223d9f84cfb`, Kokkos 5.2.0.
NightlyBuildX `5539fa31b56d4952d923e6641557d6683c68725a` passes **49/49** checks,
including the four-rank comparison. The OPALX CI comparator also passes all 49.
Disabling witness gathering fails the kick checks; disabling BBRIGID fails the
primary checks. CUDA and Serial Debug CI timings remain to be validated.

Reference generation took 0.98–2.03 seconds per case locally; OPALX CI caps each
new simulation at 30 seconds. Do not regenerate directly over the custom
launchers: `makeReference.sh` writes a generic `.local` file. Use a disposable
copy, select the generated reference `_cN.stat` as `<case>.stat`, and regenerate
its MD5 checksum. Never edit reference numbers by hand.

Run with the existing NightlyBuildX `scripts/run-reg-tests.py`, selecting these
four directory names and setting `--opalx-exe-path` to the OPALX binary directory.
Require all 49 checks, not just the runner's exit status.
