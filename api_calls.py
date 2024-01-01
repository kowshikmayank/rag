import requests,json

#upload the dynamo research paper for processing & indexing 
with open("documents/dynamo.pdf", "rb") as f:
    r = requests.post("http://localhost:8080/documaster/upload", files={"file": f})
    print(r.text)
    assert r.status_code == 200

# Checking to see if a random file upload results in a 500 
with open("docker-compose.yml", "rb") as f:
    r = requests.post("http://localhost:8080/documaster/upload", files={"file": f})
    print(r.text)
    assert r.status_code == 500

r = requests.post("http://localhost:8080/documaster/query",json=json.loads('{"query":"Who created Dynamo?","documents":["dynamo.pdf"]}') , headers={"Content-Type": "application/json"})
assert r.status_code == 200
print(r.text)

r = requests.post("http://localhost:8080/documaster/query",json=json.loads('{"query":"What company created Dynamo?"}') , headers={"Content-Type": "application/json"})   
assert r.status_code == 200
print(r.text)

#upload the attention research paper for processing & indexing
with open("documents/attention.pdf", "rb") as f:
    r = requests.post("http://localhost:8080/documaster/upload", files={"file": f})
    print(r.text)
    assert r.status_code == 200


r = requests.post("http://localhost:8080/documaster/query",json=json.loads(('{"query":"What field does this concern?","documents":["dynamo.pdf","attention.pdf"]}')) , headers={"Content-Type": "application/json"})
#here, the query is worded with some ambiguity, so is blending in data from both documents we have indexed 
assert r.status_code == 200
print(r.text)


