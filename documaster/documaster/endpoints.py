import json
import os
import sys

import jsonschema
from flask import Flask, Response, request
from utils import QdrantVectorStore, process_pdf, qa_pipeline, return_error

app = Flask(__name__)

# run prior to first request
with app.app_context():
    # create temporary folder for document uploads
    try:
        path = os.path.dirname(os.path.abspath(__file__))
        upload_folder = os.path.join(path.replace("/file_folder", ""), "tmp")
        os.makedirs(upload_folder, exist_ok=True)
        app.config["upload_folder"] = upload_folder
    except Exception as e:
        app.logger.error("Could not initialize temporary upload folder")

vector_store = QdrantVectorStore()

@app.route("/documaster/upload", methods=["POST"])
def upload_file():
    try:
        pdf_file = request.files["file"]
        pdf_name = pdf_file.filename
        save_path = os.path.join(app.config.get("upload_folder"), pdf_name)
        pdf_file.save(save_path)
        
        # process pdf
        chunks = process_pdf(save_path)
        vector_store.upsert_data(chunks)
        # remove file to save space on server
        if os.path.isfile(save_path):
            os.remove(save_path)
        return Response(
            response=json.dumps({"Message": f"File uploaded: {pdf_name}"}),
            status=200,
            mimetype="application/json",
        )

    except Exception as e:
        app.logger.error(f"Error in uploading file:{e}")
        return Response(
            response=json.dumps({"Message": f"Error in uploading file : {pdf_name}: {e}"}),
            status=500,
            mimetype="application/json",
        )

@app.route("/documaster/query", methods=["POST"])
def query():
    try:
        with open(os.path.join(sys.path[0], "config/request_schema.json"), "r") as f:
            request_schema = json.loads(f.read())
    except Exception as e:
        return return_error("Error loading request_schema", e, 500)
    try:
        body = request.get_json()
    except Exception as e:
        return return_error("Content type not application/json", e, 400)
    try:
        jsonschema.validate(instance=body, schema=request_schema)
    except jsonschema.exceptions.ValidationError as e:
        return return_error(
            "Request schema does not adhere to specified schema", e, 400
        )
    try:
        # if a list of documents is not passed, then search all documents in the collection
        document_list = body.get("documents") if body.get("documents") is not None else []
        results = vector_store.search_with_filter(body.get("query"),document_list,3)
        answer = qa_pipeline(body.get("query"),results)
    except Exception as e:
        return return_error("Unable to run query against document", e, 500)
    return Response(
        response=json.dumps({"Answer": f"{answer}"}),
        status=200,
        mimetype="application/json",
    )


@app.route("/", methods=["GET"])
def heartbeat():
    """
    Receive a PDF file in a POST request.
    Check if it already exists(using a hash) in the qdrant database, if not vectorise and add it to the database
    """
    status = 200
    return Response(
        response=json.dumps({"Message": f"Running Documaster!"}),
        status=status,
        mimetype="application/json",
    )
