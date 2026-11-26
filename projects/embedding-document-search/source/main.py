"""Practice the cosine-ranking pattern from the BillSum tutorial, PDF page 2531."""
import argparse
import math
import os

DOCUMENTS = (
    "A bill to improve access to public rail transportation.",
    "A bill to fund clean energy projects.",
    "A bill to modernize health record systems.",
)
QUERY = "Which bill invests in renewable energy?"


def cosine_similarity(left, right):
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    return dot / (math.hypot(*left) * math.hypot(*right))


def embed_live():
    from openai import OpenAI

    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    with OpenAI(
        base_url=f"{endpoint}/openai/v1/",
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    ) as client:
        result = client.embeddings.create(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            input=[*DOCUMENTS, QUERY],
        )
    return [item.embedding for item in sorted(result.data, key=lambda item: item.index)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    vectors = embed_live() if args.live else [(1, 0), (0, 1), (1, 1), (0, 1)]
    ranked = sorted(
        (
            (cosine_similarity(vector, vectors[-1]), document)
            for document, vector in zip(DOCUMENTS, vectors[:-1], strict=True)
        ),
        reverse=True,
    )
    print("Live embeddings" if args.live else "Offline ranking with illustrative vectors")
    for score, document in ranked:
        print(f"{score:.3f}  {document}")


if __name__ == "__main__":
    main()
