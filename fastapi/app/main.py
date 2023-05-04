import string
import json
import requests
from typing import Union
from elasticsearch import Elasticsearch
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from collections import Counter

app = FastAPI()
es = Elasticsearch(["http://elasticsearch:9200/"])

# Check if the indices exist / create a new one if it doesnt
if es.indices.exists(index="paragraphs"):
    print("index paragraphs exist")
else:
    print("index paragraphs does not exist - creating new")
    es.indices.create(index="paragraphs")

    mapping = {
        "properties": {
            "paragraph": {
            "type": "text",
            "fielddata": True
            }
        }
    }
    es.indices.put_mapping(index="paragraphs", body=mapping)

@app.get("/")
def hello_world():
    return {"Hello": "World"}

@app.get("/elasticsearch/info")
def elasticsearch_details():
    return JSONResponse(dict(es.info()))

@app.get("/elasticsearch/health")
def elasticsearch_health():
    return JSONResponse(dict(es.cluster.health()))

@app.get("/get")
def read_root():
    paragraph = _fetch_paragraph()

    # Save words to json
    data = {}
    try:
        with open('./data.json') as f:
            data = json.load(f)
    except:
        with open('data.json', 'w') as f:
            json.dump(data, f)

    table = str.maketrans("", "", string.punctuation)
    for i in paragraph.translate(table).split():
        i = i.lower()
        if i in data:
            data[i] += 1
        else:
            data[i] = 1
    with open('data.json', 'w') as f:
        json.dump(data, f)

    json1 = {"paragraph": paragraph}
    es.index(index="paragraphs", document=json1)
    return json1

# Retrives paragraph with 50 sentence
def _fetch_paragraph():
    url = "http://metaphorpsum.com/paragraphs/1/50"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# URL- http://{IP}:8000/search?query={words}&operator={operator}
@app.get("/search")
def search(query: str, operator):
    response = es.search(
        index="paragraphs",
        body={
            "query": {
                "simple_query_string" : {
                    "query": query,
                    "fields": ["paragraph"],
                    "default_operator": operator
                }
            }
        }
    )
    count = response["hits"]["total"]["value"]
    results = response["hits"]["hits"]
    return {
        "count":count,
        "results":results,
        }

@app.get("/count")
def count():
    result = es.search(index="paragraphs", body={"query":{"match_all":{}}})
    count = result["hits"]["total"]["value"]
    return {"count":count}

@app.get("/dictionary")
def dictionary():
    data = {}
    try:
        with open('./data.json') as f:
            data = json.load(f)
    except:
        with open('data.json', 'w') as f:
            json.dump(data, f)
    
    # Get top 10 items by frequency
    top_10 = Counter(data).most_common(10)

    definitions = {}
    for i in top_10:
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + i[0]

        try:
            response = requests.get(url)
            response.raise_for_status()
            definitions[i[0]] = response_to_definition(response.text) # to get frequency -> i[1]
        except:
            definitions[i[0]] = "Could not fetch definition"

    return {"response":top_10, "def":definitions}

def response_to_definition(response):
    data = json.loads(response)
    meanings = data[0]["meanings"][0]["definitions"][0]["definition"]
    return meanings
