import os
import sys
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Pnt

# Ensure the wrapper can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "osdag", "cad", "ifc_wrapper")))
from ifc_exporter import IFCWrapper

def run_test():
    print("Generating sample CAD objects...")
    
    # Simulate a Beam, a Plate, and a few Bolts
    cad_objects = {
        "Beam_Main": BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 100, 1000, 200).Shape(),
        "EndPlate": BRepPrimAPI_MakeBox(gp_Pnt(-10, 0, -50), 10, 150, 300).Shape(),
        "Bolt_1": BRepPrimAPI_MakeBox(gp_Pnt(-15, 25, 25), 20, 10, 10).Shape(),
        "Bolt_2": BRepPrimAPI_MakeBox(gp_Pnt(-15, 25, 250), 20, 10, 10).Shape()
    }

    output_file = "Osdag_Sample_Export.ifc"
    print(f"Exporting to {output_file}...")
    
    try:
        wrapper = IFCWrapper(output_file)
        wrapper.export(cad_objects)
        print("Success! File generated.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_test()
