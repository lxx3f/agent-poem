import requests

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "nomic-embed-text"
MAX_LEN = 1000
DIMENTION_LEN = 768


class Embedding_service:

    def get_embedding(self, text: str) -> list[float]:
        text = text.strip()
        if not text:
            raise ValueError(f"embedding error: text is empty")

        if len(text) > MAX_LEN:
            text = text[:MAX_LEN]

        resp = requests.post(OLLAMA_EMBED_URL,
                             json={
                                 "model": MODEL_NAME,
                                 "prompt": text
                             },
                             timeout=30)

        if resp.status_code != 200:
            raise ValueError(
                f"embedding error: embedding service not work, status_code : {resp.status_code}"
            )

        return resp.json().get("embedding")
