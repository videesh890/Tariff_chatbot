import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
_df = None
_vectors = None
# Create a single embeddings instance to reuse
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
def load_embeddings():
    global _df, _vectors
    if _df is not None and _vectors is not None:
        return _df, _vectors
    _df = pd.read_csv("data/tariffs.csv")  # Make sure this file exists
    descriptions = _df['Product_Description'].astype(str).tolist()
    _vectors = np.array(embeddings.embed_documents(descriptions))
    return _df, _vectors
def semantic_search(query, top_n=3):
    df, vectors = load_embeddings()
    query_vec = np.array(embeddings.embed_query(query))
    sims = cosine_similarity([query_vec], vectors)[0]
    indices = sims.argsort()[::-1][:top_n]
    return df.iloc[indices].to_dict(orient="records")
