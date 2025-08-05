import gzip
import json
from inspect_ai.dataset import Sample
from .constants import HUMANEVAL_PROMPT_JAVA, HUMANEVAL_PROMPT, LANG_PREFIX

def stream_jsonl_all(filename: str):
    results = []
    fp = gzip.open(open(filename, "rb"), "rt")
    for line in fp:
        if any(not x.isspace() for x in line):
            results.append(json.loads(line))
    fp.close()

    return results

go_content = stream_jsonl_all('data/go_data.gz')


def record_to_sample_wrapper(lang):
    if lang == 'java':
        humaneval_prompt = HUMANEVAL_PROMPT_JAVA
    else:
        humaneval_prompt = HUMANEVAL_PROMPT

    def humaneval_record_to_sample(record):
        model_input = humaneval_prompt + LANG_PREFIX[lang] + '\n' + record['prompt'] 

        idx = int(record['task_id'].split('/')[-1])

        metadata = {
            "prompt": record["prompt"],
            "test": record["test"],
            "declaration": record["declaration"]
        }
        if lang == 'go':
            metadata['import'] = go_content[idx]['import']
            metadata['test_setup'] = go_content[idx]['test_setup']
        
        return Sample(
            id=record["task_id"],
            input=model_input,
            target=record["canonical_solution"],
            metadata=metadata,
        )
    
    return humaneval_record_to_sample