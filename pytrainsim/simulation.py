from pytrainsim.task import Task
import heapq
from typing import List
from pytrainsim.event import StartEvent, Event


class Simulation:
    def __init__(self):
        self.current_time: int = 0
        self.event_queue: List[Event] = []

    def schedule_start_event(self, time: int, task: Task) -> None:
        """Schedule a new event to be executed at a specific time."""
        event = StartEvent(time, task)
        heapq.heappush(self.event_queue, event)

    def run(self) -> None:
        """Run the simulation by processing events in the queue."""
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            try:
                event.task()
            except Exception as e:
                print(f"Error executing event at time {self.current_time}: {e}")


if __name__ == "__main__":
    sim = Simulation()

    class Task1(Task):
        def __call__(self):
            print("Task 1 executed")

    class Task2(Task):
        def __call__(self):
            print("Task 2 executed")

    sim.schedule_start_event(1, Task1())
    sim.schedule_start_event(2, Task2())

    sim.run()
