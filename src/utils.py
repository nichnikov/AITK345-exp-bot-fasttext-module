import functools
import multiprocessing.pool
from functools import wraps
from src.config import logger
import pandas as pd
from src.texts_processing import TextsTokenizer
import time


def texts_tokenize(texts: [], stopwords_roots: []):
    tokenizer = TextsTokenizer()
    stopwords = []

    for root in stopwords_roots:
        stopwords_df = pd.read_csv(root, sep="\t")
        stopwords += list(stopwords_df["stopwords"])
    tokenizer.add_stopwords(stopwords)

    results = []
    for ls in chunks(texts, 15000):
        results += [" ".join(l) for l in tokenizer(ls)]

    return results


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logger.info(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def text2text_entry(text1: str, text2: str) -> float:
    """
    :param text1: текст, вхождение которого оценивается
    :param text2: текст, вхождение в который оценивается
    """
    tx1_len = len(set(text1.split()))
    if tx1_len != 0:
        intersection = set(text1.split()) & set(text2.split())
        return float(len(intersection) / tx1_len)
    else:
        return 0.0


def jaccard_similarity(text1: str, text2: str) -> float:
    """"""
    intersection = set(text1.split()) & set(text2.split())
    union = set(text1.split()).union(set(text2.split()))
    if len(union) != 0:
        return float(len(intersection) / len(union))
    else:
        return 0.0


def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""

    def timeout_decorator(item):
        """Wrap the original function."""

        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)

        return func_wrapper

    return timeout_decorator
