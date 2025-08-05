import subprocess
import contextlib
import shutil
import os
from inspect_ai.util import ExecResult, sandbox
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Scorer, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState
from .code_extraction import get_final

async def python_scorer(final_code, *args):
    try:
        result = await sandbox().exec(
            cmd=["python", "-c", final_code],
            timeout=30,
        )
    except TimeoutError:
        result = ExecResult(False, 1, "", "Verification timed out.")
    
    return result

async def js_scorer(final_code, *args):
    try:
        result = await sandbox().exec(
            cmd=["node", "-e", final_code],
            timeout=30,
        )
    except TimeoutError:
        result = ExecResult(False, 1, "", "Verification timed out.")

    return result

async def go_scorer(final_code, idx, tmp_dir):
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)
    file = os.path.join(tmp_dir, 'main_test.go')

    with contextlib.chdir(tmp_dir):
        open(file, 'w').write(final_code)
        if not os.path.exists('go.mod'):
            try:
                subprocess.run(
                    ['/usr/local/go/bin/go', 'mod', 'init', f'example.com/tmpmod_{idx}'],
                    check=True, 
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                print("Error running go mod init:")
                print(e.stderr)
        subprocess.run(
            ['/usr/local/go/bin/go', 'mod', 'tidy'], 
            check=True, 
            capture_output=True,
        )

    try:
        result = await sandbox().exec(
            cmd=["/usr/local/go/bin/go", "test", file],
            timeout=30,
            cwd=tmp_dir
        )
    except TimeoutError:
        result = ExecResult(False, 1, "", "Verification timed out.")

    shutil.rmtree(tmp_dir)

    return result

async def java_scorer(final_code, idx, tmp_dir):
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)
    file = os.path.join(tmp_dir, 'Main.java')

    with contextlib.chdir(tmp_dir):
        open(file, 'w').write(final_code)
    
    try:
        compile_proc = subprocess.run(
            ["javac", "Main.java"],
            cwd=tmp_dir,
            capture_output=True,
            text=True,
            timeout=30  
        )
        if compile_proc.returncode != 0:
            print(f"Compilation failed! Idx: {idx}")
            print("stderr:", compile_proc.stderr)
    except subprocess.TimeoutExpired:
        print("Compilation timed out!")
    except Exception as e:
        print("Compilation error:", e)

    try:
        result = await sandbox().exec(
            cmd=["java", "-cp", tmp_dir, "Main"],
            timeout=30,
        )
    except TimeoutError:
        result = ExecResult(False, 1, "", "Verification timed out.")

    shutil.rmtree(tmp_dir)

    return result

async def cpp_scorer(final_code, idx, tmp_dir):
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)
    file = os.path.join(tmp_dir, 'test.cpp')
    executable = os.path.join(tmp_dir, 'test.out')

    open(file, 'w').write(final_code)
    
    try:
        compile_proc = subprocess.run(
            ["g++", "-std=c++17", file, "-o", executable, '-lssl', '-lcrypto'],
            capture_output=True,
            text=True,
            timeout=30  # seconds, adjust as needed
        )
        if compile_proc.returncode != 0:
            print(f"Compilation failed! task number: {idx}")
            print("stderr:", compile_proc.stderr)
    except subprocess.TimeoutExpired:
        print("Compilation timed out!")

    if os.path.exists(executable):
        try:
            result = await sandbox().exec(
                cmd=[executable],
                timeout=30
            )
        except TimeoutError:
            result = ExecResult(False, 1, "", "Verification timed out.")
        except Exception as e:
            print(f'execution failed cuz of: {e}')
    else:
        result = ExecResult(False, 1, "", "Compiler Error")

    shutil.rmtree(tmp_dir)

    return result



def get_lang_idx(task_id: str):
    lang, idx = task_id.split('/')
    lang = lang.lower()
    if lang == 'javascript':
        lang = 'js'
    idx = int(idx)

    return lang, idx

@scorer(metrics=[accuracy(), stderr()])
def main_scorer() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        task_id = state.sample_id
        lang, idx = get_lang_idx(task_id)

        model_completion, processed_completion, final_code = await get_final(state, lang, task_id)

        tmp_dir = f'/root/srf-project/test_humaneval-x/tmp/test_{idx}/'
        my_scorer = globals()[f'{lang}_scorer']
        result = await my_scorer(final_code, idx, tmp_dir)

        success = result.success and (result.stderr == '')
        
        return Score(
            value=CORRECT if success else INCORRECT,
            explanation="".join(
                ["The following verification code was executed:\n\n"]
                + [final_code]
                + [f"\nThe submission was incorrect\n\n{result.stderr}"]
                if not result.success
                else [""]
            ),
            metadata={
                'completion': model_completion,
                'processed': processed_completion,
                'final_code': final_code,
                'idx': idx,
                'task_id': task_id,
            },
        )
    
    return score