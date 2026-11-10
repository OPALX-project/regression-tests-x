#!/usr/bin/env python3
"""Generate independent covariance reference; never reads OPALX output."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
from scipy.constants import e, epsilon_0, proton_mass
from scipy.integrate import solve_ivp
from ellipsoid_model import geometry, integrate, J


ROOT = Path(__file__).resolve().parent


def main():
    config_path = ROOT / "physics_config.json"
    config = json.loads(config_path.read_text())
    axes = np.array(config["initial_semiaxes_m"])
    length = max(axes)
    omega = e*config["Bz_T"]/proton_mass
    initial = np.diag(axes/length)
    strength = 3*e*config["charge_C"]/(4*np.pi*epsilon_0*proton_mass*omega**2*length**3)
    times = np.arange(1, config["steps"]+1)*config["dt_s"]

    def rhs(tau, state):
        shape = state[:9].reshape(3, 3)
        velocity = state[9:].reshape(3, 3)
        depolarization, _, _ = geometry(shape)
        acceleration = J@velocity + strength/np.linalg.det(shape)*depolarization@shape
        return np.r_[velocity.ravel(), acceleration.ravel()]

    result = solve_ivp(rhs, [0, omega*times[-1]],
                       np.r_[initial.ravel(), (J@initial).ravel()],
                       t_eval=omega*times, method="DOP853", rtol=2e-11, atol=2e-13)
    assert result.success, result.message
    shapes = result.y[:9].T.reshape(-1, 3, 3)*length
    phase = config["initial_phase_rad"]
    cosine, sine = np.cos(phase), np.sin(phase)
    rotation = np.array([[cosine, sine, 0.], [-sine, cosine, 0.], [0., 0., 1.]])
    physical_to_opal = np.array([[1., 0., 0.], [0., 0., 1.], [0., -1., 0.]])
    transform = physical_to_opal@rotation
    covariance = transform@(shapes@shapes.transpose(0, 2, 1)/5)@transform.T
    path = ROOT/config["analytic_covariance_file"]
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time_s", "xx", "xy", "xz", "yy", "yz", "zz"])
        for time, matrix in zip(times, covariance):
            values = [time, matrix[0, 0], matrix[0, 1], matrix[0, 2], matrix[1, 1], matrix[1, 2], matrix[2, 2]]
            writer.writerow([format(value, ".17e") for value in values])
    _, checks, _, _ = integrate(config["charge_C"])
    assert checks["energy_max_relative_drift"] < 1e-8
    assert checks["canonical_Lz_max_relative_drift"] < 1e-8
    assert checks["max_sum_D_error"] < 1e-12
    provenance = {
        "model": config["model"], "input_from_OPALX": False,
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "model_source_sha256": hashlib.sha256((ROOT/"ellipsoid_model.py").read_bytes()).hexdigest(),
        "covariance_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "integrator": "DOP853", "rtol": 2e-11, "atol": 2e-13,
        "independent_model_checks": checks,
    }
    (ROOT/"analytic_provenance.json").write_text(json.dumps(provenance, indent=2)+"\n")
    print(path)


if __name__ == "__main__":
    main()
