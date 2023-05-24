from src.texts_processing import TextsTokenizer
import src
print(src.NAME)
from src.config import (stopwords,
                        parameters,
                        logger)
from src.classifiers import FastAnswerClassifier
import fasttext


ft_model = fasttext.load_model("/mnt/data/github/AITK-305-fasttext-testing/models/cc.ru.300.bin")
tokenizer = TextsTokenizer()
tokenizer.add_stopwords(stopwords)
classifier = FastAnswerClassifier(tokenizer, parameters, ft_model)
logger.info("service started...")
