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

* Run ```api_calls.py``` to check if everything works. Requires just ```pip3 install requests``` to setup the Python environment to do so. 

## Notes 
I am listing down a bunch of potential improvements that I would invest time in to make this application more robust. 

* Make document uploading asynchronous as parsing and indexing them is expensive
* Experiment with using a locally run language model to create the vector embeddings stored in the index. Currently, OpenAI calls are made to generate embeddings and that can get expensive fast. 
* Experiment with different modes of vector retrieval and preprocessing of context before passing to the ChatGPT model. 
* More extensive unit tests,integration tests et al
* I have left a bunch of things like ```/documents``` in here that I would definitely not put in a repository, just in the interest of reproducibility
* Evaluate exact/fuzzy matches to see how well our system is performing. ROUGE would be a good starting metric for fuzzy match type answers.
* Neater front end! 


