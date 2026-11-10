# Independent ellipsoid reference

For a uniform unit-ball vector u, the cold uniform-volume ellipsoid is
`r(t)=C(t)+A(t)u`, with covariance `A A^T/5` and density
`rho=3Q/(4 pi det A)`. In a uniform external Bz field its nonrelativistic,
electrostatic affine equations are

```text
C'' = Omega J C'
A'' = q rho D A/(m epsilon_0) + Omega J A'
Omega = q Bz/m
J = [[0,1,0],[-1,0,0],[0,0,0]]
```

D is the depolarization tensor of the instantaneous ellipsoid. For principal
semiaxes a,b,c, `D_a = abc/3 * R_D(b^2,c^2,a^2)`, cyclically; the three factors
sum to one. `R_D` is Carlson's elliptic integral. Initial velocities are rigid
corotation, `A'(0)=Omega J A(0)`.

`ellipsoid_model.py` is the independent implementation frozen from OPALX commit
`fd6ba8dc5`. It checks sphere/oblate factors, direct quadrature, zero-charge
rotation, energy, canonical angular momentum and tighter numerical integration.
`make_analytic_reference.py` evaluates the physical covariance at all promised
tracking times, rotates it to the OPALX laboratory axes and saves it. The runtime
validator projects this covariance into the actual reference axes in each STAT
row. It does not read or fit OPALX fields when generating the oracle.

The assumptions are cold continuum motion, uniform volume charge, free space,
nonrelativistic electrostatic self-fields and a uniform applied magnetic field.
There are no material boundaries, thermal spread, collisions, radiation or
magnetic self-fields in this model. Beta=0.01 keeps the omitted relativistic
terms small; numerical tracking still needs separate time-step checks.

This validates total RMS sizes for the stated source and orbit. It does not
assert 1% accuracy in much smaller charged-minus-zero growth increments.
The main case documentation is [fft2d5-uniform-b.md](../../docs/fft2d5-uniform-b.md).
