from __future__ import annotations

from typing import Any

from langchain_core.documents import Document


def build_retriever(
    vector_store: Any,
    *,
    k: int,
    fetch_k: int,
    lambda_mult: float,
    search_type: str = "mmr",
):
    normalized_search_type = search_type.strip().lower()
    if normalized_search_type not in {"mmr", "similarity"}:
        raise ValueError("search_type must be either 'mmr' or 'similarity'.")

    search_kwargs: dict[str, Any] = {"k": k}
    if normalized_search_type == "mmr":
        search_kwargs.update(
            {
                "fetch_k": max(fetch_k, k),
                "lambda_mult": lambda_mult,
            }
        )

    return vector_store.as_retriever(
        search_type=normalized_search_type,
        search_kwargs=search_kwargs,
    )


def retrieve_for_qa(
    vector_store: Any,
    question: str,
    *,
    k: int = 4,
    fetch_k: int = 12,
    lambda_mult: float = 0.7,
    search_type: str = "mmr",
) -> list[Document]:
    retriever = build_retriever(
        vector_store,
        k=k,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult,
        search_type=search_type,
    )
    return retriever.invoke(question)


def retrieve_for_summary(
    vector_store: Any,
    query: str,
    *,
    k: int = 8,
    fetch_k: int = 20,
    lambda_mult: float = 0.5,
) -> list[Document]:
    retriever = build_retriever(
        vector_store,
        k=k,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult,
        search_type="mmr",
    )
    return retriever.invoke(query)
