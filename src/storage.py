"""https://elasticsearch-py.readthedocs.io/en/latest/async.html"""
from __future__ import annotations

import os
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from src.config import (logger,
                        PROJECT_ROOT_DIR,
                        parameters)
from src.utils import jaccard_similarity
from src.data_types import TextsDeleteSample
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base settings object to inherit from."""

    class Config:
        env_file = os.path.join(PROJECT_ROOT_DIR, ".env")
        env_file_encoding = "utf-8"


class ElasticClient(AsyncElasticsearch):
    """Handling with AsyncElasticsearch"""
    def __init__(self, *args, **kwargs):
        # self.settings = ElasticSettings()
        super().__init__(
            hosts="http://srv01.nlp.dev.msk2.sl.amedia.tech:9200",
            basic_auth=("elastic", "changeme"),
            request_timeout=100,
            max_retries=50,
            retry_on_timeout=True,
            *args,
            **kwargs,
        )

    async def texts_search(self, index: str, searching_field: str, texts: list[str]) -> list:
        async def search(tx: str, field: str):
            resp = await self.search(
                allow_partial_search_results=True,
                min_score=0,
                index=index,
                query={"match": {field: tx}},
                size=100,
            )
            return resp

        texts_search_result = []
        for txt in texts:
            res = await search(txt, searching_field)
            if res["hits"]["hits"]:
                texts_search_result.append(
                    {
                        "text": txt,
                        "search_results": [
                            {
                                **d["_source"],
                                **{"id": d["_id"]},
                                **{"score": d["_score"]},
                            }
                            for d in res["hits"]["hits"]
                        ],
                    }
                )
        return texts_search_result

    async def answer_search(self, index: str, fa_id: int, pub_id: int):
        """Отдельный метод для точного поиска по двум полям"""

        async def fa_search(templateId: int, pubId: int):
            resp = await self.search(
                allow_partial_search_results=True,
                min_score=0,
                index=index,
                query={
                    "bool": {
                        "must": [
                            {"match_phrase": {"templateId": templateId}},
                            {"match_phrase": {"pubId": pubId}},
                        ]
                    }
                },
                size=100
            )
            return resp

        res = await fa_search(fa_id, pub_id)
        if [res["hits"]["hits"]]:
            return {
                "search_results": [
                    {**d["_source"], **{"id": d["_id"]}, **{"score": d["_score"]}}
                    for d in res["hits"]["hits"]
                ]
            }
