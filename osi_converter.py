
import os
import sys
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Pnt
import logging

# Setup pathing to import the ifc_exporter script
# We are currently in c:\Users\aksha\Desktop\osdag\osdag_ifc_wrapper
# ifc_exporter.py is in src\osdag\cad\ifc_wrapper\ifc_exporter.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "osdag", "cad", "ifc_wrapper")))
from ifc_exporter import IFCWrapper

logging.basicConfig(level=logging.INFO)

def create_mock_i_beam(origin, length=500, height=200, width=100, flange_thk=10, web_thk=6):
    """Standard I-Beam mock"""
    p = origin
    return [
        # Bottom Flange
        BRepPrimAPI_MakeBox(gp_Pnt(p.X(), p.Y(), p.Z()), width, length, flange_thk).Shape(),
        # Top Flange
        BRepPrimAPI_MakeBox(gp_Pnt(p.X(), p.Y(), p.Z() + height - flange_thk), width, length, flange_thk).Shape(),
        # Web
        BRepPrimAPI_MakeBox(gp_Pnt(p.X() + (width-web_thk)/2, p.Y(), p.Z() + flange_thk), web_thk, length, height - 2*flange_thk).Shape()
    ]

def create_mock_angle(origin, length=500, leg1=50, leg2=50, thk=5):
    """Standard Angle mock"""
    p = origin
    return [
        # Leg 1
        BRepPrimAPI_MakeBox(gp_Pnt(p.X(), p.Y(), p.Z()), leg1, length, thk).Shape(),
        # Leg 2
        BRepPrimAPI_MakeBox(gp_Pnt(p.X(), p.Y(), p.Z()), thk, length, leg2).Shape()
    ]

def run_suite():
    # Mapping modules to filenames
    tasks = [
        ("BCEndplate", "Beam-to-column-EPC.osi", ["Column", "Beam", "EndPlate", "Bolts"]),
        ("CCSpliceCoverPlateCAD", "Column-to-column-CPW.osi", ["Column_Bottom", "Column_Top", "SplicePlate_Web", "SplicePlate_Flange"]),
        ("BBCad", "Beam-to-beam-CPB.osi", ["Beam_Left", "Beam_Right", "CoverPlate_Top", "CoverPlate_Bottom", "Bolts"]),
        ("Tension", "Tension-bolted-to-end-gusset.osi", ["AngleMember", "GussetPlate", "Bolts"])
    ]

    for module_name, osi_file, components in tasks:
        print(f"\n--- Testing Wrapper for Module: {module_name} (Input: {osi_file}) ---")
        cad_objects = {}
        
        if module_name == "BCEndplate":
            # beam connected to column flange via end plate
            # Column
            for i, s in enumerate(create_mock_i_beam(gp_Pnt(0,0,0), length=1000, height=300, width=250)): 
                cad_objects[f"Column_Part_{i}"] = s
            # Beam (attached to column flange at y=0, z~500)
            # offset roughly by column width/2 if column centered, but here simple placement
            for i, s in enumerate(create_mock_i_beam(gp_Pnt(260, 0, 400), length=500, height=200, width=100)): 
                cad_objects[f"Beam_Part_{i}"] = s
            # End Plate
            cad_objects["EndPlate"] = BRepPrimAPI_MakeBox(gp_Pnt(250, -10, 390), 10, 120, 220).Shape()
            # Bolts
            cad_objects["Bolt_1"] = BRepPrimAPI_MakeBox(gp_Pnt(255, 20, 420), 20, 10, 10).Shape()
            cad_objects["Bolt_2"] = BRepPrimAPI_MakeBox(gp_Pnt(255, 80, 420), 20, 10, 10).Shape()
            cad_objects["Bolt_3"] = BRepPrimAPI_MakeBox(gp_Pnt(255, 20, 560), 20, 10, 10).Shape()
            cad_objects["Bolt_4"] = BRepPrimAPI_MakeBox(gp_Pnt(255, 80, 560), 20, 10, 10).Shape()
            
        elif module_name == "CCSpliceCoverPlateCAD":
            # Column on top of Column
            for i, s in enumerate(create_mock_i_beam(gp_Pnt(0,0,0), length=1000, height=300, width=250)): 
                cad_objects[f"Col_Bottom_{i}"] = s
            for i, s in enumerate(create_mock_i_beam(gp_Pnt(0,1005,0), length=1000, height=300, width=250)): 
                cad_objects[f"Col_Top_{i}"] = s
            # Splice Plates (Flange)
            cad_objects["Splice_Flange_1"] = BRepPrimAPI_MakeBox(gp_Pnt(-10, 800, 0), 20, 400, 300).Shape()
            cad_objects["Splice_Flange_2"] = BRepPrimAPI_MakeBox(gp_Pnt(240, 800, 0), 20, 400, 300).Shape()

        elif module_name == "BBCad":
            # Beam to Beam
            for i, s in enumerate(create_mock_i_beam(gp_Pnt(0,0,0), length=1000, height=300, width=150)): 
                cad_objects[f"Beam_Left_{i}"] = s
            for i, s in enumerate(create_mock_i_beam(gp_Pnt(0,1005,0), length=1000, height=300, width=150)): 
                cad_objects[f"Beam_Right_{i}"] = s
            # Cover Plate (Top Flange)
            cad_objects["CoverPlate_Top"] = BRepPrimAPI_MakeBox(gp_Pnt(0, 800, 300), 150, 400, 10).Shape()
            # Bolts
            cad_objects["Bolt_1"] = BRepPrimAPI_MakeBox(gp_Pnt(20, 850, 305), 10, 10, 20).Shape()
            cad_objects["Bolt_2"] = BRepPrimAPI_MakeBox(gp_Pnt(120, 850, 305), 10, 10, 20).Shape()
            
        elif module_name == "Tension":
            # Gusset Plate
            cad_objects["GussetPlate"] = BRepPrimAPI_MakeBox(gp_Pnt(0,0,0), 10, 500, 300).Shape()
            # Angle Member
            for i, s in enumerate(create_mock_angle(gp_Pnt(10, 50, 50), length=600, leg1=60, leg2=60)):
                cad_objects[f"AngleMember_{i}"] = s
            # Bolts
            cad_objects["Bolt_1"] = BRepPrimAPI_MakeBox(gp_Pnt(5, 100, 80), 20, 10, 10).Shape()
            cad_objects["Bolt_2"] = BRepPrimAPI_MakeBox(gp_Pnt(5, 200, 80), 20, 10, 10).Shape()

        output_file = f"Osdag_Output_{module_name}.ifc"
        try:
            wrapper = IFCWrapper(output_file)
            wrapper.export(cad_objects)
            print(f"SUCCESS: Generated {output_file}")
        except Exception as e:
            print(f"ERROR generating {output_file}: {e}")

if __name__ == "__main__":
    run_suite()
