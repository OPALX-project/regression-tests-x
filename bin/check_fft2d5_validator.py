#!/usr/bin/env python3
"""Check that disposable intermediate/completeness errors fail physics validation.

This checks the validator, not OPALX tracking. It uses the generated native
reference as its positive control and never modifies a committed reference.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import re
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-dir", type=Path,
                        default=ROOT/"RegressionTests/FFT2D5-UniformB-1pC")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    case = args.case_dir.resolve()
    spec = importlib.util.spec_from_file_location("fft2d5_physics", case/"validate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reference = case/"reference"/(case.name+".stat")
    assert module.validate(reference)["passed"], "Positive reference control failed"
    original = reference.read_text()
    header = re.search(r"&data\b.*?&end", original, flags=re.S)
    prefix = original[:header.end()]
    lines = original[header.end():].splitlines(keepends=True)
    parameter_count = len(re.findall(r"&parameter\b.*?&end", original, flags=re.S))
    active = [index for index, line in enumerate(lines)
              if line.strip() and not line.lstrip().startswith("!")]
    rows = active[parameter_count:]
    columns = [re.search(r"\bname\s*=\s*([^,\s]+)", block).group(1).strip('"')
               for block in re.findall(r"&column\b(.*?)&end", original, flags=re.S)]
    controls = []
    changes = [("intermediate-rms", "rms_x", None),
               ("particle-loss", "numParticles", 98303),
               ("charge", "charge", 1.1e-12),
               ("shifted-time", "t", 123.456),
               ("nonfinite-rms", "rms_y", "nan"),
               ("truncated-run", None, None)]
    with tempfile.TemporaryDirectory(prefix="fft2d5-validator-") as directory:
        for label, column, value in changes:
            mutated = lines.copy()
            if column:
                row_index = rows[len(rows)//2]
                values = mutated[row_index].split()
                field = columns.index(column)
                values[field] = str(float(values[field])*1.05) if value is None else str(value)
                mutated[row_index] = "\t".join(values)+"\n"
            else:
                mutated.pop(rows[-1])
            path = Path(directory)/(label+".stat")
            path.write_text(prefix+"".join(mutated))
            try:
                result = module.validate(path)
            except (ValueError, OSError, KeyError) as error:
                result = {"passed": False, "error": str(error)}
            assert not result["passed"], f"Mutation {label} incorrectly passed"
            if label == "intermediate-rms":
                actual, _ = module.read_stat(path)
                baseline, _ = module.read_stat(reference)
                assert all(actual[-1][key] == baseline[-1][key]
                           for key in ["rms_x", "rms_y", "rms_s"])
            controls.append({"mutation": label, "correctly_rejected": True})
    result = {"positive_control_passed": True,
              "negative_controls_passed": len(controls), "controls": controls}
    text = json.dumps(result, indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
