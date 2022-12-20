# Student Name: Asude Ebrar Kiziloglu
# Student Number: 2019400009
# Compile Status: Compiling
# Program Status: Working 

import argparse
from mpi4py import MPI

# Generate command line arguments:
parser = argparse.ArgumentParser()
parser.add_argument("--input_file", type=str, help="The path of the input file")
parser.add_argument("--merge_method", type=str, help="Type of the merging")
parser.add_argument("--test_file", type=str, help="The path of the test file")
args = parser.parse_args()

# Create the MPI instance:
comm = MPI.COMM_WORLD
rank = MPI.COMM_WORLD.Get_rank()
num_ranks = MPI.COMM_WORLD.Get_size()

def merge_dict(main_dict, new_dict):
    for key in new_dict:
        if key in main_dict:
            main_dict[key] = main_dict[key] + new_dict[key]
        else:
            main_dict[key] = new_dict[key]
    return main_dict

# MASTER process:
if rank == 0:  
    
    # Read the input file, divide the sentences into WORKERS and send the data:
    with open(args.input_file, 'r') as file:
        lines = file.readlines()
    line_count = len(lines)
    division = line_count // (num_ranks - 1)
    lines_per_worker = [division for i in range(num_ranks - 1)]
    remainder = line_count % (num_ranks - 1)
    for i in range(remainder):
        lines_per_worker[i] = lines_per_worker[i] + 1

    # Determine the sentences each worker will receive, and send the data to them:
    index = 0
    for worker_rank in range(1, num_ranks):  # 1, 2, ..., num_rank-1
        list_of_lines = []
        for i in range(lines_per_worker[worker_rank - 1]):
            list_of_lines.append(lines[index])
            index += 1
        comm.send(list_of_lines, dest=worker_rank)

    # Receive the data from the workers, according to the value of the --merge_method argument:
    frequency = {}
    if args.merge_method == "MASTER":
        for i in range(1, num_ranks):
            worker_frequency = comm.recv(source=i)
            frequency = merge_dict(frequency, worker_frequency)
    elif args.merge_method == "WORKERS":
        frequency = comm.recv(source=num_ranks - 1)

    # Read the test file to calculate the frequencies:
    with open(args.test_file, 'r') as test_file:
        test_lines = test_file.readlines()
        for bigram in test_lines:
            unigram = bigram.split()[0]
            bigram = unigram + " " + bigram.split()[1].split("\\")[0]
            bigram_frequency = frequency[bigram]    
            unigram_frequency = frequency[unigram]  
            print(f"Frequency of the bigram {bigram} is: {bigram_frequency / unigram_frequency}")

# Worker processes:
else:

    # Receive the data from the MASTER and calculate the frequencies:
    data = comm.recv(source=0)
    print(f"The worker with rank {rank} received {len(data)} sentences.")
    
    worker_frequency = {}
    for sentence in data:
        words = sentence.split()
        word_count = len(words)
        for i in range(word_count - 1):
            word = words[i]
            if word in worker_frequency:
                worker_frequency[word] = worker_frequency[word] + 1
            else:
                worker_frequency[word] = 1
            combination = words[i] + " " + words[i + 1]  
            if combination in worker_frequency:
                worker_frequency[combination] = worker_frequency[combination] + 1
            else:
                worker_frequency[combination] = 1
        word = words[word_count - 1]
        if word in worker_frequency:
            worker_frequency[word] = worker_frequency[word] + 1
        else:
            worker_frequency[word] = 1      

    # Send the data appropriately, according to the --merge_method argument:
    if args.merge_method == "MASTER":
        # Requirement 2
        comm.send(worker_frequency, dest=0)

    elif args.merge_method == "WORKERS":
        # Requirement 3
        if rank > 1:
            prev_frequency = comm.recv(source=rank - 1)
            worker_frequency = merge_dict(worker_frequency, prev_frequency)
        next_rank = rank + 1
        if next_rank == num_ranks:
            next_rank = 0    
        comm.send(worker_frequency, dest=next_rank)