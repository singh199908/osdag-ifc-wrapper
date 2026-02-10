import ifcopenshell
import logging
import uuid
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopLoc import TopLoc_Location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OsdagIFCWrapper")

class IFCWrapper:
    def __init__(self, filename="Osdag_Export.ifc"):
        self.filename = filename
        self.model = ifcopenshell.file(schema="IFC4")
        self._initialize_structure()

    def _create_guid(self):
        return ifcopenshell.guid.compress(uuid.uuid1().hex)

    def _initialize_structure(self):
        # 1. Project & Units
        self.project = self.model.createIfcProject(self._create_guid(), Name="Osdag Steel Project")
        unit = self.model.createIfcSIUnit(UnitType="LENGTHUNIT", Name="METRE", Prefix="MILLI")
        self.model.createIfcUnitAssignment(Units=[unit])

        # 2. Geometric Context (Linked to Project)
        point = self.model.createIfcCartesianPoint((0.0, 0.0, 0.0))
        axis = self.model.createIfcAxis2Placement3D(point) 
        
        self.context = self.model.createIfcGeometricRepresentationContext(
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=1e-05,
            WorldCoordinateSystem=axis
        )
        # Link context to Project
        self.project.RepresentationContexts = [self.context]

        # 3. Spatial Hierarchy
        self.site = self.model.createIfcSite(self._create_guid(), Name="Osdag Site")
        self.model.createIfcRelAggregates(self._create_guid(), RelatingObject=self.project, RelatedObjects=[self.site])
        
        self.building = self.model.createIfcBuilding(self._create_guid(), Name="Osdag Building")
        self.model.createIfcRelAggregates(self._create_guid(), RelatingObject=self.site, RelatedObjects=[self.building])
        
        self.storey = self.model.createIfcBuildingStorey(self._create_guid(), Name="Level 0")
        self.model.createIfcRelAggregates(self._create_guid(), RelatingObject=self.building, RelatedObjects=[self.storey])

    def export(self, cad_objects, filename=None):
        if filename: self.filename = filename
        for name, shape in cad_objects.items():
            self._add_shape_as_element(shape, name, self._infer_ifc_class(name))
        self.model.write(self.filename)
        logger.info(f"Exported to {self.filename}")

    def _infer_ifc_class(self, name):
        n = name.lower()
        if "beam" in n: return "IfcBeam"
        if "column" in n: return "IfcColumn"
        if "plate" in n or "gusset" in n: return "IfcPlate"
        if "bolt" in n: return "IfcMechanicalFastener"
        return "IfcBuildingElementProxy"

    def _add_shape_as_element(self, shape, name, ifc_class):
        try:
            element = getattr(self.model, f"create{ifc_class}")(self._create_guid(), Name=name)
            self.model.createIfcRelContainedInSpatialStructure(self._create_guid(), RelatingStructure=self.storey, RelatedElements=[element])
            
            # Meshing
            mesh = BRepMesh_IncrementalMesh(shape, 1.0) 
            mesh.Perform()
            
            ifc_faces = []
            explorer = TopExp_Explorer(shape, TopAbs_FACE)
            while explorer.More():
                face = explorer.Current()
                loc = TopLoc_Location()
                tri = BRep_Tool.Triangulation(face, loc)
                if tri:
                    nodes = tri.Nodes()
                    tris = tri.Triangles()
                    trans = loc.Transformation()
                    for i in range(1, tri.NbTriangles() + 1):
                        indices = tris.Value(i).Get()
                        pts = [self.model.createIfcCartesianPoint(nodes.Value(idx).Transformed(trans).Coord()) for idx in indices]
                        # Create Face
                        loop = self.model.createIfcPolyLoop(Polygon=pts)
                        bound = self.model.createIfcFaceOuterBound(Bound=loop, Orientation=True)
                        ifc_faces.append(self.model.createIfcFace(Bounds=[bound]))
                explorer.Next()

            if ifc_faces:
                shell = self.model.createIfcClosedShell(ifc_faces)
                solid = self.model.createIfcFacetedBrep(Outer=shell)
                rep = self.model.createIfcShapeRepresentation(
                    ContextOfItems=self.context,
                    RepresentationIdentifier="Body",
                    RepresentationType="FacetedBrep",
                    Items=[solid]
                )
                element.Representation = self.model.createIfcProductDefinitionShape(Representations=[rep])
        except Exception as e:
            logger.error(f"Error {name}: {e}")

def write_ifc(cad_objects, output_path):
    IFCWrapper(output_path).export(cad_objects)
