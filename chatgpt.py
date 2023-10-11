import os
import sys

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from flask import request

import constants
from flask import Flask


os.environ["OPENAI_API_KEY"] = "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";


# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = True
chat_history = []

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  loader = TextLoader("data/data-original.txt", autodetect_encoding=True) # Use this line if you only need data.txt
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=1),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)





app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello to Lucanet Customer Success ChatBot !"

@app.route("/chat")
def chat():
  global chain
  global chat_history

  prompt = request.args.get('prompt')
  print("prompt:"+ prompt)
  result = chain({"question": prompt, "chat_history": chat_history})
  print(result)
  chat_history.append((prompt, result['answer']))

  return result['answer']