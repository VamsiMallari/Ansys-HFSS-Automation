# Ansys HFSS Antenna Automation (Horn + Microstrip) using PyAEDT

This repository automates the **design and simulation of antennas** in **Ansys HFSS** using the **PyAEDT Python API**.  
It includes complete automation scripts for **horn antenna** and **microstrip patch antenna**, eliminating the need for manual geometry creation in HFSS.  

---

## 📌 Project Highlights
- ✅ Automates **3D geometry creation** of different antennas in HFSS  
- ✅ Designs included:
  - **Horn Antenna** → Geometry + Waveport + Airbox + Radiation setup
  - **Microstrip Patch Antenna** → Substrate + Patch + Feed + Ground plane  
- ✅ Adds **boundaries, waveports, and radiation setup**  
- ✅ Sets up analysis at chosen frequencies (10 GHz for horn, 2.4 GHz for patch)  
- ✅ Saves the complete `.aedt` project files without manual steps  
- ✅ Runs in **non-graphical (headless) mode** for automation  

# About Me
Hi, I am a B.Tech student Electronics and Communication Engineering at IIIT RGUKT-AP, RK Valley (Kadapa).

## My interests and skills include:
- Embedded Systems, IoT, and Robotics
- Programming in C, C++, Python, Arduino, and Verilog
- Hands-on experience with automation projects and electronic design
- Founder of my college Chess Club (organized multiple tournaments)
- Currently working on RF antenna design automation with Ansys HFSS

This repository is one of my projects to showcase automation + RF design expertise.
# Repository Structure
Ansys-HFSS-Automation/

│

├── src/

│   ├── horn_antenna.py       # Script to generate Horn Antenna project

│   ├── microstrip_patch.py              # Script to generate Microstrip Patch project

│   ├── test_pyaedt.py                   # Small script to verify PyAEDT setup

│

├── docs/

│   ├── HFSS_Setup_Guide.md              # Step-by-step HFSS + PyAEDT installation guide

│   ├── Horn_Antenna_Overview.md         # Overview of Horn Antenna design

│   ├── Microstrip_Antenna_Overview.md   # Overview of Microstrip Antenna design

│

├── .gitignore                           # Ignore virtual environment, cache, etc.

├── requirements.txt                     # Python dependencies (PyAEDT, etc.)

├── README.md                            # This file

├── LICENSE.md                           # Contains the details of the license information fo the software
# Projects Included
## 1. Horn Antenna Automation
- Creates horn antenna geometry (waveguide, funnel, aperture)
- Adds airbox and radiation boundary
- Defines Waveport excitation
- Sets up analysis at 10 GHz
## 2. Microstrip Patch Antenna Automation
- Creates FR4 substrate
- Defines rectangular PEC patch
- Adds feed line and ground plane
- Sets up analysis at 2.4 GHz

Both projects generate `.aedt` files that can be opened in Ansys HFSS.
# Quick Start
## 1. Setup Environment
python -m venv ansys_env
.\ansys_env\Scripts\Activate.ps1
pip install -r requirements.txt
## 2. Run Tests
python src\test_pyaedt.py
## 3. Generate Antenna Projects
python src\horn_antenna_from_video.py
python src\microstrip_patch.py
The scripts generate:
- horn_antenna.aedt
- microstrip_patch.aedt
## 4. Open in HFSS
- Load `.aedt` files into Ansys Electronics Desktop
- Run simulations inside HFSS GUI
- View S11 plots, E-field overlays, Radiation patterns
## Notes
- Scripts run in headless mode (no GUI during generation).
- They only generate the project file; you must open it in HFSS to simulate.
- Works with HFSS 2021 R1+ (Student or Licensed edition).
- Tested in Windows OS with Python 3.8.
# Contact
For queries, feel free to reach me via GitHub or my student email.
Always open to collaboration in RF Design, IoT, and Embedded Systems.

#📜 License

This project is authored by VamsiMallari (2025).
All Rights Reserved.

. You are free to view and learn from this repository for personal, educational, or research purposes.

. Redistribution, modification, sublicensing, or commercial use of this project (in whole or in part) is strictly prohibited without prior written consent from the author.

See the [LICENSE](./LICENSE) file for full terms.

