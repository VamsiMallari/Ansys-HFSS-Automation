# Horn Antenna Overview

## 📡 Introduction
A **horn antenna** is a type of aperture antenna that consists of a flaring metal waveguide shaped like a horn.  
It is widely used in microwave frequencies (1 GHz – 100 GHz) due to its **high gain, directivity, and simple design**.

---

## 🔬 Why Horn Antennas?
- High gain and directivity  
- Wide bandwidth  
- Low reflection and standing wave ratio (SWR)  
- Simple mechanical design  
- Often used as **standard gain antennas** for calibration  

Applications:
- Radar systems  
- Satellite communication  
- Radio astronomy  
- Antenna measurement setups  

---

## ⚙️ Working Principle
The horn acts as a **transition from a waveguide to free space**.  
- The waveguide feeds electromagnetic waves into the horn.  
- The flare of the horn gradually transforms the guided wave into a radiating wave.  
- This reduces reflection and improves **impedance matching**.  

The flare dimensions determine the beamwidth, gain, and frequency performance.

---

## 📐 Specifications (from Project)
For the automation script in this repository, the horn antenna was modeled with the following parameters:

- **Base (Waveguide Section):**  
  - Dimensions: 0.4" × 0.9" × 0.315"  
  - Material: Vacuum (air-filled)  

- **Horn Aperture (Opening):**  
  - Position: (0.972", 1.325", 5.475")  
  - Size: –1.944" × –2.65"  

- **Airbox:**  
  - Surrounding space: 3" × 4" × 6"  
  - Material: Vacuum  

- **Boundaries:**  
  - Perfect E: Horn side faces  
  - Radiation: Outer Airbox  
  - Excitation: Waveport (bottom face)  

- **Simulation Setup:**  
  - Driven Modal at 10 GHz  
  - Max passes: 20  
  - Convergence ΔS: 0.02  

---

## 📊 Expected Results
When simulated in HFSS:
- **S11 parameter** should show strong return loss near 10 GHz.  
- **Radiation pattern**: Highly directive beam along the horn axis.  
- **Gain**: Typically 10–20 dB depending on flare size.  

---

## 📁 File in Repository
- Script: `src/horn_antenna_from_video.py`  
- Output Project: `horn_antenna.aedt`  

---

## ✅ Conclusion
Horn antennas are one of the most reliable antennas for high-frequency applications.  
This project demonstrates **automated design using PyAEDT**, eliminating the need for manual HFSS modeling.
