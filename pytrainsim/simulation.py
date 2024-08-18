from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.schedule import OCPEntry, Schedule
from pytrainsim.event import StartEvent, Event
from pytrainsim.task import Task
import heapq
from typing import Callable, List


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

    def schedule_train(self, schedule: Schedule, taskGen: Callable[[OCPEntry], Task]):
        """Schedule the start OCP according to the schedule."""
        first_ocp = next(schedule.ocp_entries())
        event = StartEvent(self, first_ocp.arrival_time, taskGen(first_ocp))
        heapq.heappush(self.event_queue, event)

    def run(self) -> None:
        """Run the simulation by processing events in the queue."""
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            event.execute()
