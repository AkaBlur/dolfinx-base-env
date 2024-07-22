import dolfinx
import mpi4py.MPI as MPI

from sim_tools import fem, build_geometry


def gen_vtk_files(Path: str, FunctionSet: fem.LagrangeFunctionSpace, MeshSet: build_geometry.GeometryMesh):
    print('Writing results to file')
    with dolfinx.io.VTKFile(MPI.COMM_WORLD, Path, 'w') as OutputFile:
        OutputFile.write_mesh(MeshSet.Mesh)
        OutputFile.write_function([FunctionSet.Function._cpp_object])