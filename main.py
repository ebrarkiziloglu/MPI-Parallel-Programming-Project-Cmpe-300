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
# print(f"Input file is {args.input_file}")
# print(f"Merge method is {args.merge_method}")
# print(f"Test file is {args.test_file}")

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_ranks = comm.Get_size()

# print(f"Number of processes is {num_ranks}")

dict_of_worker_params = {}

if rank == 0:
  with open(args.input_file, 'r') as file: 
    lines = file.readlines()
  line_count = len(lines)

  # print(f'Number of lines: {line_count}')
  lines_per_worker = line_count // (num_ranks - 1)
  if line_count % (num_ranks - 1):
      lines_per_worker += 1
  # print(f"number of the lines per worker is {lines_per_worker}")   

  for worker_rank in range(1, num_ranks):  # 1, 2, ..., num_rank-1
    list_of_lines = []
    for j in range((worker_rank-1) * lines_per_worker, worker_rank * lines_per_worker):
      if j < line_count:
        list_of_lines.append(lines[j])
    dict_of_worker_params[worker_rank] = list_of_lines
    comm.send(list_of_lines, dest = worker_rank)
  
  frequency = {}
  total_frequency = 0
  if args.merge_method == "MASTER":
    # Requirement 2
    pass
  elif args.merge_method == "WORKERS":
    frequency = comm.recv(source = num_ranks - 1)
    # print(f"In the master, frequency is: \n\n{frequency}\n\n")
    for value in frequency.values():
      total_frequency += value

  with open(args.test_file, 'r') as test_file: 
    test_lines = test_file.readlines()
    for bigram in test_lines:
      unigram = bigram.split()[0]
      bigram = unigram + " " + bigram.split()[1].split("\\")[0]
      bigram_frequency = frequency[bigram] / total_frequency
      unigram_frequency = frequency[unigram] / total_frequency
      print(f"Frequency of the bigram {bigram} is: {bigram_frequency / unigram_frequency}")

else:
  if args.merge_method == "MASTER":
    # Requirement 2
    pass
  elif args.merge_method == "WORKERS":
    # Requirement 3 - Ebrar
    lines_to_parse = comm.recv(source = 0)
    frequency = {}
    if rank > 1:
      prev_frequency = comm.recv(source = rank-1)
      frequency.update(prev_frequency)
    for sentence in lines_to_parse:
      my_words = sentence.split()
      word_count = len(my_words)
      for i in range(word_count-1):
        unigram = my_words[i]
        if unigram in frequency:
          frequency[unigram] = frequency[unigram] + 1
        else:
          frequency[unigram] = 1
        bigram = unigram + " " + my_words[i+1]
        if bigram in frequency:
          frequency[bigram] = frequency[bigram] + 1
        else:
          frequency[bigram] = 1

      unigram = my_words[word_count-1]
      if unigram in frequency:
        frequency[unigram] = frequency[unigram] + 1
      else:
        frequency[unigram] = 1
    # print(f"For rank {rank}, frequency dictionary is\n\n{frequency}\n\n\n\n")
    if rank < num_ranks - 1:
      comm.send(frequency, dest = rank+1)
    if rank == num_ranks - 1:
      comm.send(frequency, dest = 0)  
    pass

