from src.optimizer.adafactor import AdaFactorOptimizer
from src.optimizer.adam import AdamOptimizer
from src.optimizer.adamw import AdamWOptimizer, AdamWOptimizerTorch


def get_optimizer(model, configs):
    optimizer_name = configs.train.optimizer.name
    if optimizer_name == 'Adam':
        return AdamOptimizer(model, configs.train.optimizer.lr)
    elif optimizer_name == 'Adafactor':
        return AdaFactorOptimizer(model, None)
    elif optimizer_name == 'AdamW':
        return AdamWOptimizer(model, configs)
    elif optimizer_name == 'AdamW_torch':
        print('Using torch AdamW')
        return AdamWOptimizerTorch(model, configs)
    else:
        raise ValueError(f'Optimizer {optimizer_name} is not supported')
