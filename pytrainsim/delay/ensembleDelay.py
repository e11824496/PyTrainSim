from datetime import timedelta
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.delay.primaryDelay import SaveablePrimaryDelayInjector
from pytrainsim.task import Task


class EnsembleDelayInjector(SaveablePrimaryDelayInjector):
    def __init__(
        self,
        injector_p_1s,
        injector_p,
        injector_f_1s,
        injector_f,
        log: bool = False,
        **kwargs,
    ):
        self.injector_p_1s = injector_p_1s
        self.injector_p = injector_p
        self.injector_f_1s = injector_f_1s
        self.injector_f = injector_f

        # disable logging of sub injectors:
        self.injector_p_1s.log = False
        self.injector_p.log = False
        self.injector_f_1s.log = False
        self.injector_f.log = False

        super().__init__(log)

        self.freight_categories = [
            "KLV-Ganzzug",
            "Lokzug",
            "Direktgüterzug",
            "Rollende Landstraße",
            "Verschubgüterzug",
            "Nahgüterzug",
            "SKL",
            "Ganzzug",
            "RID-Ganzzug",
            "Leerwagenganzzug",
            "Sonder-Lokzug",
            "Bedienungsfahrt",
            "Lokzug ohne Kodierung",
            "Probezug",
            "Schwergüterzug nicht manipuliert",
            "Angebotstrassen",
        ]

    def _draw_delay(self, task: Task) -> timedelta:
        delay = timedelta()
        if isinstance(task, StartTask):
            if task.train.train_category in self.freight_categories:
                delay = self.injector_f_1s.inject_delay(task)
            else:
                delay = self.injector_p_1s.inject_delay(task)
        else:
            if task.train.train_category in self.freight_categories:
                delay = self.injector_f.inject_delay(task)
            else:
                delay = self.injector_p.inject_delay(task)

        return delay
