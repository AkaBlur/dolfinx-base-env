import dataclasses
import numpy as np
from sim_tools import build_geometry, fem, constants
import ufl

import dolfinx
from sim_tools import materials
import ufl


@dataclasses.dataclass
class LaserSettings:
    """Settings for a general laser; Gaussian-beam, sufficiently low M²"""

    PL: float
    w0: float


class BoundaryCondition:
    def __init__(
        self,
        type,
        Marker: int,
        Values,
        FEM: fem.LagrangeFunctionSpace,
        Differential: ufl.Measure,
        Mesh: build_geometry.GeometryMesh,
        FacetTags: dolfinx.mesh.MeshTags,
    ):
        """Initializes BoundaryCondition
        Parameters:
            type:
                Type of the Condition
                Either 'Dirichlet', 'von Neumann' or 'Robin'
            Marker:
                Numerical representation of the chosen boundary to generate a condition
            Values:
                Some sort of callable function or lambda to generate values to use as boundary values
            FEM:
                Initial Finite Element function space set
            Differential:
                Custom boundary differential dS for integrating over
            Mesh:
                GeometryMesh to generate boundary conditions onto
            FacetTags:
                MeshTags which describe the mesh boundaries
        """
        self._type = type
        FDim = Mesh.Mesh.topology.dim - 1

        if type == "Dirichlet":
            u_D = dolfinx.fem.Function(FEM.FunctionSpace)
            u_D.interpolate(Values)
            Facets = FacetTags.find(Marker)
            DOFs = dolfinx.fem.locate_dofs_topological(FEM.FunctionSpace, FDim, Facets)
            self._bc = dolfinx.fem.dirichletbc(u_D, DOFs)

        elif type == "Neumann":
            self._bc = ufl.inner(Values, FEM.TestFunction) * Differential(Marker)

        elif type == "Robin":
            self._bc = (
                Values[0]
                * ufl.inner(FEM.TrialFunction - Values[1], FEM.TestFunction)
                * Differential(Marker)
            )

        else:
            raise TypeError("Unknown boundary condition: {O:s}".format(type))

    @property
    def bc(self):
        return self._bc

    @property
    def type(self):
        return self._type


###########################
##### INWARD ENERGIES #####
###########################
def inward_laser_rad(
    FEM: fem.LagrangeFunctionSpace,
    Laser: LaserSettings,
    Material: materials.MaterialOptical,
) -> ufl.SpatialCoordinate:
    I_0 = 2 * Laser.PL / (np.pi * Laser.w0**2)

    LaserRad = (
        (1 - Material.R)
        * I_0
        * ufl.exp(-2 * (FEM.SpatialCoords**2) / (Laser.w0**2))
    )

    return -1 * LaserRad


############################
##### OUTWARD ENERGIES #####
############################
def outward_radiation(
    FEM: fem.LagrangeFunctionSpace,
    Material: materials.MaterialOptical,
    RoomTemperatue: float,
):
    return (
        Material.epsilon
        * constants.StefanBoltzmannCoeff
        * (FEM.Function**4 - RoomTemperatue**4)
    )


def outward_linear_convection(
    FEM: fem.LagrangeFunctionSpace,
    ConvectionConstant: float,
    RoomTemperature: float,
):
    return ConvectionConstant * (FEM.Function - RoomTemperature)
