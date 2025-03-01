# PyTrainSim 🚂

[![Lint and Test Python Code](https://github.com/e11824496/PyTrainSim/actions/workflows/lintAndTest.yml/badge.svg?branch=main)](https://github.com/e11824496/PyTrainSim/actions/workflows/lintAndTest.yml)

PyTrainSim is a Python-based train simulation project using Agent Based Modeling (ABM) with Discrete Event Simulation (DES) to model railway operations and analyze delay propagation.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Simulation Modes](#simulation-modes)
- [Quick Start](#quick-start)
- [Data Requirements](#data-requirements)
- [Primary Delay Injection](#primary-delay-injection)
- [Analysis Tools](#analysis-tools)
- [License](#license)

## Overview

This project aims to simulate train movements and analyze delay propagation in railway networks. It supports two simulation modes: Fixed Block (FiBlo) and Moving Block (MoBlo), allowing for flexible modeling of different railway signaling systems.

## Features

- Fixed Block (FiBlo) and Moving Block (MoBlo) simulation modes
- Configurable simulation parameters using TOML files
- Discrete event simulation of train movements
- Primary delay injection (distribution-based or file-based)
- Schedule-based train operations

## Simulation Modes

PyTrainSim uses a multi-agent model to simulate railway operations. The model represents the rail network as a graph, where Operational Control Points (OCPs) are nodes and tracks are edges. Key entities include OCPs, track segments, and trains (active agents).

Trains execute tasks like "Drive," "Stop," "Start," and "End" to traverse the network. Each task requires available infrastructure (tracks or stations) for execution. The simulation handles task transitions and resource management through a event mechanism, ensuring proper sequencing and preventing conflicts.

### Fixed Block (FiBlo) Simulation

Represents the railway network as a graph of Operational Control Points (OCPs) and tracks. Trains move between fixed blocks, mimicking traditional signaling systems.

### Moving Block (MoBlo) Simulation

Divides tracks into smaller, configurable subsections, allowing for more dynamic train movements. This mode better represents modern signaling systems like ETCS Level 3.

Key differences:

- FiBlo uses predefined blocks, while MoBlo allows for flexible block sizes
- MoBlo offers more granular control over train movements
- Both modes use "Drive," "Stop," "Start," and "End" tasks for train operations

## Quick Start

1. Install Poetry: [Poetry Installation Guide](https://python-poetry.org/docs/#installation)
2. Clone the repository:

   ```bash
   git clone https://github.com/e11824496/PyTrainSim.git
   cd PyTrainSim
   ```

3. Install dependencies:

   ```bash
   poetry install
   ```

4. Run the simulation using a TOML configuration:

   ```bash
   poetry run python experiment.py path/to/your/config.toml
   ```

   Sample TOML configurations can be found in the `experiments/` directory.

## Data Requirements

The project requires the following input data:

1. Train Metadata (`train_meta_data.json`)
2. OCP Entries (`trains.csv`)
3. Network data (`network.xml`)
4. Train behaviour data (`train-behaviour.json` for MoBlo)

For detailed file formats, please refer to the [Data Format Documentation](./docs/data-format.md).

## Primary Delay Injection

Delays can be injected based on a normal distribution or read from a file. The delay injection method and parameters can be specified in the TOML configuration file. For file format details, see the [Delay Injection Guide](./docs/delay-injection.md).

## Analysis Tools

### Timetable Compression

Located in `viz/compression.py`, this tool performs timetable compression based on track reservations resulting from the simulation. It's an adaptation of the UIC Leaflet 406 methodology.

### Blocking Time Visualization

The `blockingtimes.py` script visualizes when trains occupy given sections based on track reservations. It displays location on the x-axis, time on the y-axis, and highlights train occupancy with blocks.

## License

This project is licensed under the [MIT License](./LICENSE).
