import argparse
from mpi4py import MPI

# mpiexec -n 7 --oversubscribe python3 main.py --input_file data/sample_text.txt --merge_method WORKERS --test_file data/test.txt
# mpiexec -n 7 --oversubscribe python3 main.py --input_file data/sample_text.txt --merge_method MASTER --test_file data/test.txt
# mpiexec -n 4 python3 combined_project.py --input_file ./sample_text.txt --merge_method WORKERS --test_file ./test.txt

# Add command line arguments:
parser = argparse.ArgumentParser()
parser.add_argument("--input_file", type=str, help="The path of the input file")
parser.add_argument("--merge_method", type=str, help="Type of the merging")
parser.add_argument("--test_file", type=str, help="The path of the test file")
# Parse the command line arguments
args = parser.parse_args()

# CHECK - Print the values of the command line arguments
# print(f"Input file is {args.input_file}")
# print(f"Merge method is {args.merge_method}")
# print(f"Test file is {args.test_file}")

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

dict_of_worker_params = {}

if rank == 0:
    with open(args.input_file, 'r') as file:
        lines = file.readlines()
    line_count = len(lines)
    divison = line_count // (num_ranks - 1)
    lines_per_worker = [divison for i in range(num_ranks - 1)]
    remainder = line_count % (num_ranks - 1)
    for i in range(remainder):
        lines_per_worker[i] = lines_per_worker[i] + 1

    index = 0
    for worker_rank in range(1, num_ranks):  # 1, 2, ..., num_rank-1
        list_of_lines = []
        for i in range(lines_per_worker[worker_rank - 1]):
            list_of_lines.append(lines[index])
            index += 1
        dict_of_worker_params[worker_rank] = list_of_lines
        comm.send(list_of_lines, dest=worker_rank)

    frequency = {}
    if args.merge_method == "MASTER":
        for i in range(1, num_ranks):
            unigram = comm.recv(source=i, tag=1)
            frequency = merge_dict(frequency, unigram)

    elif args.merge_method == "WORKERS":
        frequency = comm.recv(source=num_ranks - 1)

    with open(args.test_file, 'r') as test_file:
        test_lines = test_file.readlines()
        for bigram in test_lines:
            unigram = bigram.split()[0]
            bigram = unigram + " " + bigram.split()[1].split("\\")[0]
            bigram_frequency = frequency[bigram]    
            unigram_frequency = frequency[unigram]  
            print(f"Frequency of the bigram {bigram} is: {bigram_frequency / unigram_frequency}")

else:
    data = comm.recv(source=0)
    number_of_lines = len(data)
    print(f"The worker with rank {rank} received {number_of_lines} sentences.")
    if args.merge_method == "MASTER":
        # Requirement 2
        unigrams = {}
        bigrams = {}
        for sentence in data:
            words = sentence.split()
            for i in range(len(words)-1):
                if words[i] in unigrams:
                    unigrams[words[i]] = unigrams[words[i]] + 1
                else:
                    unigrams[words[i]] = 1

                combination = words[i] + " " + words[i + 1]
                if combination in bigrams:
                    bigrams[combination] = bigrams[combination] + 1
                else:
                    bigrams[combination] = 1

            unigram = words[len(words)-1]
            if unigram in unigrams:
                unigrams[unigram] = unigrams[unigram] + 1
            else:
                unigrams[unigram] = 1

        dict_of_master_params = merge_dict(bigrams, unigrams)
        comm.send(dict_of_master_params, dest=0, tag=1)
        pass
    elif args.merge_method == "WORKERS":
        # Requirement 3
        frequency = {}
        if rank > 1:
            prev_frequency = comm.recv(source=rank - 1)
            frequency.update(prev_frequency)
        for sentence in data:
            my_words = sentence.split()
            word_count = len(my_words)
            for i in range(word_count - 1):
                unigram = my_words[i]
                if unigram in frequency:
                    frequency[unigram] = frequency[unigram] + 1
                else:
                    frequency[unigram] = 1
                bigram = unigram + " " + my_words[i + 1]
                if bigram in frequency:
                    frequency[bigram] = frequency[bigram] + 1
                else:
                    frequency[bigram] = 1

            unigram = my_words[word_count - 1]
            if unigram in frequency:
                frequency[unigram] = frequency[unigram] + 1
            else:
                frequency[unigram] = 1
        # print(f"For rank {rank}, frequency dictionary is\n\n{frequency}\n\n\n\n")
        if rank < num_ranks - 1:
            comm.send(frequency, dest=rank + 1)
        if rank == num_ranks - 1:
            comm.send(frequency, dest=0)
        pass