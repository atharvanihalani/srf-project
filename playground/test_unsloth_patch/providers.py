from inspect_ai.model._registry import modelapi

@modelapi(name="custom")
def custom():
    from .custom import CustomModelAPI

    return CustomModelAPI