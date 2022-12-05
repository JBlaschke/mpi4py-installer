from mpi4py import MPI
from socket import gethostname

mpi_rank = MPI.COMM_WORLD.Get_rank()
mpi_size = MPI.COMM_WORLD.Get_size()
hostname = gethostname()

print(f"{mpi_rank=}, {mpi_size=}, {hostname=}")