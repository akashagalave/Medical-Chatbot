from flask import Flask , render_template , jsonify , request
from src.helper import get_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAI
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
from src.prompt import *
import os
load_dotenv()

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')

embeddings = get_embeddings()
index_name="chatbot"

from langchain_pinecone import PineconeVectorStore

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever=docsearch.as_retriever(search_type="similarity",search_kwargs={"k":3})


llm = OpenAI(temperature=0.4,max_tokens=500)
prompt = ChatPromptTemplate(
    [
        ("system",system_prompt),
        ("human","{input}")
    ]
)


question_answer_chain=create_stuff_documents_chain(llm,prompt)
rag_chain=create_retrieval_chain(retriever,question_answer_chain)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get",methods=["GET","POST"])
def chat():
    msg=request.form["msg"]
    input=msg
    print(input)
    response = rag_chain.invoke({"input":msg})
    print("Response:",response["answer"])
    return str(response["answer"])


if __name__=='__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)

