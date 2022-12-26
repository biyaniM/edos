from parrot import Parrot
import torch
import warnings
warnings.filterwarnings("ignore")
from collections import defaultdict
from math import ceil
from tqdm import tqdm

''' 
uncomment to get reproducable paraphrase generations
def random_state(seed):
  torch.manual_seed(seed)
  if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

random_state(1234)
'''

def no_paraphrase(paraphrases):
  if len(paraphrases) == 1:
    if paraphrases[0][-1] == 0:
      return True
  return False

def generate_paraphrases(parrot,sample,zero_augmentation_patience):
  try:
    paraphrases = parrot.augment(input_phrase=sample, use_gpu=torch.cuda.is_available())
  except Exception as e:
    print(e)
    raise Exception(e)
  patience_counter = 0
  if no_paraphrase(paraphrases):
    while patience_counter<zero_augmentation_patience:
      paraphrases = parrot.augment(input_phrase=sample, use_gpu=torch.cuda.is_available())
      if not no_paraphrase(paraphrases): break
      patience_counter += 1
  
  if no_paraphrase(paraphrases): return None
  return [paraphrase for paraphrase, l in paraphrases]

def paraphraser(data:list):
  #Init models (make sure you init ONLY once if you integrate this to your code)
  parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")
  label_sexist_counter = defaultdict(int)
  for sample in data:
    label_sexist_counter[sample['label_sexist']] += 1

  max_count = max(label_sexist_counter.values())

  for label, count in label_sexist_counter.items():
    imbalance_count = max_count - count
    augmentation_multiplier = ceil(imbalance_count/count)
    augemented_sample_list = []

    if augmentation_multiplier: #* Will be 0 if label is the majority label
      for sample in tqdm(data,desc="Augmentation Progress "):
        if sample['label_sexist'] == label:
          augemented_samples = generate_paraphrases(parrot,sample,2)
          if augemented_samples is not None: augemented_sample_list.extend(augemented_samples)

      if len(augemented_sample_list)!=0: data.extend(augemented_sample_list)
    
  return data