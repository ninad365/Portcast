import string
import json
import requests
from typing import Union
from fastapi import FastAPI
from elasticsearch import Elasticsearch
from collections import Counter

es = Elasticsearch("http://localhost:9200", http_auth=("ninad1", "ninad123"))

# Check if the indices exist / create a new one if it doesnt
if es.indices.exists(index="movies"):
    print("index movies exist")
else:
    print("index movies does not exist - creating new")
    es.indices.create(index="movies")

    mapping = {
        "properties": {
            "paragraph": {
            "type": "text",
            "fielddata": True
            }
        }
    }
    es.indices.put_mapping(index="movies", body=mapping)


app = FastAPI()

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
    es.index(index="movies", document=json1)
    return json1

def _fetch_paragraph():
    url = "http://metaphorpsum.com/paragraphs/1/50"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/search")
def search(query: str, operator):
    response = es.search(
        index="movies",
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
    result = es.search(index="movies", body={"query":{"match_all":{}}})
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
        print(i)
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + i[0]
        print(url)

        try:
            response = requests.get(url)
            response.raise_for_status()
            definitions[i[0]] = response_to_definition(response.text) # to get frequency -> i[1]
        except:
            definitions[i[0]] = "Could not fetch definition"

    print(definitions)
    return {"response":top_10, "def":definitions}

def response_to_definition(response):
    data = json.loads(response)
    meanings = data[0]["meanings"][0]["definitions"][0]["definition"]
    return meanings

# @app.get("/dictionary")
# def dictionary():
#     # word = "the"
#     # url = "https://api.dictionaryapi.dev/api/v2/entries/en/hello"
#     # response = requests.get(url)
#     # return {"definition":response.text}
#     response = es.search(
#         index="movies",
#         body= {
#             "size": 0,
#             "aggs": {
#                 "top_terms": {
#                     "terms": {
#                         "field": "paragraph",
#                     }
#                 }
#             }
#         }
#     )

#     # result = response["aggregations"]["most_frequent_words"]["buckets"]
#     return {"response":response}