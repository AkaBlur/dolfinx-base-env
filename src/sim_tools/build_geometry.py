import dataclasses

import dolfinx
import dolfinx.io.gmshio as gmshio
import gmsh
from mpi4py import MPI
import numpy as np
import ufl


@dataclasses.dataclass
class GeometrySettings:
    Resolution: float
    """Resolution of the mesh a smallest feature in SI (m)"""
    Width: float
    """Width of rectangle as SI (m)"""
    Height: float
    """Height of rectangle as SI (m)"""


@dataclasses.dataclass
class GeometryMesh:
    Mesh: dolfinx.mesh.Mesh
    CellTags: dolfinx.cpp.mesh.MeshTags_int32
    FacetTags: dolfinx.cpp.mesh.MeshTags_int32


def build_rectangle(
    Settings: GeometrySettings, MeshName: str, SaveMesh: bool = False
) -> GeometryMesh:
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    # =============================================================================
    # MESHING
    # =============================================================================
    # mesh creation
    print("Generating mesh...")
    gmsh.model.add("Slab")

    Left = -1 * Settings.Width / 2
    Right = Settings.Width / 2
    Top = 0
    Bottom = -1 * Settings.Height

    # mesh points
    P1 = gmsh.model.occ.addPoint(Left, Bottom, 0, Settings.Resolution)
    P2 = gmsh.model.occ.addPoint(Right, Bottom, 0, Settings.Resolution)
    P3 = gmsh.model.occ.addPoint(Right, Top, 0, Settings.Resolution / 1e1)
    P4 = gmsh.model.occ.addPoint(Left, Top, 0, Settings.Resolution / 1e1)

    # mesh lines
    L1 = gmsh.model.occ.addLine(P1, P2)
    L2 = gmsh.model.occ.addLine(P2, P3)
    L3 = gmsh.model.occ.addLine(P3, P4)
    L4 = gmsh.model.occ.addLine(P4, P1)

    # mesh curve loop (closing loop) and rectangular surface
    C1 = gmsh.model.occ.addCurveLoop([1, 2, 3, 4])
    gmsh.model.occ.addPlaneSurface([C1])

    gmsh.model.occ.synchronize()

    # add 2D physical group for each side wall
    gmsh.model.addPhysicalGroup(2, [L1, L2, L3, L4])

    print(" Meshing")
    # generate mesh and write as file
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)

    if SaveMesh:
        print(" Writing mesh to File")
        gmsh.model.occ.synchronize()
        gmsh.write("/Rectangle_Slab.msh")

    FinishedMesh = GeometryMesh(*gmshio.model_to_mesh(gmsh.model, MPI.COMM_SELF, 0))

    FinishedMesh.Mesh.name = MeshName
    FinishedMesh.CellTags.name = f"{MeshName}_cells"
    FinishedMesh.FacetTags.name = f"{MeshName}_facets"

    return FinishedMesh


def generate_facet_markers(
    Mesh: GeometryMesh, Settings: GeometrySettings
) -> dolfinx.mesh.MeshTags:
    Bounds = [
        (1, lambda x: np.isclose(x[0], (-1 * Settings.Width / 2))),
        (2, lambda x: np.isclose(x[1], (-1 * Settings.Height))),
        (3, lambda x: np.isclose(x[0], (Settings.Width / 2))),
        (4, lambda x: np.isclose(x[1], 0.0)),
    ]

    FacetIndices, FacetMarkers = [], []
    FDim = Mesh.Mesh.topology.dim - 1
    for Marker, Locator in Bounds:
        Facets = dolfinx.mesh.locate_entities(Mesh.Mesh, FDim, Locator)
        FacetIndices.append(Facets)
        FacetMarkers.append(np.full_like(Facets, Marker))
    FacetIndices = np.hstack(FacetIndices).astype(np.int32)
    FacetMarkers = np.hstack(FacetMarkers).astype(np.int32)
    SortedFacets = np.argsort(FacetIndices)
    FacetTag = dolfinx.mesh.meshtags(
        Mesh.Mesh, FDim, FacetIndices[SortedFacets], FacetMarkers[SortedFacets]
    )

    return FacetTag


def generate_custom_differential_ds(
    Mesh: GeometryMesh, FacetTags: dolfinx.mesh.MeshTags
) -> ufl.Measure:
    ds = ufl.Measure("ds", domain=Mesh.Mesh, subdomain_data=FacetTags)
    return ds
