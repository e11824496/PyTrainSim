# Data Format Documentation

## Train Metadata (`train_meta_data.json`)

This JSON file contains metadata for each train, including the train number, train part ID, category, and UIC numbers.

```json
{
    "trainpart_id_1": {
        "category": "REX",
        "previous_trainparts": ["12345_0"]
    },
    "trainpart_id_2": {
        "category": "IC",
        "previous_trainparts": []
    }
}
```

## OCP Entries (`trains.csv`)

This CSV file contains detailed Operating Control Points (OCP) entries for each train part.

Columns:

1. `trainpart_id`: Identifier for train parts (e.g., "12345_1")
2. `arrival_id`: ID for the Task arriving at the OCP (required if not the first OCP of a trainpart)
3. `stop_id`: ID for Stopping at that OCP (required if scheduled arrival and departure differ)
4. `db640_code`: Station or OCP code
5. `scheduled_arrival`: Scheduled arrival time (format: "YYYY-MM-DD HH:MM:SS")
6. `scheduled_departure`: Scheduled departure time (format: "YYYY-MM-DD HH:MM:SS")
7. `stop_duration`: Minimum stop duration (in seconds) > 0
8. `run_duration`: Minimum run duration from previous OCP to this OCP (in seconds) > 0
9. `stop` (optional): True or False; if the OCP should be considered a stop

## Network Data

### For OCP-Based Simulation (`network.json`)

```json
{
    "ocps": [
        {
            "db640_code": "OCP1",
            "latitude": 48.8566,
            "longitude": 2.3522
        },
        {
            "db640_code": "OCP2"
        }
    ],
    "tracks": [
        {
            "start": "OCP1",
            "end": "OCP2",
            "capacity": 1
        }
    ]
}
```

### For Moving Block Simulation (`network.xml`)

```xml
<root>
    <infrastructure>
        <operationControlPoints>
            <ocp id="OCP1">
                <designator register="DB640" entry="OCP1"/>
            </ocp>
        </operationControlPoints>
        <tracks>
            <track id="track1">
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
        </tracks>
    </infrastructure>
</root>
```

This XML should adhere to the RailML schema, including detailed information about OCPs and tracks, such as section lengths, capacity, and maximum speed.

## Train Behavior (`train-behaviour.json`)

This JSON file contains behavior parameters for different train categories. It defines acceleration, deceleration, and relative maximum speed for each train type. This file is only required for Moving Block (MB) simulation.

```json
{
    "Schnellbahn": {
        "acc": 0.4,
        "dec": -0.4,
        "rel_max_speed": 0.6
    },
    "Railjet": {
        "acc": 0.2,
        "dec": -0.2,
        "rel_max_speed": 0.8
    },
    ...
}
```

Fields:

- Train category (e.g., "Schnellbahn", "Railjet"): The key representing the train type.
- `acc`: Acceleration rate in m/s².
- `dec`: Deceleration rate in m/s² (typically a negative value).
- `rel_max_speed`: Relative maximum speed as a fraction of the track's maximum allowed speed.

This file allows for customization of train behavior based on their category, which can be used in Moving Block simulations to more accurately represent the performance characteristics of different train types. It is not necessary for OCP-based simulations.
