from openai import AsyncOpenAI
import re
from .constants import IMPORT_HELPER, EXTRACTION_PROMPT_JAVA, EXTRACTION_PROMPT_GO, EXTRACTION_PROMPT

async_client = AsyncOpenAI()


def identify_codeblock(completion: str) -> str:
    pattern_1 = re.compile(r"```(?:python|javascript|java|cpp|go)\n(.*?)```", re.DOTALL)
    pattern_2 = re.compile(r"```\n(.*?)```", re.DOTALL)
    matches = pattern_1.findall(completion) + pattern_2.findall(completion)

    if matches == []:
        return completion
    else:
        return matches[0]

async def remove_signature(completion, lang):
    if lang == 'java':
        extraction_prompt = EXTRACTION_PROMPT_JAVA
    elif lang == 'go':
        extraction_prompt = EXTRACTION_PROMPT_GO
    else: 
        extraction_prompt = EXTRACTION_PROMPT

    prompt = extraction_prompt + completion

    response = await async_client.responses.create(
        model='gpt-4.1-mini',
        input=prompt,
    )

    text_out = response.output[-1].content[0].text
    return text_out

async def find_code(completion, lang):
    processed = await remove_signature(completion, lang)
    processed = identify_codeblock(processed)

    return processed



def get_final_cpp(state, completion):
    imports = ''
    for s in IMPORT_HELPER['cpp']:
        if s not in state.metadata['prompt']:
            imports += s + '\n'
    
    prompt = state.metadata['prompt']
    declaration = state.metadata['declaration']
    header = declaration.strip().split('\n')[-1]
    updated_prompt = ''.join(prompt.split(header)[:-1])

    code = imports + "\n" + updated_prompt + completion + "\n" + state.metadata['test']
    
    return code

def get_final_go(state, completion):
    import_string = state.metadata['import']
    prompt = state.metadata['prompt'].replace(import_string, '')
    prompt = ''.join(prompt.split('func ')[:-1])

    test = state.metadata['test']
    test_setup = state.metadata['test_setup']
    other_pkgs = []

    for pkg in IMPORT_HELPER['go']:
        if pkg not in test_setup:
            p = pkg.split('/')[-1]
            if p + '.' in completion:    
                other_pkgs.append(f"\"{pkg}\"")
    if other_pkgs:
        import_other_pkgs = "import (\n" + "    ".join([p + "\n" for p in other_pkgs]) + ")"
        final_code = test_setup + "\n" + import_other_pkgs + "\n" + prompt + completion + "\n" + test
    else:
        final_code = test_setup + "\n" + prompt + completion + "\n" + test

    return final_code

def get_final_java(state, completion):
    prompt = state.metadata['prompt']
    prompt = ''.join(prompt.split('class Solution')[:-1])

    final_code = prompt + completion + "\n\n" + state.metadata['test'] + "\n"
    return final_code

def get_final_js(state, completion):
    prompt = state.metadata['prompt']
    prompt = ''.join(prompt.split('const ')[:-1])

    final_code = prompt + completion + "\n\n" + state.metadata['test'] + "\n"
    return final_code

def get_final_python(state, completion):
    imports = "\n".join(IMPORT_HELPER["python"]) + "\n"
    prompt = state.metadata['prompt']
    prompt = ''.join(prompt.split('def ')[:-1])

    final_code = imports + prompt + completion + "\n" + state.metadata['test'] + "\n"
    return final_code



async def get_final(state, lang, task_id):
    model_completion = state.output.completion
    processed_completion = await find_code(model_completion, lang)

    final = globals()[f'get_final_{lang}']
    final_code = final(state, processed_completion)

    if 'errormsg' in final_code:
        print(f'error in sample: {task_id}')
    
    return model_completion, processed_completion, final_code
