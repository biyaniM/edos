from .voting import Voting
from .meta_classifier import MetaClassifier

from .random_forest_ensemble import RandomForestEnsemble

def get_ensemble_model(configs, logger, device):
    model_name = configs.model.ensemble.name

    if model_name == 'voting':
        model = Voting(configs, logger, device)
    elif model_name == 'meta-classifier':
        model = MetaClassifier(configs, logger, device)
    elif model_name == 'bagging_random_forest':
        model = RandomForestEnsemble(configs, logger, device)
    else:
        raise Exception('Invalid ensemble name')

    return model