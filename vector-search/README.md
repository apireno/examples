# SurrealDB Vector Search Example using Surreal Deal Dataset

This is a step by step tutorial to implement Vector Search using SurrealDB. 

Vector search allows for similarity-based queries on high-dimensional data, which is particularly useful for applications like semantic search, recommendation systems, and more.

## Prerequisites

- [SurrealDB installed](https://surrealdb.com/install) and running
- Ollama installed with the [nomic-embed-text model](https://ollama.com/library/nomic-embed-text)
- Import [Surreal Deal dataset](https://surrealdb.com/docs/surrealdb/surrealql/demo).

## Setup

Import the dataset that includes vector embeddings for products.
The dataset already includes the vector indexes and fields to store embeddings. 

The product embeddings will be stored in the `details_embedding` field.
```surql
DEFINE FIELD details_embedding
    ON TABLE product 
    TYPE array<decimal>;
```
The vector index `idx_product_details_embedding` uses the [MTREE algorithm](https://surrealdb.com/docs/surrealdb/surrealql/statements/define/indexes#m-tree-index-since-130) with 768 dimensions and [cosine distance](https://surrealdb.com/docs/surrealdb/surrealql/functions/database/vector#vectorsimilaritycosine) for similarity calculations.
```surql
DEFINE INDEX idx_product_details_embedding ON product 
    FIELDS details_embedding 
    MTREE DIMENSION 768 DIST COSINE;
```

## Usage

To perform a meaningful vector search, we first need to convert our text query into a vector embedding. We are converting our query into a numerical representation that we can compare with our product embeddings. I am using the Ollama API to generate these embeddings:

```surql
LET $query_text = "baggy clothes"; 
LET $query_embeddings = select * from http::post('http://localhost:11434/api/embeddings', {
  "model": "nomic-embed-text",
  "prompt": $query_text
}).embedding;
```

Once we have our query embeddings, we can perform a vector similarity search against our surreal deal store dataset.
Let's select the record id, name, and some more details of the products are fullfill our search for baggy clothes.

```surql
SELECT id, name, category, sub_category, price, vector::similarity::cosine(details_embedding, $query_embeddings) AS similarity FROM product ORDER BY similarity DESC LIMIT 3;
```
This query uses the `vector::similarity::cosine()` function to calculate the cosine similarity between our query embeddings and the product embeddings. We order the results by similarity in descending order to get the most relevant matches first, and limit the output to the top 3 results.

```surql
[
    {
        "id": "product:01GBDKYEAG93XBKM07CFH1S9S6",
        "name": "Men's Slammer Heavy Hoodie",
        "category": "Men",
        "sub_category": "Shirts & Tops",
        "price": 65,
        "similarity": 0.5410314334339928
    },
    {
        "id": "product:01GADYP46G8GN8YBPYTWGKYVB9",
        "name": "Men's Locker Heavy Zip-Through Hoodie",
        "category": "Men",
        "sub_category": "Shirts & Tops",
        "price": 70,
        "similarity": 0.5395832679844547
    },
    {
        "id": "product:01H36XDJRG95NB89AQKSV1NRGA",
        "name": "Women's Locker Heavy Zip-Through Hoodie",
        "category": "Women",
        "sub_category": "Shirts & Tops",
        "price": 65,
        "similarity": 0.5395832679844547
    }
]
```
The similarity scores range from -1 to 1, with 1 indicating perfect similarity. The similarity scores for the above products is around 0.54.


This vector search approach allows us to find semantically related items, even when there isn't an exact match for the search terms in the product descriptions or names.