from pyaedt import Hfss
import os

# ------------------------------- User Parameters -------------------------------
ground_length = 100.0
ground_width = 60.0

substrate_length = 100.0
substrate_width = 60.0
substrate_height = 1.6
substrate_material = "FR4_epoxy"

patch_length = 30.0
patch_width = 40.0

feed_length = 20.0
feed_width = 3.0

port_width = 3.0
port_height = 1.6

rad_offset = 20.0
solution_freq = 2.45  # GHz

# ----------------------------------------------------------------------------
hfss = Hfss(specified_version="2024.1", non_graphical=False, new_desktop_session=True)

# ----------------------------------------------------------------------------
# Ground plane
ground = hfss.modeler.create_rectangle(
    origin=["-" + str(ground_length / 2) + "mm", "-" + str(ground_width / 2) + "mm", "0mm"],
    sizes=[str(ground_length) + "mm", str(ground_width) + "mm"],
    name="ground",
    material="copper",
    orientation="XY"
)

# Substrate
substrate = hfss.modeler.create_box(
    origin=["-" + str(substrate_length / 2) + "mm", "-" + str(substrate_width / 2) + "mm", "0mm"],
    sizes=[str(substrate_length) + "mm", str(substrate_width) + "mm", str(substrate_height) + "mm"],
    name="substrate",
    material=substrate_material
)

# Patch
patch = hfss.modeler.create_rectangle(
    origin=["-" + str(patch_length / 2) + "mm", "-" + str(patch_width / 2) + "mm", str(substrate_height) + "mm"],
    sizes=[str(patch_length) + "mm", str(patch_width) + "mm"],
    name="patch",
    orientation="XY"
)

# Feed line
feed = hfss.modeler.create_rectangle(
    origin=["-" + str(feed_length + feed_width / 2) + "mm", "-" + str(feed_width / 2) + "mm", str(substrate_height) + "mm"],
    sizes=[str(feed_length) + "mm", str(feed_width) + "mm"],
    name="feed",
    orientation="XY"
)

# Port sheet
port = hfss.modeler.create_rectangle(
    origin=["-" + str(feed_length + feed_width) + "mm", "-" + str(port_width / 2) + "mm", str(substrate_height) + "mm"],
    sizes=[str(port_width) + "mm", str(port_height) + "mm"],
    name="port",
    orientation="XY"
)

# Assign lumped port (safe for different PyAEDT versions)
def add_lumped_port(h):
    if hasattr(h, "lumped_port"):
        return h.lumped_port(sheet_name="port", axisdir="X", impedance=50)
    if hasattr(h, "create_lumped_port_to_sheet"):
        return h.create_lumped_port_to_sheet(sheet_name="port", axisdir="X", impedance=50)
    if hasattr(h, "assign_lumped_port_to_sheet"):
        return h.assign_lumped_port_to_sheet(sheet_name="port", axisdir="X", renormalize=True,
                                             impedance="50ohm", name="LumpedPort1")
    raise AttributeError("No lumped-port API found for this PyAEDT/HFSS version.")

add_lumped_port(hfss)

# Radiation box
rad_x = ground_length + 2 * rad_offset
rad_y = ground_width + 2 * rad_offset
rad_z = substrate_height + rad_offset

radiation_box = hfss.modeler.create_box(
    origin=["-" + str(rad_x / 2) + "mm", "-" + str(rad_y / 2) + "mm", "-" + str(rad_offset) + "mm"],
    sizes=[str(rad_x) + "mm", str(rad_y) + "mm", str(rad_z) + "mm"],
    name="radiation",
    material="air"
)

# Boundaries
hfss.assign_radiation_boundary_to_objects(["radiation"], name="RadiationBoundary")
hfss.assign_perfect_e(["patch", "ground"], name="PerfectE_BP")

# Setup
setup = hfss.create_setup("Setup1")
setup.props["Frequency"] = str(solution_freq) + "GHz"
setup.update()

# Validate and analyze
hfss.validate_full_design()
hfss.analyze()

# Save project
project_name = "MicrostripAntenna_Project"
save_path = os.path.join(os.getcwd(), project_name + ".aedt")
hfss.save_project(save_path)
hfss.release_desktop()

print("Project saved as " + save_path)
