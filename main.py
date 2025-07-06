import warnings

warnings.filterwarnings("ignore")

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
    RecursiveJsonSplitter
)

from utils import open_file, result_info, save_to_vector_store, query_vector_store
from pprint import pprint
import json


loader = GenericLoader.from_filesystem(
    "./Zone-Transfer-Detector",
    glob="**/*",
    suffixes=[".py",],
    parser=LanguageParser(),
)

docs = loader.load()

# Adding splitting functionality for large files
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON
)

split_docs = python_splitter.split_documents(docs)

processed_docs = set()

result_json = []

for document in split_docs:
    meatadata = document.metadata
    filepath = meatadata.get("source")
    source_code = document.page_content
    if filepath not in processed_docs:
        processed_docs.add(filepath)
        node = open_file(filepath)
        result = result_info(node, filepath, source_code)
        result_json.append(result)

# save the result to a JSON file
with open("result.json", "w") as f:
    json.dump(result_json, f, indent=4)
        

with open("result.json", "r") as f:
    data = json.loads(f.read())


# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["fullpath"] = record.get("fullpath", "")
    metadata["total_functions_count"] = record.get("total_functions_count", 0)
    metadata["total_classes_count"] = record.get("total_classes_count", 0)
    return metadata


# Json loader
loader = JSONLoader(
    file_path="./result.json",
    jq_schema=".[].filename",
    content_key="source_code",
    metadata_func=metadata_func
)

json_docs = loader.load()
for doc in json_docs:
    metadata = doc.metadata
    source_code = doc.page_content


    save_to_vector_store(
        data=source_code
    )