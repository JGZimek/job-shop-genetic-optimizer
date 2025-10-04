# Job Shop Instance File Format

This document explains the required format for input data files used in the Job Shop Scheduling Problem with transport times. Use this as a reference when preparing your own test instances.

***

## File Structure

1. **First line:**
   - Two integers separated by a space: `<number_of_jobs> <number_of_machines>`

2. **For each job (repeat for number_of_jobs):**
   - One line: machine IDs for each operation (space-separated, length = number_of_machines)
   - One line: processing times for each operation (space-separated, length = number_of_machines)

3. **Transport time matrix:**
   - `number_of_machines` lines, each with `number_of_machines` integers (space-separated)
   - Entry at row `i`, column `j` is the transport time from machine `i` to machine `j`

***

## Example

```
3 3

0 1 2
5 3 4

1 2 0
6 2 3

2 0 1
4 7 5

0 2 3
2 0 1
3 1 0
```

**Explanation:**
- There are 3 jobs and 3 machines.
- For each job, the first line lists the machine sequence, the second line lists the processing times for those operations.
- The last 3 lines form a 3x3 matrix of transport times between machines.

***

**Tip:**
- Each test instance should be saved as a separate `.txt` file in the `data/instances/` directory (e.g., `instance_small.txt`, `instance_medium.txt`, `instance_large.txt`).
- Always follow this format to ensure your parser works correctly.