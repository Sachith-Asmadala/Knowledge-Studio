from __future__ import annotations

import unittest

from src.retriever import build_retriever


class FakeVectorStore:
    def __init__(self) -> None:
        self.call: dict | None = None

    def as_retriever(self, **kwargs):
        self.call = kwargs
        return kwargs


class BuildRetrieverTests(unittest.TestCase):
    def test_mmr_includes_diversity_options(self) -> None:
        store = FakeVectorStore()

        build_retriever(
            store,
            k=5,
            fetch_k=3,
            lambda_mult=0.6,
            search_type="MMR",
        )

        self.assertEqual(store.call["search_type"], "mmr")
        self.assertEqual(
            store.call["search_kwargs"],
            {"k": 5, "fetch_k": 5, "lambda_mult": 0.6},
        )

    def test_similarity_only_passes_supported_options(self) -> None:
        store = FakeVectorStore()

        build_retriever(
            store,
            k=4,
            fetch_k=12,
            lambda_mult=0.7,
            search_type="Similarity",
        )

        self.assertEqual(
            store.call,
            {"search_type": "similarity", "search_kwargs": {"k": 4}},
        )

    def test_invalid_search_type_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_retriever(
                FakeVectorStore(),
                k=4,
                fetch_k=12,
                lambda_mult=0.7,
                search_type="hybrid",
            )


if __name__ == "__main__":
    unittest.main()
