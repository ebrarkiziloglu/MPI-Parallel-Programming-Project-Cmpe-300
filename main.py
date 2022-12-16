from mpi4py import MPI

# mpiexec -n 10 python3 main.py
rank = MPI.COMM_WORLD.Get_rank()
num_ranks = MPI.COMM_WORLD.Get_size()


# Open the file in read mode
with open("./resources/sample_text.txt", 'r') as file:        # TAKE THE INPUT NAME AS parameter instead
  lines = file.readlines()
line_count = len(lines)

print(f'Number of lines: {line_count}')
lines_per_worker = line_count // num_ranks
if line_count % num_ranks:
    lines_per_worker += 1
print(f"number of the lines per worker is {lines_per_worker}")    
