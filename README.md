# FREE1105 — Funky Radical Electrodynamics Engine

A 2D electrodynamics simulator built from scratch in Python, featuring real-time charge dynamics, a custom symplectic physics engine, and a 3D electric potential visualiser. Developed independently alongside a second-year Theoretical Physics degree.

### JUST DOWNLOAD THE REPO AND RUN MAIN.PY - you can look through the Jupyter file if you want to see the iterative steps and thoughts along the way, but if you wish to run phase 4, just go through main.py. You have to download the following modules tho. And yeah as a man of God, i will not lie that I used Claude to generate this README
- pygame
- matplotlib
- numpy

---

## Overview

FREE1105 simulates the motion of point charges under mutual Coulomb interactions, with a focus on **numerical stability** and **energy conservation**. The project was built iteratively — both the physics and the numerical methods were developed from first principles, with deliberate attention to where and why naive approaches fail.

The codebase is split into modular components: a physics engine, a charge system, a GUI layer, and a standalone 3D visualiser.

---

## Physics

### Coulomb Force (with Softening)

Pairwise electrostatic forces are computed using Coulomb's law:

$$F_{ij} = k_e \frac{q_i q_j}{r^2} \hat{r}$$

A **softening parameter** $\varepsilon$ is applied to the denominator to regularise near-singularities:

$$F_{ij} = k_e \frac{q_i q_j}{r^2 + \varepsilon^2} \cdot \frac{\vec{r}}{|r^2 + \varepsilon^2|^{1/2}}$$

This is a standard technique in N-body simulation (cf. cosmological particle codes) and ensures numerical stability when particles approach each other closely.

### Electric Potential Surface (Phase 4)

The scalar electric potential is computed over a 2D grid:

$$V(x, y) = \sum_i \frac{k_e q_i}{r_i(x,y)}$$

and rendered as a 3D surface — positive charges warp the grid upward, negative charges downward — providing a geometric interpretation of the field analogous to spacetime curvature diagrams.

---

## Numerical Methods — Integrator Progression

A central focus of this project was achieving **long-term energy conservation**. The integrator was developed through four stages:

### 1. Explicit Euler
$$x_{n+1} = x_n + v_n \Delta t, \quad v_{n+1} = v_n + a_n \Delta t$$
Simple to implement, but **energy grows monotonically** — the system "explodes" over time. Rejected.

### 2. RK2 (Midpoint Method)
Second-order Runge-Kutta. Significantly smoother, but energy still drifts secularly. Rejected for long runs.

### 3. RK4
Fourth-order accuracy. Good short-term behaviour, but RK methods are **not symplectic** — they do not preserve the phase-space volume of Hamiltonian systems, leading to energy drift over long timescales.

### 4. Velocity-Verlet (Symplectic)
The final integrator:

$$x_{n+1} = x_n + v_n \Delta t + \tfrac{1}{2} a_n \Delta t^2$$
$$v_{n+1} = v_n + \tfrac{1}{2}(a_n + a_{n+1}) \Delta t$$

Velocity-Verlet is a **symplectic integrator** — it preserves the symplectic structure of Hamiltonian mechanics, meaning it conserves a *shadow Hamiltonian* close to the true one. In practice this means total energy **oscillates around a fixed value** rather than drifting, which is exactly what was observed in the energy diagnostics.

This is the integrator of choice in molecular dynamics (e.g. GROMACS, LAMMPS) and N-body codes precisely for this reason.

---

## Collision Resolution

Pairwise particle collisions are handled via **impulse-based resolution**:

- Relative velocity along the collision normal is computed
- An impulse scalar is derived from the coefficient of restitution $e$ and the reduced mass of the pair
- Positional correction (80% factor) is applied post-impulse to prevent particle overlap without injecting energy

Wall collisions use a configurable wall coefficient of restitution, controllable at runtime via slider.

---

## Energy Diagnostics

Total kinetic and potential energy are tracked each frame:

$$E_{total} = \underbrace{\sum_i \frac{1}{2} m_i v_i^2}_{KE} + \underbrace{\sum_{i < j} \frac{k_e q_i q_j}{r_{ij,\text{soft}}}}_{PE}$$

The visualised oscillation of $E_{total}$ around its initial value was the primary diagnostic used to validate symplectic behaviour and tune the softening parameter.

---

## Phase 4 — 3D Potential Visualiser

A standalone real-time 3D visualiser running in a separate matplotlib window, updating at 5 Hz via a background thread (thread-safe snapshot pattern to avoid blocking the pygame loop).

- Surface height encodes normalised $V(x,y)$
- Greyscale colouring matches the 2D heatmap convention (bright = positive, dark = negative)
- Blue wireframe overlay for geometric clarity
- Charge positions marked as coloured scatter points on the surface

---

## Stack

| Component | Library |
|---|---|
| Simulation loop & GUI | `pygame` |
| Numerics | `numpy` |
| 3D Visualisation | `matplotlib` (TkAgg backend, background thread) |
| Language | Python 3 |

---

## Project Structure

```
FREE1105/
├── main.py                  # Simulation loop and state machine
├── physics_engine.py        # Velocity-Verlet integrator, collision resolution, energy diagnostics
├── point_charge.py          # PointCharge class, trail rendering, arrow display
├── electric_field.py        # 2D heatmap of electric potential (pygame surface)
├── phase4_visualiser.py     # 3D potential surface (matplotlib, threaded)
├── gui.py                   # All UI components (sliders, forms, toggles)
├── constants_for_all_files.py
└── README.md
```

---

## Key Engineering Decisions

**Symplectic over RK4** — RK4 is higher order but not structure-preserving. For a Hamiltonian system like this, Velocity-Verlet gives better long-run energy behaviour at lower computational cost per step.

**Softening parameter** — Chosen empirically by monitoring energy conservation across a range of close-approach scenarios. Too small causes energy spikes; too large distorts the physics. A value of $\varepsilon = 100$ px was found to balance stability and accuracy at the simulation's spatial scale.

**Thread-safe visualiser** — The matplotlib window runs on a daemon thread. Charge data is copied to a shared snapshot under a mutex each frame, and the render thread consumes it at its own rate. This decouples the 60+ FPS pygame loop from the slower matplotlib redraw.

**Modular state machine** — The simulation runs a three-state machine (SETUP / RUNNING / PAUSED) that cleanly separates editing logic from physics updates, preventing race conditions between drag-and-drop interaction and live force calculations.

---

## Possible Extensions

- Phase 3: Charged rigid body dynamics (torque from non-uniform charge distributions)
- Phase 5: Maxwell's equations — displacement current, magnetic field generation, electromagnetic wave propagation
- Barnes-Hut tree for O(N log N) force computation
- GPU acceleration via CuPy for large N

The reason the phases are outta order is because initially the geometric visualisation was gonna be phase 4, but I ran out of time with other commitments so I just decided to do it instead of phase 3 and 5 quickly because it would be pretty easy compared to 3 and 5, considering it is basically just matplotlib.

---

*Built independently as a self-directed computational physics project, 2025–26.*

![WhatsApp Image 2026-02-23 at 01 00 25](https://github.com/user-attachments/assets/f406baf8-15f7-4318-8896-94861fcc9ada)
<img width="1906" height="996" alt="image" src="https://github.com/user-attachments/assets/8a589cc4-d17c-4821-9932-99e83a15ee4d" />
<img width="1919" height="959" alt="image" src="https://github.com/user-attachments/assets/423fbba2-0143-4b61-a73f-7ea3235bb881" />
<img width="1769" height="1026" alt="image" src="https://github.com/user-attachments/assets/78eb871b-89b7-4b4e-9c50-55479ca131f8" />


