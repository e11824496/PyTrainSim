# Delay Injection Guide

PyTrainSim allows for primary delay injection to simulate real-world disturbances in train schedules. Delays can be injected in two ways:

1. Based on a normal distribution
2. Read from a file

## Normal Distribution Delay Injection

When using normal distribution for delay injection, you can specify the mean and standard deviation of the delay distribution. This method randomly applies delays to trains based on the specified distribution.

To use this method, modify the simulation parameters in your script:

```python
simulation = Simulation(
    NormalPrimaryDelayInjector(mean, std, probability),
    network
)
```

This will inject delays with a mean of 30 seconds and a standard deviation of 10 seconds.

## File-Based Delay Injection

For more controlled delay scenarios, you can specify delays in a CSV file. This method allows you to apply specific delays to particular tasks or train parts.

### Delay File Format

Create a CSV file with the following format:

```csv
task_id,delay_seconds
task_1,30
task_2,45
task_3,60
```

- `task_id`: The identifier of the task to which the delay should be applied.
- `delay_seconds`: The delay in seconds to be applied to the specified task.
