import wandb

def download_wandb_artifact(artifact_name: str, download_location: str):
    api = wandb.Api()
    my_artifact = api.artifact(artifact_name, 'model')
    my_artifact.download(download_location)

