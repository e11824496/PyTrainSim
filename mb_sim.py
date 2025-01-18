from experiment import create_experiment


config = {
    "general": {"name": "mb_experiment", "simulation_type": "mb"},
    "paths": {
        "train_schedule": "./data/mb_compatible/train_schedule.csv",
        "train_meta_data": "./data/mb_compatible/train_meta_data.json",
        "network": "./data/mb_compatible/Infrastrukturmodell_AT.xml",
        "train_behavior": "./data/mb_compatible/train_behavior.json",
    },
    "mb": {
        "section_length": 500,
    },
    "delay": {"type": "normal", "mean": 0, "std": 0, "probability": 0},
}
experiment = create_experiment(config)
experiment.run()
