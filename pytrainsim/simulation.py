from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.resources.train import Train
from pytrainsim.event import StartEvent, Event
from pytrainsim.task import Task
import heapq
from typing import List


class Simulation:
    def __init__(self, tps: TrainProtectionSystem) -> None:
        self.current_time: int = 0
        self.event_queue: List[Event] = []
        self.tps = tps

    def schedule_event(self, event: Event) -> None:
        """Schedule a new event to be executed at a specific time."""
        heapq.heappush(self.event_queue, event)

    def schedule_start_event(self, time: int, task: Task) -> None:
        """Schedule a new event to be executed at a specific time."""
        event = StartEvent(self, time, task)
        heapq.heappush(self.event_queue, event)

    def schedule_train(self, train: Train):
        """Schedule the start OCP according to the schedule."""
        first_task = train.current_task()
        event = StartEvent(self, first_task.scheduled_time(), first_task)
        heapq.heappush(self.event_queue, event)

    def run(self) -> None:
        """Run the simulation by processing events in the queue."""
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            event.execute()
