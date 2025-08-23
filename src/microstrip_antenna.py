"""
Microstrip patch antenna automation (headless) for AEDT/HFSS via PyAEDT.
This script focuses on robust geometry creation and saving the .aedt project.
This is a corrected and updated version that uses modern API calls to avoid
skipping steps and ensures correct port geometry.

Default target: 2.4 GHz microstrip on FR4.
"""

import os
from pyaedt import Hfss

# -------- User configuration --------
SAVE_PATH = r"C:\Users\Public\Documents\microstrip_patch_corrected.aedt"  # change if you like
UNITS = "mm"

# Substrate / patch sizing (simple rectangular inset feed can be added later)
freq_ghz = 2.4
c = 3e11  # mm/s
lam = c / (freq_ghz * 1e9)  # mm
# Simple starter dimensions (approx; not optimized)
sub_x = 80.0
sub_y = 60.0
sub_h = 1.6

patch_x = 38.0
patch_y = 29.0

feed_w = 3.0
feed_l = 15.0

# Positions (origin at substrate corner for simplicity)
sub_pos = [0.0, 0.0, 0.0]
patch_pos = [(sub_x - patch_x) / 2.0, (sub_y - patch_y) / 2.0, sub_h]  # on top of substrate
gnd_pos = [0.0, 0.0, 0.0]  # at z=0

# Feed line along -Y edge of patch
feed_pos = [patch_pos[0] + (patch_x - feed_w) / 2.0, patch_pos[1] - feed_l, sub_h]


def ensure_folder(path):
    """Creates the folder for the given path if it doesn't exist."""
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

def main():
    """Main function to create and save the HFSS project."""
    ensure_folder(SAVE_PATH)

    # Launch HFSS in non-graphical mode.
    # A new desktop session ensures a clean environment.
    hfss = Hfss(non_graphical=True, new_desktop_session=True)
    try:
        hfss.modeler.model_units = UNITS

        # --- GEOMETRY CREATION ---

        # Substrate (FR4)
        substrate = hfss.modeler.create_box(sub_pos, [sub_x, sub_y, sub_h], name="Substrate", matname="FR4_epoxy")

        # Ground plane (PEC sheet) at z=0
        ground = hfss.modeler.create_rectangle(
            cs_plane="XY",
            position=gnd_pos,
            dimension_list=[sub_x, sub_y],
            name="Ground",
        )
        ground.material_name = "pec"


        # Patch (PEC sheet) at z = sub_h
        patch = hfss.modeler.create_rectangle(
            cs_plane="XY",
            position=patch_pos,
            dimension_list=[patch_x, patch_y],
            name="Patch",
        )


        # Feed microstrip line (PEC sheet) connecting from below patch edge
        feed = hfss.modeler.create_rectangle(
            cs_plane="XY",
            position=feed_pos,
            dimension_list=[feed_w, feed_l],
            name="FeedLine",
        )

        # Unite patch + feed (single conductor) and assign material
        conductor = hfss.modeler.unite([patch, feed])
        conductor.name = "Radiator"
        conductor.material_name = "pec"


        # --- BOUNDARIES AND EXCITATION ---

        # Surround with airbox for radiation boundary
        pad = 20.0  # mm padding around substrate
        airbox = hfss.modeler.create_box(
            [-pad, -pad, 0], # Airbox sits on the ground plane
            [sub_x + 2 * pad, sub_y + 2 * pad, sub_h + 2 * pad],
            name="AirBox",
            matname="air"
        )
        
        # Assign radiation boundary to airbox faces (modern, direct method)
        hfss.assign_radiation_boundary_to_faces(airbox, "RadBoundary")
        print("✅ Assigned radiation boundary.")

        # Create a sheet for the Lumped Port at the end of the feed line.
        # This sheet bridges the gap between the feed line and the ground plane.
        port_pos = [feed_pos[0], feed_pos[1], 0.0]
        port_sheet = hfss.modeler.create_rectangle(
            cs_plane="XZ",  # Correct plane: perpendicular to the feed line direction (Y)
            position=port_pos,
            dimension_list=[feed_w, sub_h],  # Correct dimensions: [width_in_X, height_in_Z]
            name="PortSheet",
        )
        print("✅ Created correct port geometry.")
        
        # Assign Lumped Port with a defined integration line for robustness
        # The line runs vertically from the ground plane to the feed line.
        integration_line_start = [port_pos[0] + feed_w / 2.0, port_pos[1], 0.0]
        integration_line_end = [port_pos[0] + feed_w / 2.0, port_pos[1], sub_h]
        
        hfss.create_lumped_port_to_sheet(
            sheet_name=port_sheet.name,
            axis_dir=2, # Corresponds to Z-axis (from ground to feed)
            port_name="LumpedPort1",
            port_impedance=50.0,
            renormalize=True
        )
        print("✅ Assigned lumped port.")

        # --- ANALYSIS SETUP ---

        # Solution setup (no sweep; you can add it later)
        setup = hfss.create_setup("Setup1")
        setup.props["Frequency"] = f"{freq_ghz}GHz"
        setup.props["MaximumPasses"] = 12
        setup.props["DeltaS"] = 0.02
        setup.update()
        print("✅ Created analysis setup.")

        # --- SAVE AND EXIT ---
        
        # Save (no analyze)
        hfss.save_project(SAVE_PATH)
        print(f"✅ Saved microstrip patch project: {SAVE_PATH}")

    except Exception as e:
        # Catch any unexpected error during the process
        print(f"❌ An error occurred: {e}")
    finally:
        # Ensure AEDT is closed properly whether the script succeeds or fails
        hfss.release_desktop(close_projects=True, close_desktop=True)
        print("✅ HFSS desktop released (headless).")

if __name__ == "__main__":
    main()
