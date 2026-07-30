from __future__ import annotations

import unittest

from src.utils import export_chat_markdown


class ExportChatMarkdownTests(unittest.TestCase):
    def test_exports_all_messages_and_source_labels(self) -> None:
        result = export_chat_markdown(
            [
                {"role": "user", "content": "What is RAG?"},
                {
                    "role": "assistant",
                    "content": "A grounded answer.",
                    "sources": [
                        {
                            "metadata": {
                                "source_filename": "lecture.pdf",
                                "page_number": 2,
                                "chunk_index": 4,
                            }
                        }
                    ],
                },
            ],
            document_name="lecture.pdf",
        )

        self.assertIn("## You\n\nWhat is RAG?", result)
        self.assertIn("## Assistant\n\nA grounded answer.", result)
        self.assertIn("lecture.pdf · Page 2 · Chunk 4", result)

    def test_empty_conversation_has_a_useful_message(self) -> None:
        result = export_chat_markdown([], document_name=None)

        self.assertIn("No conversation yet", result)


if __name__ == "__main__":
    unittest.main()
