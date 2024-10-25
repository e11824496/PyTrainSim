# PyTrainSim [![Lint and Test Python Code](https://github.com/e11824496/PyTrainSim/actions/workflows/lintAndTest.yml/badge.svg?branch=main)](https://github.com/e11824496/PyTrainSim/actions/workflows/lintAndTest.yml)

PyTrainSim is a Python-based train simulation project using Agent Based Modeling (ABM) with Discrete Event Simulation (DES) to model railway operations and analyze delay propagation.

## Project Overview

This project aims to simulate train movements and analyze delay propagation in railway networks. It currently implements a model based on Operational Control Points (OCPs) and tracks, with plans to extend to a moving block system mimicking ETCS Level 3.

### Current Features

- OCP and track-based network modeling
- Discrete event simulation of train movements
- Primary delay injection
- Schedule-based train operations

### Upcoming Features

- Moving block system implementation
- Finer granularity in track sections
- Enhanced delay propagation analysis

## Data Requirements

The project requires the following input data:

1. **Train Metadata (`train_meta_data.json`)**
   - Contains metadata for each train, including the train number, train part ID, category, and UIC numbers.

2. **OCP Entries (`ocp_entries.csv`)**
   - Contains detailed Operating Control Points (OCP) entries for each train part, including scheduled and actual arrival/departure times, and calculated durations.

### Train Metadata Format

The input train metadata should be a JSON file with the following structure:

```json
[
    {
        "trainpart_id": "12345_1",
        "category": "REX",
        "uic_numbers": [1111, 2222, 3333],
        "previous_trainparts": ["12345_0"]
    },
    ...
]
```

### OCP Entries Format

The input OCP entries should be a CSV file with the following columns:

1. `trainpart_id`: Identifier for train parts (e.g., "12345_1")
1. `arrival_id`: ID for the Task arriving at the OCP (optional, but required if it is not the first OCP of a trainpart)
1. `stop_id`: ID for Stopping at that OCP (optional, but required if schedule arrival and departure differ)
1. `db640_code`: Station or OCP code
1. `scheduled_arrival`: scheduled arrival time (format: "YYYY-MM-DD HH:MM:SS")
1. `scheduled_departure`: scheduled departure time (format: "YYYY-MM-DD HH:MM:SS")
1. `stop_duration`: min stop duration (in seconds) > 0
1. `run_duration`: min run duration from previous OCP to this OCP (in seconds) > 0

Optional:

1. 'stop': True or False; if the OCP should be considered a stop; if not given, use scheduled_arrival and scheduled_departure to determin

## Setup with Poetry

To set up the project using Poetry, follow these steps:

1. Ensure you have Poetry installed. If not, install it by following the instructions [here](https://python-poetry.org/docs/#installation).

2. Clone the repository:

    ```bash
    git clone https://github.com/e11824496/PyTrainSim.git
    cd PyTrainSim
    ```

3. Install project dependencies:

    ```bash
    poetry install
    ```

4. Run the main simulation:

    ```bash
    poetry run python main.py
    ```

## Current Model

The current model represents the railway network as a graph of OCPs (nodes) and tracks (edges). Trains traverse this network using "Drive" and "Stop" tasks, with durations derived from the input schedule. This model simplifies the network by treating each section between OCPs as a single block with limited capacity.

## Moving Block Development

A moving block approach is currently in development. This extension aims to:

- Split sections between OCPs into multiple smaller blocks (of length x)
- Allow trains to traverse these smaller blocks individually
- Implement a more dynamic and flexible train movement system
- More accurately represent systems like ETCS Level 3

This development will enable more precise simulation of train movements and potentially improve the accuracy of delay propagation analysis.
