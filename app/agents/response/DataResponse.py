import json

from pydantic import BaseModel
from typing import List, Optional, Dict

class Form(BaseModel):
    # Define fields for the 'form' based on its expected structure.
    # Here we assume it's an empty dictionary for now, but you can expand it if necessary.
    pass

class CommonData(BaseModel):
    description: str
    state: str
    timestamp: float
    form: Form
    missFields: List[str]
    intent: str
if __name__ == '__main__':
    # Example of creating an instance of the IntentData model
    intent_data = CommonData(
        description="Great! All information is complete, let’s start searching for related projects now!",
        state="",
        timestamp=1744258518.8706527,
        form={},  # Or you can expand the form model if needed
        missFields=[],
        intent="deep_research"
    )

    # Convert the model to a Python dictionary
    intent_data_dict = intent_data.dict()

    # Print the JSON string with pretty-printing
    print(json.dumps(intent_data_dict, indent=4))