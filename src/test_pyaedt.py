"""
Quick sanity check for PyAEDT + Ansys HFSS.
Starts a non-graphical desktop session and closes it.
"""

from pyaedt import Hfss

def main():
    hfss = Hfss(non_graphical=True, new_desktop_session=True)
    try:
        print("✅ PyAEDT initialized. Project:", hfss.project_name, "| Design:", hfss.design_name)
        print("✅ Model units:", hfss.modeler.model_units)
    finally:
        hfss.release_desktop(close_projects=True, close_desktop=True)
        print("✅ HFSS desktop released (headless).")

if __name__ == "__main__":
    main()
