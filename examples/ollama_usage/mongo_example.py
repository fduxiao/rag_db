#/usr/bin/env python3
import ollama
import pymongo
from pymongo.operations import SearchIndexModel
from bson.binary import Binary
from bson.binary import BinaryVectorDtype


documents = [
    "Llamas are members of the camelid family meaning they're pretty closely related to vicuñas and camels",
    "Llamas were first domesticated and used as pack animals 4,000 to 5,000 years ago in the Peruvian highlands",
    "Llamas can grow as much as 6 feet tall though the average llama between 5 feet 6 inches and 5 feet 9 inches tall",
    "Llamas weigh between 280 and 450 pounds and can carry 25 to 30 percent of their body weight",
    "Llamas are vegetarians and have very efficient digestive systems",
    "Llamas live to be about 20 years old, though some only live for 15 years and others live to be 30 years old",
]


EmbeddingModel = "mxbai-embed-large"
EmbeddingSize = 1024
GeneratingModel = "deepseek-r1:1.5b"


def get_embedding(text):
    response = ollama.embed(model=EmbeddingModel, input=text)
    return response["embeddings"][0]


def generate_bson_vector(vector, vector_dtype):
   return Binary.from_vector(vector, vector_dtype)


client = pymongo.MongoClient("mongodb://localhost:27017?directConnection=true")
db = client.get_database("test")
collection = db.get_collection("abc")
# delete all
collection.delete_many({})


# store each document in a vector embedding database
for i, d in enumerate(documents):
    e = get_embedding(d)
    doc = {
        "_id": i,
        "text": d,
        "embedding": generate_bson_vector(e, BinaryVectorDtype.FLOAT32),
    }
    collection.insert_one(doc)
    print(f"document {i} inserted")


# create indices
search_index_model = SearchIndexModel(
    definition = {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "similarity": "dotProduct",
                "numDimensions": EmbeddingSize
            },
        ]
      },
    name="vector_index",
    type="vectorSearch"
)
collection.create_search_index(model=search_index_model)


# an example input
input_prompt = "What animals are llamas related to?"
query_embedding = get_embedding(input_prompt)


# Sample vector search pipeline
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "queryVector": query_embedding,
            "path": "embedding",
            "exact": True,
            "limit": 1
       }
    },
    {
        "$project": {
            "_id": 1,
            "text": 1,
            "score": {
                "$meta": "vectorSearchScore"
            }
        }
   }
]
# Execute the search
results = collection.aggregate(pipeline)
data = list(results)[0]["text"]

print("Retrieved. Now, generating...")
# generate a response combining the prompt and data we retrieved in step 2
output = ollama.generate(
    model=GeneratingModel,
    prompt=f"Using this data: {data}. Respond to this prompt: {input_prompt}"
)
print(output['response'])
