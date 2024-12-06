# PyTrainSim [![Lint and Test Python Code](https://github.com/e11824496/PyTrainSim/actions/workflows/lintAndTest.yml/badge.svg?branch=main)](https://github.com/e11824496/PyTrainSim/actions/workflows/lintAndTest.yml)

PyTrainSim is a Python-based train simulation project using Agent Based Modeling (ABM) with Discrete Event Simulation (DES) to model railway operations and analyze delay propagation.

## Project Overview

This project aims to simulate train movements and analyze delay propagation in railway networks. It currently supports two simulation modes: a model based on Operational Control Points (OCPs) and a Moving Block system that mimics ETCS Level 3.

### Current Features

- OCP and track-based network modeling
- Moving Block system implementation
- Discrete event simulation of train movements
- Primary delay injection
- Schedule-based train operations

### Upcoming Features

- Finer granularity in track sections
- Enhanced delay propagation analysis

## Data Requirements

The project requires the following input data:

### General Requirements

1. **Train Metadata (`train_meta_data.json`)**
   - Contains metadata for each train, including the train number, train part ID, category, and UIC numbers.

2. **OCP Entries (`trains.csv`)**
   - Contains detailed Operating Control Points (OCP) entries for each train part, including scheduled and actual arrival/departure times, and calculated durations.

#### Train Metadata Format

The input train metadata should be a JSON file with the following structure:

```json
[
    "trainpart_id_1": {
        "category": "REX",
        "previous_trainparts": ["12345_0"]
    },
    ...
]
```

#### OCP Entries Format

The input OCP entries should be a CSV file with the following columns:

1. `trainpart_id`: Identifier for train parts (e.g., "12345_1")
2. `arrival_id`: ID for the Task arriving at the OCP (optional, but required if it is not the first OCP of a trainpart)
3. `stop_id`: ID for Stopping at that OCP (optional, but required if scheduled arrival and departure differ)
4. `db640_code`: Station or OCP code
5. `scheduled_arrival`: Scheduled arrival time (format: "YYYY-MM-DD HH:MM:SS")
6. `scheduled_departure`: Scheduled departure time (format: "YYYY-MM-DD HH:MM:SS")
7. `stop_duration`: Minimum stop duration (in seconds) > 0
8. `run_duration`: Minimum run duration from previous OCP to this OCP (in seconds) > 0

Optional:

- `stop`: True or False; if the OCP should be considered a stop; if not given, use scheduled_arrival and scheduled_departure to determine.

### OCP-Based Simulation

To run the OCP-based simulation, you need the `train_meta_data.json`, `trains.csv`, and a `network.json` file with the railway network data.

#### Network JSON Format

The `network.json` file should include a list of OCPs and tracks:

```json
{
    "ocps": [
        {"db640_code": "OCP1"},
        {"db640_code": "OCP2"},
        ...
    ],
    "tracks": [
        {"start": "OCP1", "end": "OCP2", "capacity": 1},
        ...
    ]
}
```

### Moving Block Simulation

To run the Moving Block simulation, you need the `train_meta_data.json`, `trains.csv`, and a `network.xml` file formatted in RailML.

#### Network XML Format

The `network.xml` should adhere to the RailML schema. It includes detailed information about OCPs and tracks, including section lengths, capacity, and maximum speed.

```xml
<root>
    <infrastructure>
        <operationControlPoints>
            <ocp id="OCP1">
                ...
                <designator register="DB640" entry="OCP1"/>
            </ocp>
            ...
        </operationControlPoints>
        <tracks>
            <track id="track1">
                ...
                <trackTopology>
                    <trackBegin pos="0">
                        <macroscopicNode ocpRef="OCP1"/>
                    </trackBegin>
                    <trackEnd pos="1000">
                        <macroscopicNode ocpRef="OCP2"/>
                    </trackEnd>
                </trackTopology>
                <trackElements>
                    <speedChanges>
                        <speedChange vMax="100"/>
                    </speedChanges>
                </trackElements>
            </track>
            ...
        </tracks>
    </infrastructure>
</root>
```

## Primary Delay Injection

Delays can be injected into the simulation based on a normal distribution or read from a file. The file should have the following format:

```csv
task_id,delay_seconds
task_1,30
task_2,45
...
```

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

4. Run the main simulation. For OCP-based simulation:

    ```bash
    poetry run python ocp_sim.py
    ```

   For Moving Block simulation:

    ```bash
    poetry run python mb_sim.py
    ```

## Current Model

### OCP-Based Model

The OCP-based model represents the railway network as a graph of OCPs (nodes) and tracks (edges). Trains traverse this network using "Drive" and "Stop" tasks, with durations derived from the input schedule.

### Moving Block Development

The Moving Block approach splits OCP-to-OCP sections into smaller chunks and performs basic acceleration and deceleration behavior using a constant factor. This approach is more dynamic and flexible, representing systems like ETCS Level 3.
