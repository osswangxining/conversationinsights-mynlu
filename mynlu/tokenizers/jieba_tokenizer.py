from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from typing import Any
from typing import Dict
from typing import List
from typing import Text

from mynlu.config.mynluconfig import MyNLUConfig
from mynlu.tokenizers import Tokenizer, Token
from mynlu.pipeline.plugin import Plugin
from mynlu.trainers import Message
from mynlu.trainers import TrainingData

import logging
logger = logging.getLogger(__name__)

class JiebaTokenizer(Tokenizer, Plugin):
    
    name = "tokenizer_jieba"

    provides = ["tokens"]
    
    def __init__(self):
        pass
    
    @classmethod
    def required_packages(cls):
        # type: () -> List[Text]
        return ["jieba"]

    def train(self, training_data, config, **kwargs):
        # type: (TrainingData, MyNLUConfig, **Any) -> None
        if config['language'] != 'zh':
            raise Exception("tokenizer_jieba is only used for Chinese. Check your configure json file.")
        for example in training_data.training_examples:
            example.set("tokens", self.tokenize(example.text))

    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None

        message.set("tokens", self.tokenize(message.text))

    def tokenize(self, text):
        # type: (Text) -> List[Token]
        import jieba

        words = jieba.lcut(text.encode('utf-8'))
        #logger.debug("words:{}".format(words))

        running_offset = 0
        tokens = []
        for word in words:
            word_offset = text.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))
        return tokens
