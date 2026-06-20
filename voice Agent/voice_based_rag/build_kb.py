import os
import sys
import uuid
import PyPDF2
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance,VectorParams, PointStruct


COLLECTION_NAME = "knowledge_base"
QDRANT_PATH = "./qdrant_storage"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBED_DIM = 384





def get_client() -> QdrantClient:
    return QdrantClient(path=QDRANT_PATH)

def create_collection(client: QdrantClient, fresh:bool = False):
    exist = client.collection_exists(COLLECTION_NAME)

    if fresh and exist:
        client.delete_collection(COLLECTION_NAME)
        exist = False

    if not exist:
        client.create_collection(collection_name=COLLECTION_NAME,vectors_config=VectorParams(size=EMBED_DIM,distance=Distance.COSINE))
        print(f"COLLECTION {COLLECTION_NAME} created ar {QDRANT_PATH}")
    else:
        print(f"COLLECTION {COLLECTION_NAME} ALREADY EXIST AND RUNNING")


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path,"rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text = text+page_text +"\n"

    return text

def chunk_text(text, chunk_size  :int = 1000, overlap : int=200):
    chunks=[]
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if len(chunk.strip())>50:
            chunks.append(chunk)
        start = end - overlap
    return chunks
        
def upload_chunks(client:QdrantClient, model: SentenceTransformer, chunks:list, sourcename :str):

    points=[]
    for i , chunk in enumerate(chunks):
        vector = model.encode(chunk).tolist()
        points.append(PointStruct(id =str(uuid.uuid4()), vector=vector,payload = {"text":chunk,"source":sourcename,"chunk_id":i}))
    client.upsert(collection_name=COLLECTION_NAME, points=points)

    print(f"Uploaded {len(points)} chunks from {sourcename}")




def build_from_pdf(client: QdrantClient, model: SentenceTransformer, pdf_path:str):
    text = extract_text_from_pdf(pdf_path)
    print(f" Extracted {len(text)} characters")
    chunks = chunk_text(text)
    upload_chunks(client,model,chunks,os.path.basename(pdf_path))

def main():
    target = sys.argv[1]
    fresh = "--fresh" in sys.argv

    model = SentenceTransformer(EMBED_MODEL_NAME)

    client = get_client()
    create_collection(client,fresh =fresh)

    if os.path.isdir(target):
        pdfs = [ f for f in  os.listdir(target) if f.lower().endswith(".pdf")]
        if not pdfs:
            print(f"PDF not found in {target}")
            sys.exit(1)
        for fname in pdfs:
            build_from_pdf(client,model,os.path.join(target,fname))
    elif os.path.isfile(target):
        build_from_pdf(client,model,target)
    else:
        print(f"{target} is not found")
        sys.exit(1)

    count= client.count(collection_name=COLLECTION_NAME,exact=True)
    print(f"Knowledge base ready - total chunk stored in {QDRANT_PATH} is {count}")

if __name__ == "__main__":
    main()