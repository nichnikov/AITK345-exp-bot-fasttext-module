from typing import List
from pydantic import BaseModel, Field


class Parameters(BaseModel):
    clusters_index: str
    answers_index: str
    stopwords_files: List[str]
    max_hits: int
    chunk_size: int


class TemplateIds(BaseModel):
    templateIds: List[int]
    # pubId: int


class SearchData(BaseModel):
    """"""
    pubid: int = Field(title="Пабайди, в котором будет поиск дублей")
    text: str = Field(title="вопрос для поиска")


class TextsDeleteSample(BaseModel):
    """Схема данных для удаления данных по тексту из Индекса"""
    Index: str
    Texts: List[str]
    FieldName: str
    Score: float


class DeleteSample(BaseModel):
    """Схема данных для удаления данных по тексту из Индекса"""
    Index: str
    Texts: List[str]
    FieldName: str
    Score: float


