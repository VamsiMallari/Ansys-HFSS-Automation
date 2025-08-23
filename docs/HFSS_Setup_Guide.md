## HFSS + PyAEDT Setup Guide
# Step 1: Install Python 3.8 on Windows
PyAEDT works best with Python 3.7 – 3.10. We recommend Python 3.8.

1. Download Python 3.8 (64-bit) from the official site: https://www.python.org/downloads/release/python-3810/
2. During installation:
   - Select 'Add Python to PATH'
   - Choose 'Install for all users'
3. Verify installation in Command Prompt or PowerShell:
   python --version
Expected output: Python 3.8.x

# Step 2: Clone the Repository
Clone the project files into your system:

git clone https://github.com/your-username/Ansys-HFSS-Automation.git
cd Ansys-HFSS-Automation

# Step 3: Create a Python Virtual Environment
1. In the repo root:
   python -m venv ansys_env
2. Activate the environment:
   .\ansys_env\Scripts\Activate.ps1
3. Your prompt will now look like:
   (ansys_env) C:\Users\YourName\Ansys-HFSS-Automation>

If activation is blocked, run:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   
# Step 4: Install Dependencies
Use the provided requirements file:
pip install -r requirements.txt

This installs PyAEDT and its dependencies.

# Step 5: Install Ansys Electronics Desktop (HFSS)
1. Download and install Ansys Electronics Desktop (HFSS) 2021 R1 or later.
   - You can use the Student Edition if you don’t have a license.
   - Install in the default path: C:\Program Files\AnsysEM\AnsysEM21.1\Win64
2. Confirm installation by opening HFSS manually once.
3. 
# Step 6: Test PyAEDT Installation
Run:
python src\test_pyaedt.py

Expected output:
✅ PyAEDT initialized. Project: Project1 | Design: HFSSDesign1
✅ HFSS desktop released (headless).

# Step 7: Run Automation Scripts
Run the scripts to generate antenna projects:

python src\horn_antenna_from_video.py
python src\microstrip_patch.py

These save:
- horn_antenna.aedt
- microstrip_patch.aedt
  
# Step 8: Open in HFSS GUI
1. Open Ansys Electronics Desktop.
2. Load the generated .aedt files.
3. Run the simulation setup inside HFSS.
4. View results such as:
- S11 (Return Loss)
- Radiation patterns
- 3D field distributions

# Notes & Best Practices
- Scripts run in headless mode (no GUI).
- They only save the .aedt file, not simulate it.
- Always run scripts inside the virtual environment.
- If PyAEDT throws API errors, check your HFSS version.
