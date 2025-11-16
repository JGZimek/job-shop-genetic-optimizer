# Job Shop Instance File Format

Supported formats for Job Shop Scheduling Problem instances with transport times.

## Supported Formats

The application accepts three file formats: **TXT**, **CSV**, and **JSON** (future).

---

## TXT Format (Recommended)

**File extension:** `.txt`
**Delimiter:** space

### Structure

```
<jobs> <machines>

# Machine sequences
<machine_id> <machine_id> ... (repeated for each operation)
...

# Processing times
<time> <time> ... (repeated for each operation)
...

# Transport times
<time> <time> ... (matrix: machines × machines)
...
```

### Example (6×6)

```
6 6

# Machine sequences
3 1 2 4 0 5
3 0 2 4 5 1
3 1 2 0 4 5
1 2 3 4 5 0
1 3 2 0 5 4
2 1 0 3 4 5

# Processing times
19 9 1 6 14 11
9 5 7 11 4 3
13 4 12 12 20 9
2 15 18 4 13 3
18 10 20 12 19 7
3 2 8 10 3 8

# Transport times
0 2 7 5 8 6
3 0 6 6 4 5
2 10 0 3 9 4
3 8 7 0 5 9
4 6 1 4 0 1
6 7 5 2 4 0
```

---

## CSV Format

**File extension:** `.csv`
**Delimiter:** comma

### Structure

Identical to TXT format, but with commas instead of spaces.

### Example (6×6)

```
6,6

# Machine sequences
3,1,2,4,0,5
3,0,2,4,5,1
3,1,2,0,4,5
1,2,3,4,5,0
1,3,2,0,5,4
2,1,0,3,4,5

# Processing times
19,9,1,6,14,11
9,5,7,11,4,3
13,4,12,12,20,9
2,15,18,4,13,3
18,10,20,12,19,7
3,2,8,10,3,8

# Transport times
0,2,7,5,8,6
3,0,6,6,4,5
2,10,0,3,9,4
3,8,7,0,5,9
4,6,1,4,0,1
6,7,5,2,4,0
```

---

## JSON Format (Future Support)

**File extension:** `.json`

### Structure

```json
{
  "metadata": {
    "name": "Instance name",
    "n_jobs": 6,
    "n_machines": 6
  },
  "machine_sequences": [
    [3, 1, 2, 4, 0, 5],
    [3, 0, 2, 4, 5, 1],
    ...
  ],
  "processing_times": [
    [19, 9, 1, 6, 14, 11],
    [9, 5, 7, 11, 4, 3],
    ...
  ],
  "transport_times": [
    [0, 2, 7, 5, 8, 6],
    [3, 0, 6, 6, 4, 5],
    ...
  ]
}
```

---

## Data Specification

| Field | Description |
|-------|-------------|
| **jobs** | Number of jobs (integer) |
| **machines** | Number of machines (integer) |
| **Machine sequences** | For each job: list of machine IDs in order |
| **Processing times** | For each job: time on each machine (in order) |
| **Transport times** | Square matrix (machines × machines) with transport time from machine i to j |

---

## Constraints

- Machine IDs: 0 to `machines-1`
- All times: non-negative integers
- Transport matrix: symmetric (optional), diagonal = 0

---

## File Location

Place all instance files in: `data/instances/`

**Naming convention:**
- `instance_small_4x3.txt`
- `instance_medium_10x10.csv`
- `instance_large_20x20.json`

---

## Creating Your Own Instance

1. Define number of jobs and machines
2. Create random/realistic machine sequences
3. Define processing times (e.g., 1-20 time units)
4. Define transport times (matrix)
5. Save in chosen format

**Example (4×3):**
```
4 3

# Machine sequences
1 2 0
2 0 1
1 0 2
0 2 1

# Processing times
5 3 8
6 4 7
4 5 6
3 7 5

# Transport times
0 2 3
1 0 2
2 1 0
```

---

**v1.0** | Supported: TXT, CSV | Future: JSON