# Microstrip Patch Antenna Project Overview

## Introduction
This project automates the creation of a **rectangular microstrip patch antenna** in ANSYS HFSS using **PyAEDT**.  
Microstrip patch antennas are popular due to their **low profile**, **light weight**, and ease of fabrication, especially for **wireless communication**.

---

## Geometry Parameters
- Substrate (FR4 epoxy): `80 × 60 × 1.6 mm`
- Patch (PEC): `38 × 29 mm` on top
- Feed line: `3 × 15 mm` microstrip line
- Ground plane: PEC rectangle at z=0
- Airbox: padded box with radiation boundary

---

## Boundaries & Setup
- Patch + Feed → PEC conductor
- Ground plane → PEC
- Substrate → FR4 epoxy
- Input feed → Lumped port (50Ω)
- Solution frequency → **2.4 GHz**

---

## Output
The generated `.aedt` file contains:
- Substrate, patch, feed, ground
- Excitation setup (Lumped Port)
- Simulation setup at 2.4 GHz

Once opened in HFSS GUI, you can:
- Analyze **S11 at 2.4 GHz**
- Study patch resonance
- Plot radiation patterns
