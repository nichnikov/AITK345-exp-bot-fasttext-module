"""
классификатор KNeighborsClassifier в /home/an/Data/Yandex.Disk/dev/03-jira-tasks/aitk115-support-questions
"""
from src.data_types import Parameters
from src.storage import ElasticClient
from src.texts_processing import TextsTokenizer
from src.utils import timeout
from src.config import logger
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# https://stackoverflow.com/questions/492519/timeout-on-a-function-call

tmt = float(10)  # timeout


class FastAnswerClassifier:
    """Объект для оперирования MatricesList и TextsStorage"""

    def __init__(self, tokenizer: TextsTokenizer, parameters: Parameters, ft_model):
        self.es = ElasticClient()
        self.tkz = tokenizer
        self.prm = parameters
        self.ft_model = ft_model

    @timeout(float(tmt))
    def searching(self, text: str, pubid: int, score: float):
        """"""
        """searching etalon by  incoming text"""
        try:
            tokens = self.tkz([text])
            if tokens[0]:
                tokens_str = " ".join(tokens[0])
                etalons_search_result = self.es.texts_search(self.prm.clusters_index, "LemCluster", [tokens_str])
                result_dicts = etalons_search_result[0]["search_results"]
                if result_dicts:
                    results_tuples = [(d["ID"], d["Cluster"], d["LemCluster"]) for d in result_dicts]
                    ids, ets, lm_ets = zip(*results_tuples)
                    q_vc = self.ft_model.get_sentence_vector(tokens_str)
                    et_vcs = [self.ft_model.get_sentence_vector(lm_et) for lm_et in list(lm_ets)]
                    et_vcs = [v.reshape(1, 100) for v in et_vcs]
                    et_vcs = np.concatenate(et_vcs, axis=0)
                    scores = cosine_similarity(q_vc.reshape(1, 100), et_vcs)[0]
                    the_best_result = sorted(list(zip(ids, ets, lm_ets, scores)), key=lambda x: x[3], reverse=True)[0]
                    if the_best_result[3] >= score:
                        answers_search_result = self.es.answer_search(self.prm.answers_index, the_best_result[0], pubid)
                        if answers_search_result["search_results"]:
                                search_result = {"templateId": answers_search_result["search_results"][0]["templateId"],
                                                 "templateText": answers_search_result["search_results"][0][
                                                     "templateText"]}
                                logger.info("search completed successfully with result: {}".format(str(search_result)))
                                return search_result
                        else:
                            logger.info("not found answer with templateId {} and pub_id {}".format(str(d["ID"]),
                                                                                                       str(pubid)))
                    else:
                        logger.info("elasticsearch doesn't find any etalons for input text {}".format(str(text)))
                        return {"templateId": 0, "templateText": ""}
                else:
                    logger.info("elasticsearch doesn't find any etalons for input text {}".format(str(text)))
                    return {"templateId": 0, "templateText": ""}
            else:
                logger.info("tokenizer returned empty value for input text {}".format(str(text)))
                return {"templateId": 0, "templateText": ""}
                # return tuple(0, "no", "no", 0)
        except Exception:
            logger.exception("Searching problem with text: {}".format(str(text)))
            # return tuple(0, "no", "no", 0)
            return {"templateId": 0, "templateText": ""}

