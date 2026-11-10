#!/usr/bin/env python3
"""Validate every tracking step against an independent ellipsoid covariance.

Runtime dependencies: Python standard library only. The analytic table is made
by make_analytic_reference.py without reading OPALX output. The actual reference
momentum defines the axes in which OPALX reports rms_x/rms_y/rms_s.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import re
import sys


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_stat(path):
    text = path.read_text()
    columns, units = [], {}
    for block in re.findall(r"&column\b(.*?)&end", text, flags=re.S):
        name = re.search(r"\bname\s*=\s*([^,\s]+)", block)
        if name is None:
            raise ValueError("SDDS column has no name")
        name = name.group(1).strip('"')
        columns.append(name)
        unit = re.search(r"\bunits\s*=\s*([^,\s]+)", block)
        units[name] = unit.group(1).strip('"') if unit else ""
    header = re.search(r"&data\b.*?&end", text, flags=re.S)
    if header is None or not re.search(r"no_row_counts\s*=\s*1", header.group(0)):
        raise ValueError("Expected ASCII SDDS with no_row_counts=1")
    parameters = len(re.findall(r"&parameter\b.*?&end", text, flags=re.S))
    lines = [line.strip() for line in text[header.end():].splitlines()
             if line.strip() and not line.lstrip().startswith("!")]
    rows = []
    for line in lines[parameters:]:
        values = line.split()
        if len(values) != len(columns):
            raise ValueError("SDDS row length differs from its column count")
        rows.append(dict(zip(columns, map(float, values))))
    if not rows:
        raise ValueError("Statistics contain no tracking rows")
    return rows, units


def validate(stat_path):
    config_path = ROOT / "physics_config.json"
    config = json.loads(config_path.read_text())
    provenance = json.loads((ROOT / "analytic_provenance.json").read_text())
    covariance_path = ROOT / config["analytic_covariance_file"]
    fixtures = {
        config_path: provenance["config_sha256"],
        covariance_path: provenance["covariance_sha256"],
        ROOT / "ellipsoid_model.py": provenance["model_source_sha256"],
        ROOT / config["source_file"]: config["source_sha256"],
        ROOT / config["fieldmap_file"]: config["fieldmap_sha256"],
        ROOT / config["reference_path_file"]: config["reference_path_sha256"],
    }
    for path, expected in fixtures.items():
        if digest(path) != expected:
            raise ValueError(f"Fixture changed without independent review: {path.name}")
    with covariance_path.open(newline="") as stream:
        model = [{key: float(value) for key, value in row.items()}
                 for row in csv.DictReader(stream)]
    rows, units = read_stat(stat_path)
    steps = int(config["steps"])
    if len(rows) != steps or len(model) != steps:
        raise ValueError(f"Expected all {steps} tracking steps; found {len(rows)} STAT and {len(model)} model rows")
    for key in ["rms_x", "rms_y", "rms_s"]:
        if units.get(key) != "m":
            raise ValueError(f"Unexpected unit for {key}: {units.get(key)}")
    time_scale = {"s": 1., "ms": 1e-3, "us": 1e-6,
                  "ns": 1e-9, "ps": 1e-12}.get(units.get("t"))
    if time_scale is None:
        raise ValueError(f"Unexpected time unit: {units.get('t')}")
    fields = ["t", "rms_x", "rms_y", "rms_s", "ref_px", "ref_py", "ref_pz", "charge", "numParticles"]
    errors = {key: 0. for key in ["rms_x", "rms_y", "rms_s"]}
    worst_step = {key: 0 for key in errors}
    max_charge_error = 0.
    for index, (row, expected) in enumerate(zip(rows, model), 1):
        if any(not math.isfinite(row[key]) for key in fields):
            raise ValueError(f"Nonfinite required value at step {index}")
        time = row["t"] * time_scale
        target_time = index * config["dt_s"]
        if not math.isclose(time, target_time, rel_tol=2e-11, abs_tol=1e-18):
            raise ValueError(f"Missing or shifted time at step {index}: {time} instead of {target_time}")
        if not math.isclose(expected["time_s"], target_time, rel_tol=2e-11, abs_tol=1e-18):
            raise ValueError(f"Independent model time mismatch at step {index}")
        if row["numParticles"] != config["expected_particles"]:
            raise ValueError(f"Particle count changed at step {index}")
        charge_error = abs(row["charge"] / config["assigned_charge_C"] - 1.)
        max_charge_error = max(max_charge_error, charge_error)
        if not math.isclose(row["charge"], config["assigned_charge_C"], rel_tol=1e-11, abs_tol=1e-25):
            raise ValueError(f"Charge changed at step {index}")
        momentum = math.sqrt(sum(row[key] ** 2 for key in ["ref_px", "ref_py", "ref_pz"]))
        if momentum == 0. or abs(row["ref_py"]) / momentum > 1e-9:
            raise ValueError("This reference requires a nonzero horizontal-planar orbit")
        theta = math.atan2(-row["ref_px"], row["ref_pz"])
        cosine, sine = math.cos(theta), math.sin(theta)
        variances = {
            "rms_x": cosine*cosine*expected["xx"] + 2*cosine*sine*expected["xz"] + sine*sine*expected["zz"],
            "rms_y": expected["yy"],
            "rms_s": sine*sine*expected["xx"] - 2*cosine*sine*expected["xz"] + cosine*cosine*expected["zz"],
        }
        for key, variance in variances.items():
            if variance <= 0. or row[key] <= 0.:
                raise ValueError(f"Nonpositive RMS or model variance at step {index}")
            error = abs(row[key] / math.sqrt(variance) - 1.)
            if error > errors[key]:
                errors[key], worst_step[key] = error, index
    tolerance = config["rms_relative_tolerance"]
    return {
        "case": config["name"], "passed": all(error <= tolerance for error in errors.values()),
        "criterion": "Every total RMS size within 1% of independent ellipsoid model at every STAT step; exact particle count, charge and full time coverage",
        "model_charge_C": config["charge_C"],
        "assigned_charge_C": config["assigned_charge_C"],
        "stat_samples": len(rows), "final_time_s": rows[-1]["t"]*time_scale,
        "expected_particles": config["expected_particles"],
        "maximum_charge_relative_error": max_charge_error,
        "rms_relative_tolerance": tolerance,
        "maximum_relative_rms_errors": errors, "worst_step": worst_step,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stat", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.stat)
    except (ValueError, OSError, KeyError) as error:
        result = {"passed": False, "error": str(error)}
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
