import os
from llama_index.node_parser import SentenceSplitter
from dotenv import load_dotenv
from llama_index.vector_stores import AstraDBVectorStore
import os
from llama_index import (
    StorageContext,
    VectorStoreIndex, SimpleDirectoryReader, ServiceContext
)
# from llama_parse import LlamaParse  # pip install llama-parse
from dotenv import load_dotenv
from llama_hub.smart_pdf_loader import SmartPDFLoader
import os
from glob import iglob
import certifi
# paste this at the start of code
from llama_index import Document

os.environ["SSL_CERT_FILE"] = certifi.where()

load_dotenv()

def laod_to_db(collection,file_list):
    # parser = LlamaParse(
    #     api_key=os.getenv("LLAMA_API_KEY"),  # can also be set in your env as LLAMA_CLOUD_API_KEY
    #     result_type="markdown"  # "markdown" and "text" are available
    # )
    # parser = PDFParser()
    # file_extractor = {".pdf": parser}
    for pdf_url in file_list:
        print(pdf_url)
        try:
            llmsherpa_api_url = "https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"
            pdf_loader = SmartPDFLoader(llmsherpa_api_url=llmsherpa_api_url)
            filename_fn = lambda filename: {"Ticker": filename.split('-')[0][4:], "Quarter": filename.split('-')[1], "Year": filename.split('-')[2]}
            documents = pdf_loader.load_data(pdf_url, extra_info=filename_fn(pdf_url))
            documents = [Document(text=doc.text, metadata=filename_fn(pdf_url)) for doc in documents]
            # print(f"Connected to Astra DB: {collection.get_collections()}")
            # documents = SimpleDirectoryReader('dir', file_extractor=pdf_loader, file_metadata=filename_fn).load_data()
            text_splitter = SentenceSplitter(chunk_size=200, chunk_overlap=10)
            service_context = ServiceContext.from_defaults(text_splitter=text_splitter)
            storage_context = StorageContext.from_defaults(vector_store=collection)
            index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context, service_context=service_context
            )
        except Exception as e:
            print(e, 'failed for', pdf_url)


if __name__ == '__main__':
    # astra_db_store = AstraDB(
    #     token = os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    #     api_endpoint= os.getenv("ASTRA_DB_API_ENDPOINT"),
    #     namespace="default_keyspace",
    # )
    
    db = AstraDBVectorStore(collection_name="sec_2023_ALL_ALL", token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"), api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"), namespace="default_keyspace", embedding_dimension=1536)

    rootdir_glob = 'dir/**' # Note the added asterisks
    # This will return absolute paths
    file_list = [f for f in iglob(rootdir_glob, recursive=False) if os.path.isfile(f)]
    # collection = astra_db_store.create_collection("sec_2023", dimension=1536, metric="cosine")
    # print(f"Connected to Astra DB: {collection}" )
    try:
        laod_to_db(db, file_list)
    except Exception as e:
        print(e)
    print("DONE")