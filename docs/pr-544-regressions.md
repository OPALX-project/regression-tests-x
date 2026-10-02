# PR 544 tracking regression cases

These six cases preserve final `.stat` results from OPALX branch
`544-closed-orbit-finder-for-opalx`. They use the existing NightlyBuildX runner
and only `stat "column" last epsilon` checks. They detect changes to the recorded
tracking behavior; they are not independent analytical validation of the physics,
a tune calculation, or a space-charge convergence study.

## Cases

| Case | Input and stopping condition | Final checks |
| --- | --- | ---: |
| [DBA-COF-Track-1](../RegressionTests/DBA-COF-Track-1/DBA-COF-Track-1.in) | 2.5 MeV proton DBA; fresh host Boris COF; `INITIALORBIT=ic`; one centered particle; one directed reference turn; no SC | 13 |
| [DBA-COF-Gauss](../RegressionTests/DBA-COF-Gauss/DBA-COF-Gauss.in) | Same COF and ring; 64 generated Gaussian particles; transverse sigma = 50/3 micrometres, cutoff 3, zero momentum spread; one turn; no SC | 14 |
| [Cyclotron-Coasting](../RegressionTests/Cyclotron-Coasting/Cyclotron-Coasting.in) | One 72 MeV proton in eight field-map sectors; one directed reference turn; no SC | 13 |
| [Cyclotron-RF-Stop](../RegressionTests/Cyclotron-RF-Stop/Cyclotron-RF-Stop.in) | One proton with fundamental/third-harmonic RF gaps; `EKINSTOP=0.073` GeV; final complete kick reaches 73.27309842485 MeV | 13 |
| [Cyclotron-SC-Midpoint](../RegressionTests/Cyclotron-SC-Midpoint/Cyclotron-SC-Midpoint.in) | Fixed 262144-particle file; 12 steps; OPEN 32x32x32 mesh; one GAMMAZ bin; `SCFIELDUPDATE="MIDPOINT"` | 18 |
| [Cyclotron-SC-Prestep](../RegressionTests/Cyclotron-SC-Prestep/Cyclotron-SC-Prestep.in) | Identical bunch, fields, mesh and step count; `SCFIELDUPDATE="PRESTEP"`; separate reference | 18 |

Each launcher uses **one MPI rank**. Both DBA launchers also set one OpenMP
thread for repeatable local sampling. All required maps and particle files are
included in their case directories. Identical copies of the large particle file
and magnetic map have identical Git blobs.

`PSDUMPFREQ=0` disables particle dumps. `STATDUMPFREQ=1000000000` leaves one final
statistics row on the reference OPALX revision. The initial statistics dump is
disabled in that implementation; the final dump is performed when tracking ends.
Final-only output avoids comparing backend-dependent intermediate row counts.

The DBA section is the field-free midpoint of C1_D1. The ring list is rotated to
start with C1_D1; none of the 30 element placements is changed. COF and TRACK use
`DT=6.25e-11` s. A positive 1 pm Gaussian width avoids singular zero-width
sampling in the one-particle case, and Gaussian mean subtraction centers that
particle exactly before the solved orbit pose is added. The 64-particle case has
a 1 pm longitudinal width and is a thin, cold launch, not a matched beam.

The RF test is a short stopping-condition fixture, not full acceleration to
590 MeV. At the reference revision the SINGLEGAP path is host-side and restricted;
this test does not establish support for general device/PIC RF tracking. The PIC
cases use bunch charge 3.9486673247778873e-11 C, timestep
1.6452780519907864e-10 s, `GREENSF=STANDARD`, and `BBOXINCR=2`.

## Checks and tolerances

The `.rt` files are authoritative. The runner uses a strict **absolute** comparison
`abs(actual - reference) < epsilon`, in the units of each statistics column.

- DBA: particle count, energy, final time/path, six reference coordinates, and
  actual particle centroids. Track-1 position thresholds are 1 nm (10 nm for
  longitudinal mean/path), with reference momentum tolerance 1e-10 in p/(mc).
  The Gaussian centroid tolerance is 100 nm, allowing small sample-dependent
  nonlinear centroid motion while detecting a changed COF launch. Its charge is
  also checked. Both cases use 1e-9 MeV for energy and 1e-5 ns for time.
- Coasting/RF: particle count, energy, time/path, six reference coordinates and
  three particle centroids. Position/path tolerances are 1 micrometre, momenta
  1e-7 in p/(mc), time 1e-5 ns, and energy 1e-4 MeV (100 eV), well below a gap's
  energy gain. A count tolerance of 0.5 detects any integer count change.
- PIC: count, charge, bin count, energy, time/path, three RMS sizes, three RMS
  momenta, three normalized emittances and three centroids. Sizes use 10 nm,
  centroids/path 1 nm, momenta 1e-10 in p/(mc), emittances 1e-10 m, energy
  1e-7 MeV, and time 1e-9 ns. Charge uses 1e-20 C; integer counts/bins use 0.5.
  These thresholds leave room for floating-point reduction differences while
  resolving changes between the two update modes.

A fixed Gaussian seed does **not** yield the same samples on every backend.
Kokkos's pool assigns random streams according to execution threads. Therefore
DBA-COF-Gauss does not compare RMS sizes or emittances against a common baseline.
Its distribution is centered before launch, making the centroid check useful
without requiring identical finite samples. The deterministic PIC particle file
supports detailed moment checks. The one-particle references contain undefined
normalized correlation coefficients (`xpx`, `ypy`, `zpz`); none is checked.

These tolerances were checked on OpenMP with one and two threads, all on one MPI
rank. CUDA/HIP portability still needs validation. Do not loosen a failed
threshold without examining its absolute difference, units, and cause.

## Reference provenance

References were generated on 2026-10-01 with `bin/makeReference.sh --ranks 1` in
fresh temporary copies of the inputs. Only the generated `.stat` and `.stat.md5`
are retained here; `.out` and timing files are not regression oracles. Numerical
reference values were not hand-edited.

| Component | Revision/configuration |
| --- | --- |
| OPALX | `72154e2c409721cd18b0843b610b16ffa0c3360a`, clean tracked source, branch `544-closed-orbit-finder-for-opalx` |
| Regression base | `f383937d46f0380232cdb606d14cc2de8784b5c2` (`master`) |
| Compiler/backend | macOS arm64, Clang 21.1.8, Release, OpenMP, Open MPI 5.0.8; one rank, one thread |
| IPPL | `9df417aca5d2f5763ef9ac26be45eab15c6443e7` |
| Kokkos 5.2.0 | `d9397f95a04a0334d327647e64ab7f1882ca0664` |
| HeFFTe 2.4.1 | `4d8d4597b479d1e4709a2b1b4cd7d8922600045f` |
| NightlyBuildX runner | `5539fa31b56d4952d923e6641557d6683c68725a` (`main`) |

Reference executable SHA-256:
`ab93a5d27f305e2a2075bb626fbfef7a8238e33de535397fb7ea1598cf3467c9`.
The magnetic maps, RF maps and particle files are unchanged copies of the
previously exercised cyclotron fixtures. The shared PIC particle file SHA-256 is
`df11b9cf5b8cd75d5b967f6e43b8eb77b99228067161364139dee4f6739ade47`;
magnetic map SHA-256 is
`0bd65560cfe7c92df55e64a17058d6d856cc3b75d4737a2a100bcbbe97b0d305`.

## Running these cases

Use an OPALX build that includes the branch's COF, INITIALORBIT, ring and RF
functionality. From the regression repository root, with NightlyBuildX beside it:

```bash
export OPALX_EXE_PATH=/path/to/opalx/build/src
export OPALX_SRC_DIR=/path/to/opalx
export OMP_NUM_THREADS=1 OMP_DYNAMIC=false OMP_PROC_BIND=false
python3 ../NightlyBuildX/scripts/run-reg-tests.py \
  --base-dir "$PWD/RegressionTests" --opalx-exe-path "$OPALX_EXE_PATH" --no-gpl \
  DBA-COF-Track-1 DBA-COF-Gauss Cyclotron-Coasting Cyclotron-RF-Stop \
  Cyclotron-SC-Midpoint Cyclotron-SC-Prestep
```

Expected summary: **89 / 89 checks passed**. Require all six simulations to run
and the full check count: this runner revision can omit checks after a launcher
failure, so exit status alone is insufficient. Its existing behavior is unchanged
by these fixtures. The cases become discoverable through the existing directory
scan; this change does not alter any CI allowlist.

For a reference update, run the existing generator in a fresh copy of each case
with a reviewed executable, then inspect the result before replacing its `.stat`
and generated checksum. The generator rewrites `.local`, so keep the maintained
launchers when copying references back.

## Local validation

- All six maintained launchers ran successfully through the unmodified stock
  runner. The final definitions passed all 89 checks against the fresh one-thread
  outputs; those checked values reproduced their references exactly.
- Independent one-rank, two-thread runs also passed all 89 checks. These runs
  invoked OPALX directly to override the DBA launchers' one-thread setting.
  Gaussian centroids changed by at most 0.26 nm. PIC differences stayed below
  9e-6 of their respective tolerances.
- In disposable copies, increasing each final energy by ten times its threshold
  caused exactly six failures: 83/89 passed and the stock runner exited 1.
  The committed reference files were not modified for this negative control.
- PRESTEP and MIDPOINT transverse momentum spreads differ by about 2900 times
  their tolerance, and their energies by about six times their tolerance. Thus
  substituting one update mode's result for the other is detectable.
- Reference-generation elapsed times on this machine were approximately 3.7 s
  (DBA single particle), 15.2 s (Gaussian), 0.3 s (coasting), 0.3 s (RF), and
  2.4 s for each PIC case, excluding the runner's comparison plots.
