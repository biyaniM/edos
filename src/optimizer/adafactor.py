from transformers import Adafactor
from transformers.optimization import AdafactorSchedule

from src.optimizer.optimizer import Optimizer


class AdaFactorOptimizer(Optimizer):
    def __init__(self, model, lr=None) -> None:
        self.optimizer = Adafactor(model.parameters(), scale_parameter=True, relative_step=True, warmup_init=True, lr=lr)
        self.lr_scheduler = AdafactorSchedule(self.optimizer)

    def step(self) -> None:
        self.optimizer.step()
        self.lr_scheduler.step()

    def zero_grad(self) -> None:
        self.optimizer.zero_grad()
