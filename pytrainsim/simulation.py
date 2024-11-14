from queue import SimpleQueue
from datetime import datetime
import logging
from logging.handlers import QueueHandler, QueueListener
import sys
from pytrainsim.primaryDelay import PrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.event import StartEvent, Event
import heapq
from typing import List

LOG_LEVEL = logging.DEBUG


LOG_TO_CONSOLE = True
# performance critical if set to DEBUG
CONSOLE_LOG_LEVEL = logging.INFO


class Simulation:
    def __init__(self, delay_injector: PrimaryDelayInjector) -> None:
        self.current_time: datetime
        self.event_queue: List[Event] = []
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

    def setup_logging(self, log_file="app.log"):
        if len(logging.getLogger().handlers) == 0:
            root_logger = logging.getLogger()
            root_logger.setLevel(LOG_LEVEL)

            log_queue = SimpleQueue()

            queue_handler = QueueHandler(log_queue)
            queue_handler.setLevel(LOG_LEVEL)

            # Create handlers
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(CONSOLE_LOG_LEVEL)
            console_format = logging.Formatter("%(message)s")
            console_handler.setFormatter(console_format)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(LOG_LEVEL)
            file_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_format)

            # Add handlers to the root logger
            root_logger.addHandler(queue_handler)

            if LOG_TO_CONSOLE:
                root_logger.addHandler(console_handler)

            queue_listener = QueueListener(log_queue, file_handler)
            queue_listener.start()

            root_logger.info("Logging setup complete.")
