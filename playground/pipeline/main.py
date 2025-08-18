import os
import inspect_ai
from huggingface_hub import login
from dotenv import load_dotenv

from inspect_ai import Task, task
from inspect_ai.dataset import hf_dataset
from inspect_ai.solver import generate
from inspect_ai.model import get_model

from .scorer import main_scorer
from .utils import record_to_sample_wrapper

load_dotenv()
login(token = os.environ['HF_TOKEN'])


def run_eval(lang: str, model_args: dict, samples: tuple = (0, 164), epochs: int = 1, log_dir: str = '/root/srf-project/logs'):
    dataset = hf_dataset(
        path = 'THUDM/humaneval-x',
        name = lang,
        split = 'test',
        sample_fields = record_to_sample_wrapper(lang),
        trust = True,
    )

    @task
    def humaneval():
        return Task(
            dataset = dataset[samples[0]:samples[1]],
            solver = generate(),
            scorer = main_scorer(),
            sandbox = 'local',
        )
    
    model = get_model(**model_args)

    result = inspect_ai.eval(
        humaneval(), 
        model = model, 
        epochs = epochs,
        log_dir = log_dir,
    )

    return result


# model_args = {
#     'model': 'openai/gpt-4o-mini'
# }

# run_eval('python', model_args=model_args, samples=30)