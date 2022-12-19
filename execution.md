```sh
$ mpiexec -n 6 --oversubscribe python3 main.py --input_file data/sample_text.txt --merge_method WORKERS --test_file data/test.txt

$ mpiexec -n 5 --oversubscribe python3 main.py --input_file data/sample_text.txt --merge_method MASTER --test_file data/test.txt 

$ mpiexec -n 4 --oversubscribe python3 combined_project.py --input_file ./sample_text.txt --merge_method WORKERS --test_file ./test.txt
```
