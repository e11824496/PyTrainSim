from typing import Dict, List, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReservationLogEntry:
    trainpart_id: str
    start_time: datetime
    end_time: Union[datetime, None] = None


class ReservationRecorder:
    def __init__(self):
        self.reservation_logs: Dict[str, List[ReservationLogEntry]] = {}

    def reserve(
        self, trainpart_id: str, simulation_time: datetime
    ) -> ReservationLogEntry:
        log_entry = ReservationLogEntry(
            trainpart_id=trainpart_id, start_time=simulation_time
        )
        if trainpart_id not in self.reservation_logs:
            self.reservation_logs[trainpart_id] = []
        self.reservation_logs[trainpart_id].append(log_entry)
        return log_entry

    def release(
        self, trainpart_id: str, simulation_time: datetime
    ) -> ReservationLogEntry:
        if (
            trainpart_id not in self.reservation_logs
            or not self.reservation_logs[trainpart_id]
        ):
            raise ValueError(
                f"No active reservation found for trainpart_id: {trainpart_id}"
            )

        # Updating the most recent reservation end time
        latest_reservation = self.reservation_logs[trainpart_id][-1]
        if latest_reservation.end_time is not None:
            raise ValueError(
                f"The latest reservation for trainpart_id: {trainpart_id} is already released."
            )
        latest_reservation.end_time = simulation_time

        return latest_reservation

    def get_reservation_logs(self) -> List[Dict[str, Union[str, datetime]]]:
        logs = [
            {
                "trainpart_id": log_entry.trainpart_id,
                "start_time": log_entry.start_time,
                "end_time": log_entry.end_time,
            }
            for log_entries in self.reservation_logs.values()
            for log_entry in log_entries
        ]
        return logs

    def reset(self):
        self.reservation_logs = {}
