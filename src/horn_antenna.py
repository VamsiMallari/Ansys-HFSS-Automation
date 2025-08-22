from pyaedt import Hfss
import os
import math

# ------------------------------- Parameters (inches) -------------------------------
# Base (rectangular waveguide section)
base_origin = (-0.2, -0.45, 0.0)     # X, Y, Z (in)
base_size   = (0.4, 0.9, 0.315)      # dx, dy, dz (in)

# Funnel profiles (two rectangles to loft/taper)
# funnel_base: sits on top face of the base (z = base_origin.z + base_size.z)
fb_z = base_origin[2] + base_size[2]
funnel_base_origin = (base_origin[0], base_origin[1], fb_z)    # same x,y as base footprint
funnel_base_size   = (base_size[0],   base_size[1])            # same dx,dy as base footprint

# horn_top: positioned at given absolute coordinates, note sizes are negative (as per your summary)
horn_top_origin = (0.972, 1.325, 5.475)
horn_top_size   = (-1.944, -2.65)      # dx, dy (negative values are allowed in HFSS UI; we normalize below)

# AirBox
airbox_origin = (-1.5, -2.0, 0.0)
airbox_size   = (3.0, 4.0, 6.0)

# Analysis
solution_freq_ghz = 10.0

# ------------------------------- HFSS Session -------------------------------------
hfss = Hfss(
    specified_version="2024.1",
    non_graphical=False,
    new_desktop_session=True,
    solution_type="DrivenModal"  # ensure Driven Modal
)

# Set model units to inches
try:
    hfss.modeler.model_units = "in"
except Exception:
    # Fallback for older APIs (usually not needed in 2024.1)
    pass

# ------------------------------- Helpers ------------------------------------------
def in_str(val):
    """Format a numeric value as inches string for PyAEDT geometry calls."""
    return f"{val}in"

def rect_xy(name, origin_xyz, size_xy, material=None):
    """Create an XY-oriented rectangle sheet at a given Z height."""
    x0, y0, z0 = origin_xyz
    sx, sy = size_xy

    # HFSS/Modeler supports negative sizes, but we normalize to keep logic simple.
    # If a size is negative, shift origin and make size positive.
    if sx < 0:
        x0 = x0 + sx  # shift left
        sx = -sx
    if sy < 0:
        y0 = y0 + sy  # shift down
        sy = -sy

    rect = hfss.modeler.create_rectangle(
        origin=[in_str(x0), in_str(y0), in_str(z0)],
        sizes=[in_str(sx), in_str(sy)],
        name=name,
        orientation="XY"
    )
    if material:
        try:
            hfss.modeler.assign_material(rect.name, material)
        except Exception:
            # In modern PyAEDT, material is usually set at creation for solids.
            pass
    return rect

def box(name, origin_xyz, size_xyz, material=None):
    """Create a 3D box solid."""
    x0, y0, z0 = origin_xyz
    sx, sy, sz = size_xyz

    # Normalize negative sizes
    if sx < 0:
        x0 = x0 + sx
        sx = -sx
    if sy < 0:
        y0 = y0 + sy
        sy = -sy
    if sz < 0:
        z0 = z0 + sz
        sz = -sz

    obj = hfss.modeler.create_box(
        origin=[in_str(x0), in_str(y0), in_str(z0)],
        sizes=[in_str(sx), in_str(sy), in_str(sz)],
        name=name,
        material=material if material else None
    )
    return obj

def unite(objs, name=None):
    """Boolean unite a list of object names."""
    if not objs:
        return None
    if len(objs) == 1:
        if name and objs[0].name != name:
            hfss.modeler.rename(objs[0].name, name)
        return hfss.modeler.get_object_from_name(name or objs[0].name)
    res = hfss.modeler.unite([o.name if hasattr(o, "name") else o for o in objs])
    if name and res and res.name != name:
        hfss.modeler.rename(res.name, name)
        return hfss.modeler.get_object_from_name(name)
    return res

def make_solid_funnel(sheet1_name, sheet2_name, solid_name):
    """
    Create a solid taper between two XY rectangles using whatever API is available
    (loft/connect), then thicken if needed. Returns the resulting solid object.
    """
    # Preferred: loft
    if hasattr(hfss.modeler, "loft"):
        try:
            loft_obj = hfss.modeler.loft([sheet1_name, sheet2_name], solid=True, ruled=False, name=solid_name)
            return hfss.modeler.get_object_from_name(loft_obj.name if hasattr(loft_obj, "name") else solid_name)
        except Exception:
            pass

    # Alternative: connect (some older APIs create a surface; we then thicken)
    if hasattr(hfss.modeler, "connect"):
        try:
            conn = hfss.modeler.connect([sheet1_name, sheet2_name], new_object_name=solid_name)
            # If this resulted in a sheet, try to thicken slightly into a solid (along +Z).
            obj = hfss.modeler.get_object_from_name(solid_name)
            if obj and getattr(obj, "is_sheet", False):
                # Thicken by tiny amount (e.g., 0.001 in) to get a solid shell
                hfss.modeler.thicken_sheet(obj.name, in_str(0.001), both_sides=False)
            return hfss.modeler.get_object_from_name(solid_name)
        except Exception:
            pass

    # Fallback: try create_tapered_poly? Not commonly available; raise if nothing works.
    raise RuntimeError("Could not create funnel solid: no suitable loft/connect API found.")

def assign_radiation_to_objects(objs, name="RadiationBoundary"):
    return hfss.assign_radiation_boundary_to_objects(
        [o if isinstance(o, str) else getattr(o, "name", o) for o in objs],
        name=name
    )

def assign_perfect_e_to_faces(face_ids, name="PerfectE_HornSides"):
    """
    Assign Perfect E to a list of face IDs. Try face-specific API first,
    then fall back to object-wide if necessary.
    """
    # Preferred face-based API (varies by PyAEDT version)
    for candidate in ["assign_perfect_e_to_faces", "assign_perfect_e_to_face_list"]:
        if hasattr(hfss, candidate):
            fn = getattr(hfss, candidate)
            return fn(face_ids, name=name)

    # Fallback: assign to entire object (not ideal, but robust)
    # Callers should pass object names if using this path.
    return hfss.assign_perfect_e(face_ids, name=name)

def wave_port_on_sheet(sheet_name, port_name="WavePort1"):
    """Assign a wave port to a sheet using version-safe API names."""
    if hasattr(hfss, "wave_port"):
        return hfss.wave_port(sheet_name=sheet_name, name=port_name, num_modes=1, renormalize=True)
    if hasattr(hfss, "create_wave_port_to_sheet"):
        return hfss.create_wave_port_to_sheet(sheet_name=sheet_name, name=port_name, num_modes=1, renormalize=True)
    if hasattr(hfss, "assign_waveport_to_sheet"):
        return hfss.assign_waveport_to_sheet(sheet_name=sheet_name, name=port_name, renormalize=True, num_modes=1)
    raise AttributeError("No wave-port API found for this PyAEDT/HFSS version.")

# ------------------------------- Geometry ----------------------------------------
# 1) Base (vacuum/air solid)
base = box("Base", base_origin, base_size, material="vacuum")  # or "air"

# 2) Funnel profiles (sheets)
funnel_base = rect_xy("funnel_base", (funnel_base_origin[0], funnel_base_origin[1], funnel_base_origin[2]),
                      (funnel_base_size[0], funnel_base_size[1]))

horn_top = rect_xy("horn_top", (horn_top_origin[0], horn_top_origin[1], horn_top_origin[2]),
                   (horn_top_size[0], horn_top_size[1]))

# 3) Create funnel (solid) by lofting/connecting between the two rectangles
funnel = make_solid_funnel("funnel_base", "horn_top", "funnel")

# 4) Unite Base and funnel into one solid "Horn"
horn = unite([hfss.modeler.get_object_from_name("Base"),
              hfss.modeler.get_object_from_name("funnel")], name="Horn")

# 5) AirBox (vacuum)
airbox = box("AirBox", airbox_origin, airbox_size, material="vacuum")

# ------------------------------- Boundaries & Excitations -------------------------
# Radiation on AirBox
assign_radiation_to_objects(["AirBox"], name="Radiation_AirBox")

# Perfect E on horn side faces only (exclude top and bottom faces ~ normals ±Z)
horn_obj = hfss.modeler.get_object_from_name("Horn")
side_face_ids = []
try:
    for f in horn_obj.faces:
        # Get face normal (approx) and pick those largely horizontal (|nz| small)
        n = f.normal
        nz = n[2] if isinstance(n, (list, tuple)) and len(n) == 3 else 0.0
        if abs(nz) < 0.5:  # side faces (normals not pointing ±Z)
            side_face_ids.append(f.id)
    if side_face_ids:
        assign_perfect_e_to_faces(side_face_ids, name="PerfectE_HornSides")
    else:
        # Fallback: assign to entire horn if normals API isn't available
        hfss.assign_perfect_e(["Horn"], name="PerfectE_Horn")
except Exception:
    # Fallback if faces API not available
    hfss.assign_perfect_e(["Horn"], name="PerfectE_Horn")

# Wave port on the horn's bottom face:
# Create a sheet covering the base's bottom (XY at z=0) and use it as the port reference plane.
waveport_sheet = rect_xy(
    name="WavePortSheet",
    origin_xyz=(base_origin[0], base_origin[1], base_origin[2]),  # z=0 plane
    size_xy=(base_size[0], base_size[1]),
)
wave_port_on_sheet("WavePortSheet", port_name="WavePort1")

# ------------------------------- Setup & Solve -----------------------------------
# Setup
setup = hfss.create_setup("Setup1")
setup.props["Frequency"] = f"{solution_freq_ghz}GHz"
# Optional: if your PyAEDT keys differ, you can skip these to avoid key errors.
# setup.props["MaximumPasses"] = 20
# setup.props["MaximumDeltaS"] = 0.02
setup.update()

# Validate (2024.1)
if hasattr(hfss, "validate_full_design"):
    hfss.validate_full_design()

# Analyze
if hasattr(hfss, "analyze"):
    hfss.analyze()
else:
    # Very old fallback (unlikely on 2024.1)
    hfss.analyze_all()

# ------------------------------- Save & Close ------------------------------------
project_name = "horn_antenna"
save_path = os.path.join(os.getcwd(), project_name + ".aedt")
hfss.save_project(save_path)
hfss.release_desktop()
print("Project saved as", save_path)
