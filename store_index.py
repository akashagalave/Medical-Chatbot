from src.helper import load_pdf_file,text_split,get_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from tqdm import tqdm
import os
from dotenv import load_dotenv
load_dotenv()



PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')


extracted_data = load_pdf_file(data=r'C:\Final Projects\Medical-Chatbot\Data')
text_chunks=text_split(extracted_data)
embeddings = get_embeddings()



pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "chatbot"
dimension = 1536

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

vectorstore = PineconeVectorStore(
    index_name=index_name,
    embedding=embeddings
)

batch_size = 100
for i in tqdm(range(0, len(text_chunks), batch_size)):
    batch = text_chunks[i:i + batch_size]
    vectorstore.add_documents(batch)

