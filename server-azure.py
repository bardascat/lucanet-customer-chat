import os
import sys

import openai
from flask import request

import constants
from flask import Flask
from flask import jsonify
from flask_cors import CORS, cross_origin


import openai, os, requests

openai.api_type = "azure"

# Azure OpenAI on your own data is only supported by the 2023-08-01-preview API version
openai.api_version = "2023-08-01-preview"

# Azure OpenAI setup
openai.api_base = "https://lucanet-gpt4.openai.azure.com/" # Add your endpoint here
openai.api_key = 'b8294436f81f48c59c3444f79b78c153'
deployment_id = "gpt-4-rpm-60" # Add your deployment ID here
# Azure Cognitive Search setup
search_endpoint = "https://customersuccesscogsearch.search.windows.net"; # Add your Azure Cognitive Search endpoint here
search_key = 'Zci8ZGllWMIkQKWTQLyzF68Q6faczA4ZcdVjJ8hyRvAzSeAE7qlG' # Add your Azure Cognitive Search admin key here
search_index_name = "custsuccessindex"; # Add your Azure Cognitive Search index name here

messages = []
def setup_byod(deployment_id: str) -> None:
    """Sets up the OpenAI Python SDK to use your own data for the chat endpoint.

    :param deployment_id: The deployment ID for the model to use with your own data.

    To remove this configuration, simply set openai.requestssession to None.
    """

    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):

        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    # Mount a custom adapter which will use the extensions endpoint for any call using the given `deployment_id`
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter()
    )

    openai.requestssession = session

setup_byod(deployment_id)





app = Flask(__name__)
CORS(app)

@app.route("/")
@cross_origin()
def hello():
    return "Hello to Lucanet Customer Success ChatBot !"

@app.route("/chat")
def chat():
  global openai
  global deployment_id
  global search_endpoint
  global search_key
  global search_index_name
  global messages
  
  prompt = request.args.get('prompt')
  print("prompt:"+ prompt)
  messages.append({"role": "user", "content": prompt})
  
  completion = openai.ChatCompletion.create(
    messages=messages,
    deployment_id=deployment_id,
    dataSources=[  # camelCase is intentional, as this is the format the API expects
        {
            "type": "AzureCognitiveSearch",
            "parameters": {
                "endpoint": search_endpoint,
                "key": search_key,
                "indexName": search_index_name,
            }
        }
    ]
)


  print(completion)


  return jsonify(
        answer=completion['choices'][0]['message']['content'],
        prompt=prompt
    )

