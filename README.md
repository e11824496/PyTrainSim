# PyTrainSim

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

### Input Data

The project requires the following input data:

1. Train schedule data (`PropagationExperiment_20221214_25.csv`)
   - Contains information about train schedules, including train numbers, scheduled and actual arrival/departure times, and categories.
2. Network data (generated from train schedule data)
3. Delay data (optional, for specific delay scenarios)

### Schedule Data Format

The input schedule data should be a CSV file with the following columns:

1. `train_number`: Unique identifier for each train
2. `db640_code`: Station or OCP code
3. `trainpart_id`: Identifier for train parts (e.g., "12345_1")
4. `scheduled_arrival`: Planned arrival time (format: "DD.MM.YYYY HH:MM:SS")
5. `scheduled_departure`: Planned departure time (format: "DD.MM.YYYY HH:MM:SS")
6. `arrival`: Actual arrival time (format: "DD.MM.YYYY HH:MM:SS")
7. `departure`: Actual departure time (format: "DD.MM.YYYY HH:MM:SS")
8. `category`: Train category (e.g., "REX", "RJ")

### Data Processing

1. `preprocessing.py` processes the raw schedule data:
   - Input: `PropagationExperiment_20221214_25.csv`
   - Output: `trains.csv` (cleaned and filtered schedule data)

2. `main.py` uses the processed data:
   - Inputs: `trains.csv`, `network.pickle` (generated network data), `delay.csv` (optional)
   - Output: Simulation results

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

4. Run the preprocessing script:

    ```bash
    poetry run python preprocessing.py
    ```

5. Run the main simulation:

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
