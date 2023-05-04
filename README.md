# Tech stack:

1.FastAPI

2.Elasticsearch

3.Docker

# Steps to run

Pull code or download the code.

Install docker in your system.

Open folder in terminal and run the following command:

docker-compose up

# Endpoints

(IP can be obtained from the logs when the above command is run)

URL- http://{IP}:8000/elasticsearch/info

Description- Information about elasticsearch


URL- http://{IP}:8000/elasticsearch/health

Description- Information about health of elasticsearch


URL- http://{IP}:8000/get

Description- Gets a new paragraph with 50 sentence


URL- http://{IP}:8000/search?query={words}&operator={operator}

Description- Search for paragraphs with given words. Operator can be 'and' or 'or'.


URL- http://{IP}:8000/count

Description- Total number of paragraphs indexed


URL- http://{IP}:8000/dictionary

Description- Returns the definition of top 10 words with highest frequency
