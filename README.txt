Osdag IFC Wrapper
=================

This project is a utility for Osdag that enables exporting 3D CAD models to the IFC (Industry Foundation Classes) format. It acts as a bridge between PythonOCC geometry and BIM-compatible workflows.

Folder Structure:
-----------------
src/osdag/cad/ifc_wrapper/
    - ifc_exporter.py    : The core wrapper logic.
Report.md                : Technical documentation on methodology and challenges.
test_wrapper.py          : A sample script demonstrating how to use the wrapper.

Requirements:
-------------
- Python 3.x
- pythonOCC (v0.17+)
- ifcopenshell (v0.7.0+)

Quick Start:
------------
1. Install the required library:
   pip install ifcopenshell

2. Usage in your code:
   from osdag.cad.ifc_wrapper.ifc_exporter import IFCWrapper
   
   # objects is a dict of {name: OCC_Shape}
   wrapper = IFCWrapper("output.ifc")
   wrapper.export(objects)

3. To run the included test:
   python test_wrapper.py

Contact:
--------
Developer: Akshat Grover
GitHub: https://github.com/singh199908
Project Link: https://github.com/singh199908/osdag-ifc-wrapper

