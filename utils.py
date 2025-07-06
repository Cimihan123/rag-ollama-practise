# pip install -qU "langchain-chroma>=0.1.2"
import ast
from langchain_community.vectorstores import SQLiteVec
from langchain_ollama import OllamaEmbeddings

import json

def save_to_vector_store(data):
    embedding_function = OllamaEmbeddings(model="llama3",)
    connection = SQLiteVec.create_connection("test.db")
    db = SQLiteVec(
        table="vector_store",
        embedding=embedding_function,
        connection=connection
    )

    db.add_texts(
        texts=[json.dumps(data)],
    )
    return db

def query_vector_store(query, db):
    results = db.similarity_search(query, k=5)
    return results


def open_file(file_path):
    with open(file_path, 'r') as file:
        file_node = ast.parse(file.read())
    return file_node

def show_info(function_node):
    function_rep = function_node.name + '('
    
    for arg in function_node.args.args:
        function_rep += arg.arg + ', '
    
    function_rep = function_rep.rstrip(', ')
    function_rep += ')'

    return function_rep

def result_info(node, filepath, source_code):
    func_count = 0
    class_count = 0
    
    result = {
        "filename": {
            "fullpath": filepath,
            "objects": {
                "classes": [],
                "functions": []
            },
            "source_code": source_code,
            "total_functions_count": 0,
            "total_classes_count": 0,
        } 
    }

    # Collect functions and classes
    functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
    classes = [n for n in node.body if isinstance(n, ast.ClassDef)]

    # Process functions
    for function in functions:
        function_info = show_info(function)
        result["filename"]["objects"]["functions"].append(function_info)
        func_count += 1

    # Process classes
    for class_ in classes:
        class_info = {
            "class_name": class_.name,
            "methods": []
        }

        # Collect methods belonging to the class
        methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
        for method in methods:
            method_info = show_info(method)
            class_info["methods"].append(method_info)
        
        result["filename"]["objects"]["classes"].append(class_info)
        class_count += 1

    # Update counts in result
    result["filename"]["total_functions_count"] = func_count
    result["filename"]["total_classes_count"] = class_count

    return result