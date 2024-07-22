from __future__ import annotations

import dataclasses
import dolfinx
import dolfinx.fem.petsc
import dolfinx.nls.petsc
import ufl
import time

import mpi4py.MPI as MPI
import petsc4py.PETSc as PETSc



@dataclasses.dataclass
class LagrangeFunctionSpace:
    FunctionSpace: dolfinx.fem.FunctionSpace
    """Main function space for problem"""
    Function: dolfinx.fem.Function
    """Main function for problem"""
    TrialFunction: ufl.TrialFunction
    """Trial function in use"""
    TestFunction: ufl.TestFunction
    """Test function in use"""
    SpatialCoords: ufl.SpatialCoordinate
    """Main spatial coordinate space"""


def init_function_spaces_var_lagrange(
    Mesh: build_geometry.GeometryMesh,
) -> LagrangeFunctionSpace:
    # function space with Lagrange type finite elements
    # variational problem initials
    # prepared for nonlinear solver using Newton-Method

    FunctionSpace = dolfinx.fem.functionspace(Mesh.Mesh, ("CG", 1))

    FunctionCollection = LagrangeFunctionSpace(
        FunctionSpace=FunctionSpace,
        Function=dolfinx.fem.Function(FunctionSpace),
        TrialFunction=ufl.TrialFunction(FunctionSpace),
        TestFunction=ufl.TestFunction(FunctionSpace),
        SpatialCoords=ufl.SpatialCoordinate(Mesh.Mesh),
    )

    return FunctionCollection


def generate_nonlinear_problem(
    Function,
    FEM: LagrangeFunctionSpace,
    BoundaryConditions: list[outside_loads.BoundaryCondition],
) -> dolfinx.fem.petsc.NonlinearProblem:
    # create the complete list of boundaries for solver
    BC = []
    for Condition in BoundaryConditions:
        if Condition.type == "Dirichlet":
            BC.append(Condition.bc)

        else:
            Function += Condition.bc

    print("Creating FEM problem")

    TimeStart = time.time()

    Jacobian = ufl.derivative(Function, FEM.Function)
    Problem = dolfinx.fem.petsc.NonlinearProblem(
        Function, FEM.Function, bcs=BC, J=Jacobian
    )

    TimeEnd = time.time()
    Delta = TimeEnd - TimeStart
    print(f" Done: {int((Delta - (Delta % 60)) / 60)} min {int(Delta % 60)} s")

    return Problem


def solve_nonlinear_problem(
    Problem: dolfinx.fem.petsc.NonlinearProblem, FEM: LagrangeFunctionSpace
):
    print("Starting FEM problem solving - Nonlinear Problem")
    TimeStart = time.time()

    Solver = dolfinx.nls.petsc.NewtonSolver(MPI.COMM_WORLD, Problem)

    Solver.convergence_criterion = "incremental"
    Solver.rtol = 1e-6
    Solver.report = True

    KSP = Solver.krylov_solver
    Opts = PETSc.Options()
    OptionPrefix = KSP.getOptionsPrefix()
    Opts[f"{OptionPrefix}ksp_type"] = "cg"
    Opts[f"{OptionPrefix}pc_type"] = "gamg"
    Opts[f"{OptionPrefix}pc_factor_mat_solver_type"] = "mumps"
    KSP.setFromOptions()

    print("Solving")

    n, converged = Solver.solve(FEM.Function)
    assert converged

    print(f"Iterations: {n}")

    TimeEnd = time.time()
    Delta = TimeEnd - TimeStart
    print(f"Solving took: {int((Delta - (Delta % 60)) / 60)} min {int(Delta % 60)} s")
