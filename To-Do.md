### Code File:
* Configure the MPI environment
* ~~Read the program arguments: there are 3 of them~~
* ~~Read the input file~~
* ~~Count the number of lines in the file~~
* ~~Divide the input lines equally to the workers (an example is given in parallel_loop.py)~~
* Each worker will print its rank and number of lines it received
* Each worker will read its lines and will count the number of unigrams and bigrams
* Each worker will send the resultant count (dictionary?) to somewhere, according to the '--merge_method' argument's value 
* The master process will receive all of the statistics
* The master process will read lines from the input test file and compute the probabilities
### Report File
* Write a Project report according to the "Programming Project Documentation" given in [this website](cmpe.boun.edu.tr/~gungort/informationstudents.htm).
### Individiaul Work Files
* Write your own