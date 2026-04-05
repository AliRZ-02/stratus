from typing import Callable, Type, List
from sentence_transformers import SentenceTransformer
import numpy as np
import os

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field

from stratus.tools.aiopslab.helper import AIOpsLabHelper


class GetRunbooksToolInput(BaseModel):
    summarized_issue: str = Field(
        title="Summarized_Issue",
        description="A condensed summary (max 50 words) of the issue you are facing, that you have understood from logs, metrics, or any other sources.",
    )


class GetRunbooksTool(BaseTool):
    name: str = "get_runbooks"
    description: str = (
        "This tool helps you fetch runbooks for common Kubernetes issues. "
        "Please provide 'summarized_issue' as an argument, and the tool will fetch the closest runbook."
    )
    args_schema: Type[BaseModel] = GetRunbooksToolInput
    generator: AIOpsLabHelper | None = None
    cache_function: Callable = lambda _args=None, _result=None: False
    model: None = None
    embeddings: None = None
    docs: List | None = None

    def __init__(self, generator: AIOpsLabHelper | None = None):
        super().__init__()
        self.generator = generator

        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        data = np.load("compressed_runbooks.npz", allow_pickle=True)
        self.embeddings = data["embeddings"]
        self.docs = data["documents"].tolist()

    def _run(self, summarized_issue: str) -> str:
        if self.generator is None:
            return f'No generator linked. Cannot fetch a runbook.'
        
        if self.model is None:
            return f'No embedding model found. Cannot fetch a runbook.'
        
        if self.embeddings is None:
            return f'No embeddings found. Cannot fetch a runbook.'
        
        if self.docs is None:
            return f'No runbooks found in collection. Cannot fetch a runbook.'
        
        query = "Represent this sentence for searching relevant passages: " + summarized_issue
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        scores = np.dot(self.embeddings, query_embedding)
        top_match = np.argsort(scores)[::-1][:1]

        for i in top_match:
            return "Here is the closest runbook I could find to your described issue:\n\n" + self.docs[i]
        
