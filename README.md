# Documaster 

## Overview 
This API has two endpoints. 

    1. POST /documaster/upload

    This allows us to upload a PDF file to be parsed and indexed, supplied as a file argument with the request. No additional parameters need to be passed, like here

        Example: 
        curl -X POST -F "file=@documents/dynamo.pdf" http://127.0.0.1:8080/documaster/upload

    2. POST /documaster/query
    This allows us to query against a list of documents(all if none specified). 
    The query and optional list of documents are passed in the JSON payload should conform to 
    
    {
    "type": "object",
    "properties": {
        "query": {
            "type": "string"
        },
        "documents": {
            "type": "array",
            "items" : {
                "type": "string"
            }
        }
    },
    "required": [
        "query"
    ],
    "additionalProperties": true
    }

    Example 
    curl --header "Content-Type: application/json" \
         --request POST \
         --data '{"query":"Who created Dynamo?","documents":["dynamo.pdf"]}' \
        http://localhost:8080/documaster/query

## Usage 
* You need your OPENAI_API_KEY replacing the placeholder in `docker-compose.yml` , and ensure you are running `docker-compose --version` later than 3/

* Run ```docker-compose up --build``` from the root of this folder

* Navigate to ```http://localhost:8501``` to interact with the API by uploading documents and running queries against them. 
