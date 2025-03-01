from experiment import create_experiment


config = {
    "general": {"name": "ocp_experiment", "simulation_type": "ocp"},
    "paths": {
        "train_schedule": "./data/mb_compatible/train_schedule.csv",
        "train_meta_data": "./data/mb_compatible/train_meta_data.json",
        "network": "./data/mb_compatible/estimated_network.xml",
    },
    "delay": {"type": "normal", "mean": 0, "std": 0, "probability": 0},
}
experiment = create_experiment(config)
experiment.run()
