import re
from pymystem3 import Mystem
from itertools import chain
from itertools import groupby
import operator


def group_gen(asc_dsc: list):
    """генератор"""
    it = groupby(sorted(asc_dsc, key=lambda x: x[1]), operator.itemgetter(1))
    for k, v in it:
        yield k, [x[0] for x in v]


class TextsTokenizer:
    """Tokenizer"""

    def __init__(self):
        self.stopwords = []
        self.synonyms = []
        self.stop_words_patterns = re.compile("")
        self.m = Mystem()

    def texts2tokens(self, texts: list[str]) -> list[str]:
        """Lemmatization for texts in list. It returns list with lemmatized texts"""
        try:
            text_ = "\n".join(texts)
            text_ = re.sub(r"[^\w\n\s]", " ", text_)
            lm_texts = "".join(self.m.lemmatize(text_.lower()))
            return [lm_tx.split() for lm_tx in lm_texts.split("\n")][:-1]
        except TypeError as e:
            return []

    def add_stopwords(self, stopwords: list[str]):
        """adding stop words into class"""
        self.stopwords = [" ".join(x) for x in self.texts2tokens(stopwords)]
        self.stop_words_patterns = re.compile("|".join([r"\b" + tx + r"\b" for tx in self.stopwords]))

    def add_synonyms(self, synonyms: list[(str)]):
        """adding stop words into class"""
        ascs, dscs = zip(*synonyms)
        lm_ascs = [" ".join(x) for x in self.tokenization(list(ascs))]
        syns_dct = {k: v for k, v in group_gen([(a, d) for a, d in zip(lm_ascs, dscs)])}
        for asc in syns_dct:
            self.synonyms.append((asc, re.compile("|".join([r"\b" + w + r"\b" for w in syns_dct[asc]]))))

    def del_stopwords(self, stopwords: list[str]):
        """adding stop words into class"""
        stopwords_del = [x for x in chain(*self.texts2tokens(stopwords))]
        self.stopwords = [w for w in self.stopwords if w not in stopwords_del]
        self.stop_words_patterns = re.compile("|".join([r"\b" + tx + r"\b" for tx in self.stopwords]))

    def tokenization(self, texts: list[str]) -> list[list]:
        """list of texts lemmatization with stop words deleting"""
        lemm_texts = self.texts2tokens(texts)
        if self.synonyms:
            lem_texts_union = "\n".join([" ".join(lm_tx) for lm_tx in lemm_texts])
            for syn_pair in self.synonyms:
                lem_texts_union = syn_pair[1].sub(syn_pair[0], lem_texts_union)
            if self.stopwords:
                return [self.stop_words_patterns.sub(" ", l_tx).split() for l_tx in lem_texts_union.split("\n")]
            else:
                return [l_tx.split() for l_tx in lem_texts_union.split("\n")]
        if self.stopwords:
            return [self.stop_words_patterns.sub(" ", " ".join(l_tx)).split() for l_tx in lemm_texts]
        else:
            return lemm_texts

    def __call__(self, texts: list[str]):
        return self.tokenization(texts)


if __name__ == "__main__":
    import os
    import pandas as pd

    df = pd.read_csv(os.path.join("data", "synonyms.csv"), sep="\t")
    L = [(a, d) for a, d in zip(df["asc"], df["dsc"])]
    print(L)

    tknz = TextsTokenizer()
    tknz.add_stopwords(["жопа", "член"])
    print("stopwords:", tknz.stop_words_patterns)
    tknz.add_synonyms(L)
    print(tknz.synonyms)
    tx = "налог со спецоценкой индивидуальный предприниматель справляется плохо на упрощенной системе жопа член"
    print(tknz([tx]))
