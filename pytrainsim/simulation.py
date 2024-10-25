from datetime import datetime
import logging
import sys
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.primaryDelay import PrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.event import StartEvent, Event
import heapq
from typing import List


class Simulation:
    def __init__(
        self, tps: TrainProtectionSystem, delay_injector: PrimaryDelayInjector
    ) -> None:
        self.current_time: datetime
        self.event_queue: List[Event] = []
        self.tps = tps
        self.delay_injector = delay_injector

        self.setup_logging()

    def schedule_event(self, event: Event) -> None:
        """Schedule a new event to be executed at a specific time."""
        heapq.heappush(self.event_queue, event)

    def schedule_train(self, train: Train):
        """Schedules a train for simulation."""
        first_task = train.current_task()
        event = StartEvent(
            self, first_task.scheduled_time() - first_task.duration(), first_task
        )
        heapq.heappush(self.event_queue, event)

    def run(self) -> None:
        """Run the simulation by processing events in the queue."""
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            if hasattr(self, "current_time") and event.time < self.current_time:
                raise ValueError(
                    f"Event time {event.time} is before current time {self.current_time}: {event}, {event.task}"
                )
            self.current_time = event.time
            event.execute()

    def setup_logging(self, log_file="app.log", log_level=logging.DEBUG):
        # Create a custom logger
        logger = logging.getLogger()
        logger.setLevel(log_level)

        # Define log format
        log_format = "%(message)s"
        formatter = logging.Formatter(log_format)

        # Create handlers
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        if logger.hasHandlers():
            logger.handlers.clear()  # Clear existing handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        logger.info("Logging setup complete.")
        print(f"Logging setup complete. Logs will be written to {log_file}")
