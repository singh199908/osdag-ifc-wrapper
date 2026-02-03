# Osdag IFC Wrapper - Development Report

## Methodology

### Approach
The primary goal was to develop a bridge between Osdag's PythonOCC-based geometry and the IFC format. Since Osdag's modules generate complex topological shapes (`TopoDS_Shape`), I needed a reliable way to translate these into BIM-compatible entities.

I chose to implement a custom extraction engine using `IfcOpenShell`. The core logic revolves around these stages:
1. **Model Initialization**: Setting up a standard IFC4 schema with the necessary spatial hierarchy (Project -> Site -> Building -> Storey).
2. **Geometric Translation**: To ensure maximum compatibility and avoid issues with missing high-level APIs in some environments, I implemented a triangulation-based approach. We use `BRepMesh_IncrementalMesh` to tessellate the OCC shapes and then manually reconstruct them as `IfcFacetedBrep` objects in the IFC file.
3. **Semantic Mapping**: I built a simple inference logic that looks at component names (like "Beam", "Column", "Bolt") and assigns them the correct IFC class (e.g., `IfcBeam`, `IfcMechanicalFastener`), ensuring the model is semantically rich when opened in BIM software.

## Challenges Faced

### 1. Environment and Library Versions
Developing for engineering software often involves strict version dependencies. I found that standard `IfcOpenShell` builds sometimes lack the `geom` serialization features required for direct OCC conversion. 
**Solution**: I bypassed this by writing a low-level geometry converter that works directly with vertex/index data, making the wrapper much more robust across different Python environments.

### 2. Visibility in BIM Viewers
Early versions of the exported files were valid but appeared empty in viewers like BIMvision. 
**Solution**: This was due to missing geometric representation contexts. I explicitly defined the world coordinate system and linked it to the Project entity, which fixed the camera extents and visibility.

### 3. Mesh Optimization
Finding a balance between visual detail (like screw threads or plate edges) and file size was tricky. 
**Solution**: I tuned the meshing deflection parameters in the code to provide a clean look without creating unnecessarily large files.

## References
- official Osdag documentation and source structure (https://osdag.fossee.in/)
- IfcOpenShell-Python documentation
- PythonOCC-Core examples and BRep exploration guides
- buildingSMART IFC4 schema specifications
