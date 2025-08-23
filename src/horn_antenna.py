"""
Horn antenna automation (headless) for AEDT/HFSS via PyAEDT.
Builds horn geometry, assigns boundaries, adds a wave port, ADDS A SWEEP,
RUNS THE SIMULATION, EXTRACTS S11 RESULTS, and saves the .aedt project.
"""

import os
from pyaedt import Hfss
import math # Needed for log10 if calculating dB manually

# -------- User configuration --------
SAVE_PATH = r"C:\Users\Public\Documents\horn_antenna_simulated.aedt"  # New save path
UNITS = "in"
SOL_FREQ_GHZ = 10.0

# Geometry parameters (from your summary)
base_pos = [-0.2, -0.45, 0.0]
base_size = [0.4, 0.9, 0.315]
funnel_base_pos = [base_pos[0], base_pos[1], base_pos[2] + base_size[2]]
funnel_base_size = [0.4, 0.9]
horn_top_pos_given = [0.972, 1.325, 5.475]
horn_top_size_given = [-1.944, -2.65]
horn_top_x0 = min(horn_top_pos_given[0], horn_top_pos_given[0] + horn_top_size_given[0])
horn_top_y0 = min(horn_top_pos_given[1], horn_top_pos_given[1] + horn_top_size_given[1])
horn_top_z  = horn_top_pos_given[2]
horn_top_size = [abs(horn_top_size_given[0]), abs(horn_top_size_given[1])]
horn_top_pos = [horn_top_x0, horn_top_y0, horn_top_z]
airbox_pos = [-1.5, -2.0, 0.0]
airbox_size = [3.0, 4.0, 6.0]

def ensure_folder(path):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

def main():
    ensure_folder(SAVE_PATH)
    hfss = Hfss(non_graphical=True, new_desktop_session=True)
    try:
        hfss.modeler.model_units = UNITS
        base = hfss.modeler.create_box(base_pos, base_size, name="Base", matname="vacuum")
        funnel_base = hfss.modeler.create_rectangle("XY", funnel_base_pos, funnel_base_size, name="FunnelBase")
        horn_top = hfss.modeler.create_rectangle("XY", horn_top_pos, horn_top_size, name="HornTop")
        funnel = hfss.modeler.create_loft([funnel_base, horn_top], loft_cross_section="Line", name="Funnel")
        horn = hfss.modeler.unite([base, funnel], name="Horn")
        horn.material_name = "pec"
        airbox = hfss.modeler.create_box(airbox_pos, airbox_size, name="AirBox", matname="air")
        hfss.assign_radiation_boundary_to_faces(airbox.faces, "RadBoundary")
        port_face = min(base.faces, key=lambda f: f.center[2])
        hfss.create_wave_port_from_sheet(port_face, port_name="WavePort1", renormalize=True, renorm_impedance=50)

        # --- ANALYSIS SETUP ---
        setup = hfss.create_setup("Setup1")
        setup.props["Frequency"] = f"{SOL_FREQ_GHZ}GHz"
        setup.props["MaximumPasses"] = 15
        setup.props["DeltaS"] = 0.02
        setup.update()

        # --- ADDED: FREQUENCY SWEEP ---
        # To get S11 results, we need to solve over a range of frequencies.
        sweep = setup.add_sweep("Sweep1")
        sweep.props["Type"] = "Interpolating"
        sweep.props["RangeStart"] = "8GHz"
        sweep.props["RangeEnd"] = "12GHz"
        sweep.props["RangeStep"] = "0.05GHz" # Initial step, interpolating is adaptive
        sweep.props["SaveFields"] = False
        sweep.update()
        print("✅ Added frequency sweep from 8 GHz to 12 GHz.")

        # --- ADDED: RUN ANALYSIS ---
        # This command blocks the script and runs the HFSS simulation.
        print("🚀 Starting HFSS analysis... (This may take a few minutes)")
        hfss.analyze_setup(setup.name)
        print("✅ Analysis complete.")

        # --- ADDED: EXTRACT AND PRINT S11 RESULTS ---
        try:
            # Expression for S11 in decibels (dB). Port name is 'WavePort1'.
            s11_expression = "dB(S(WavePort1,WavePort1))"
            s11_data = hfss.get_solution_data(s11_expression)
            
            if s11_data:
                print("\n--- S11 (Return Loss) Results ---")
                print(f"{'Frequency (GHz)':<20} | {'S11 (dB)':<20}")
                print("-" * 45)
                # Loop through the frequency points and their corresponding S11 values
                for freq, s11_val in zip(s11_data.primary_sweep_values, s11_data.data_real()):
                    print(f"{freq:<20.4f} | {s11_val:<20.4f}")
                print("-" * 45)
            else:
                print("❌ Could not retrieve S11 data.")

        except Exception as e:
            print(f"❌ An error occurred during results extraction: {e}")

        # --- SAVE AND EXIT ---
        hfss.save_project(SAVE_PATH)
        print(f"✅ Saved horn antenna project with results: {SAVE_PATH}")

    finally:
        hfss.release_desktop(close_projects=True, close_desktop=True)
        print("✅ HFSS desktop released (headless).")

if __name__ == "__main__":
    main()
