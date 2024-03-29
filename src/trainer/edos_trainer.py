from sklearn.metrics import classification_report, f1_score
from tqdm import tqdm

from src.trainer.trainer import Trainer


class EDOSTrainer(Trainer):
    def __init__(self, configs, state_configs, model, train_dataloader, eval_dataloader, optimizer, device, logger) -> None:
        super().__init__(configs, state_configs, model, train_dataloader, eval_dataloader, optimizer, device, logger)

    def train(self, train_dataloader):
        self.model.train()
        total_loss = 0

        for batch in tqdm(train_dataloader, desc="Training "):
            self.optimizer.zero_grad()
            pred, loss = self.model(batch)
            total_loss += loss.item()
            loss.backward()
            self.optimizer.step_optimizer()
        if self.configs.train.scheduler.name == 'reduce_lr_on_plateau': 
            f1 = self.get_training_f1(batch, pred)
            self.optimizer.step_scheduler(metrics=f1)
        else:
            self.optimizer.step_scheduler()
        return total_loss / len(train_dataloader)

    def eval(self, eval_dataloader):
        self.model.eval()
        actual_a, actual_b, actual_c = [], [], []
        predicted_a, predicted_b, predicted_c = [], [], []
        predictions = [(
            'rewire_id', 'text',
            'actual_a', 'pred_a', 'confidence_a', 'uncertainity_a',
            'actual_b', 'pred_b', 'confidence_b', 'uncertainity_b',
            'actual_c', 'pred_c', 'confidence_c', 'uncertainity_c'
        )]
        for batch in tqdm(eval_dataloader):
            pred, _ = self.model(batch, train=False)
            for i, rewire_id in enumerate(batch['rewire_id']):
                predictions.append(self.format_predictions(rewire_id, batch, pred, i))

                if 'a' in self.configs.train.task:
                    actual_a.append(batch['label_sexist'][i])
                    predicted_a.append(pred[rewire_id]['sexist'])

                if batch['label_sexist'][i] == 'sexist' and 'b' in self.configs.train.task:
                    actual_b.append(batch['label_category'][i])
                    predicted_b.append(pred[rewire_id]['category'])

                if batch['label_sexist'][i] == 'sexist' and 'c' in self.configs.train.task:
                    actual_c.append(batch['label_vector'][i])
                    predicted_c.append(pred[rewire_id]['vector'])

        scores = {
            'a': classification_report(actual_a, predicted_a, output_dict=True) if 'a' in self.configs.train.task else None,
            'b': classification_report(actual_b, predicted_b, output_dict=True) if 'b' in self.configs.train.task else None,
            'c': classification_report(actual_c, predicted_c, output_dict=True) if 'c' in self.configs.train.task else None
        }

        return scores, predictions

    def predict(self, dataset):
        pass

    def summarize_scores(self, scores):
        objective = self.configs.train.selection_objective
        self.logger.log_console(f'Summarizing objective: {objective}')
        return scores[objective]['macro avg']['f1-score']
    
    def get_training_f1(self, batch, pred):
        actual_a, predicted_a, actual_b, predicted_b, actual_c, predicted_c = [], [], [], [], [], []
        for i, rewire_id in enumerate(batch['rewire_id']):
            if 'a' in self.configs.train.task:
                actual_a.append(batch['label_sexist'][i])
                predicted_a.append(pred[rewire_id]['sexist'])

            if batch['label_sexist'][i] == 'sexist' and 'b' in self.configs.train.task:
                actual_b.append(batch['label_category'][i])
                predicted_b.append(pred[rewire_id]['category'])

            if batch['label_sexist'][i] == 'sexist' and 'c' in self.configs.train.task:
                actual_c.append(batch['label_vector'][i])
                predicted_c.append(pred[rewire_id]['vector'])
        assert len(self.configs.train.task) >= 1, "No task selected"
        f1 = 1
        for task in self.configs.train.task:
            if task == 'a':
                f1 *= f1_score(actual_a, predicted_a, average='macro')
            elif task == 'b':
                f1 *= f1_score(actual_b, predicted_b, average='macro')
            elif task == 'c':
                f1 *= f1_score(actual_c, predicted_c, average='macro')
            else:
                raise ValueError("Invalid task")
        return f1

    def format_predictions(self,rewire_id, batch, pred, i):
        return (rewire_id, batch['text'][i],
            batch['label_sexist'][i],
            pred[rewire_id]['sexist'] if 'a' in self.configs.train.task else '-',
            pred[rewire_id]['confidence']['sexist'] if 'a' in self.configs.train.task else '-',
            pred[rewire_id]['uncertainity']['sexist'] if 'a' in self.configs.train.task else '-',
            batch['label_category'][i],
            pred[rewire_id]['category'] if 'b' in self.configs.train.task else '-',
            pred[rewire_id]['confidence']['category'] if 'b' in self.configs.train.task else '-',
            pred[rewire_id]['uncertainity']['category'] if 'b' in self.configs.train.task else '-',
            batch['label_vector'][i],
            pred[rewire_id]['vector'] if 'c' in self.configs.train.task else '-',
            pred[rewire_id]['confidence']['vector'] if 'c' in self.configs.train.task else '-',
            pred[rewire_id]['uncertainity']['vector'] if 'c' in self.configs.train.task else '-')