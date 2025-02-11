from typing import Dict
from pytrainsim.delay.primaryDelay import PrimaryDelayInjector

from pytrainsim.delay.normalDelay import NormalPrimaryDelayInjector
from pytrainsim.delay.dfDelay import DFPrimaryDelayInjector, MBDFPrimaryDelayInjector
from pytrainsim.delay.paretoDelay import ParetoPrimaryDelayInjector
from pytrainsim.delay.ensembleDelay import EnsembleDelayInjector
import pandas as pd


class DelayFactory:
    @staticmethod
    def create_delay(config: Dict) -> PrimaryDelayInjector:
        delay_type = config.pop("type", "normal")

        if delay_type == "df":
            delay_df = pd.read_csv(config.pop("path"))
            if config.pop("simulation_type", None) == "mb":
                return MBDFPrimaryDelayInjector(delay_df, **config)
            else:
                return DFPrimaryDelayInjector(delay_df, **config)
        elif delay_type == "normal":
            return NormalPrimaryDelayInjector(**config)
        elif delay_type == "pareto":
            return ParetoPrimaryDelayInjector(**config)
        elif delay_type == "ensemble":
            sub_injectors = {}
            for key in ["injector_p_1s", "injector_p", "injector_f_1s", "injector_f"]:
                sub_config = config.pop(key)
                sub_config["log"] = False  # Disable logging for sub-injectors
                sub_injectors[key] = DelayFactory.create_delay(sub_config)
            return EnsembleDelayInjector(**sub_injectors, **config)
        else:
            raise ValueError(f"Invalid delay type: {delay_type}")
