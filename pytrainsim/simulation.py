from datetime import datetime
from pytrainsim.primaryDelay import PrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.event import StartEvent, Event
import heapq
from typing import List


class Simulation:
    def __init__(self, delay_injector: PrimaryDelayInjector) -> None:
        self.current_time: datetime
        self.event_queue: List[Event] = []
        self.delay_injector = delay_injector

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
