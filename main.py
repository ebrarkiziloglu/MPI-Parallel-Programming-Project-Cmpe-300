import argparse
from mpi4py import MPI

# mpiexec -n 5 --oversubscribe python3 main.py --input_file data/sample_text.txt --merge_method WORKERS --test_file data/test.txt

# Add command line arguments:
parser = argparse.ArgumentParser()
parser.add_argument("--input_file", type=str, help="The path of the input file")
parser.add_argument("--merge_method", type=str, help="Type of the merging")
parser.add_argument("--test_file", type=str, help="The path of the test file")
# Parse the command line arguments
args = parser.parse_args()

# CEHCK - Print the values of the command line arguments
print(f"Input file is {args.input_file}")
print(f"Merge method is {args.merge_method}")
print(f"Test file is {args.test_file}")

rank = MPI.COMM_WORLD.Get_rank()
num_ranks = MPI.COMM_WORLD.Get_size()

with open(args.input_file, 'r') as file: 
  lines = file.readlines()
line_count = len(lines)

print(f'Number of lines: {line_count}')
lines_per_worker = line_count // num_ranks
if line_count % num_ranks:
    lines_per_worker += 1
print(f"number of the lines per worker is {lines_per_worker}")   
if args.merge_method == "MASTER":
  # Requirement 2
  pass
elif args.merge_method == "WORKERS":
  # Requirement 3
  pass

