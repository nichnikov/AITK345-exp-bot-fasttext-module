import os
import time
from collections import namedtuple
import pandas as pd
import asyncio
from src.start import classifier
from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer(os.path.join("treined_models", "EBmodel188655ft"))

test_qrs_df = pd.read_csv(os.path.join("data", "queries_testing.csv"), sep="\t")
result_file_name = "searching_results_es_230414.csv"

test_qrs_dicts = test_qrs_df.to_dict(orient="records")
loop = asyncio.new_event_loop()

Result = namedtuple("Result", ["Query", "Etalon", "FastAnswerId", "JaccardScore", "TransformerScore"])
test_results = []

start_time = time.time()
for num, d in enumerate(test_qrs_dicts):
    t = time.time()
    query = d["Query"]
    search_results = loop.run_until_complete(classifier.searching(query, 9, 0.3))
    if search_results:
        temp_results = [(query, et_tx, fa_id, jcr_sc, 0) for et_tx, fa_id, jcr_sc in search_results if jcr_sc > 0.9]
        if temp_results:
            jaccard_the_best_results = sorted(temp_results, key=lambda x: x[3], reverse=True)
            test_results.append(jaccard_the_best_results[0])
        else:
            query_emb = model.encode(query)
            candidates_embs = [model.encode(x[0]) for x in search_results]
            et_txs, fa_ids, jcr_scs = zip(*search_results)
            scores = []
            for cand_emb in candidates_embs:
                scores.append(util.cos_sim(query_emb, cand_emb).item())
            results_with_scores = [(query, et, fa_id, j_sc, st_sc) for 
                                st_sc, et, fa_id, j_sc in zip(scores, et_txs, fa_ids, jcr_scs)]
            the_best_results = sorted(results_with_scores, key=lambda x: x[4], reverse=True)
            test_results.append(the_best_results[0])
    else:
        test_results.append((query, "Not Found", 0, 0, 0))
    print(num, time.time() - t)

print("test results 1:\n", test_results)
test_results = [Result(*x) for x in test_results]
print("test results 2:\n", test_results)


test_results_df = pd.DataFrame(test_results)
print(test_results_df)

test_results_df.to_csv(os.path.join("data", "results", "EBmodel188655ft.csv"), sep="\t", index=False)
print("working time:", time.time() - start_time)
