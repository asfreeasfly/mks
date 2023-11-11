from numpy import dot
from numpy.linalg import norm
from coordinators.documents.create import create_tagged_documents
from coordinators.models.read import retrieve_models
from database import connect
from helpers.vectorize import preprocess_text


async def count_documents():
    try:
        conn = await connect()
        results = await conn.fetchval(
            f"select count(*) from documents")

        return results
    except Exception as e:
        raise ValueError("Can't get documents")


async def get_all():
    try:
        conn = await connect()
        results = await conn.fetch(
            f"select * from documents docs")

        return results
    except Exception as e:
        raise ValueError('Documents not found!')


async def get(id: int):
    try:
        conn = await connect()
        result = await conn.fetchrow(
            f"select * from documents doc where doc.id = {id}")

        return result
    except Exception as e:
        raise ValueError('Document not found!')

def cosine_similarity(vec_a, vec_b):
    return dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b))

async def filter_by_similarity_score(
        nlp,
        query: str,
        top_k=5
):
    try:
        documents = await get_all()
        tagged_documents = create_tagged_documents(nlp, documents)

        query_tokens = preprocess_text(nlp(query))
        models = await retrieve_models()

        most_similar_docs = []
        for model in models:
            query_vector = model.infer_vector(query_tokens)

            sims = model.dv.most_similar([query_vector], topn=len(model.dv))
            most_similar_docs.extend(
                [
                    (
                        tagged_documents[int(sim[0])].tags[0],
                        tagged_documents[int(sim[0])].words, sim[1]
                    ) for sim in sims[:top_k]
                ]
            )

        return most_similar_docs
    except Exception as e:
        raise ValueError(str(e))
