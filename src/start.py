import os
import fasttext
from texts_processing import TextsTokenizer
from config import (stopwords,
                    parameters,
                    logger,
                    PROJECT_ROOT_DIR)
from classifiers import FastAnswerClassifier


ft_model = fasttext.load_model(os.path.join(PROJECT_ROOT_DIR, "models", "bss_cbow_lem.bin"))
tokenizer = TextsTokenizer()
tokenizer.add_stopwords(stopwords)
classifier = FastAnswerClassifier(tokenizer, parameters, ft_model)
logger.info("service started...")
