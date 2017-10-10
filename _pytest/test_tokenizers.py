# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


def test_whitespace():
    from mynlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
    tk = WhitespaceTokenizer()

    assert [t.text for t in tk.tokenize("Forecast for lunch")] == ['Forecast', 'for', 'lunch']
    assert [t.offset for t in tk.tokenize("Forecast for lunch")] == [0, 9, 13]

    assert [t.text for t in tk.tokenize("hey ńöñàśçií how're you?")] == ['hey', 'ńöñàśçií', 'how\'re', 'you?']
    assert [t.offset for t in tk.tokenize("hey ńöñàśçií how're you?")] == [0, 4, 13, 20]


def test_spacy(spacy_nlp):
    from mynlu.tokenizers.spacy_tokenizer import SpacyTokenizer
    tk = SpacyTokenizer()
    
    assert [t.text for t in tk.tokenize(spacy_nlp("Forecast for lunch"))] == ['Forecast', 'for', 'lunch']
    assert [t.offset for t in tk.tokenize(spacy_nlp("Forecast for lunch"))] == [0, 9, 13]

    assert [t.text for t in tk.tokenize(spacy_nlp("hey ńöñàśçií how're you?"))] == \
           ['hey', 'ńöñàśçií', 'how', '\'re', 'you', '?']
    assert [t.offset for t in tk.tokenize(spacy_nlp("hey ńöñàśçií how're you?"))] == [0, 4, 13, 16, 20, 23]


def test_mitie():
    from mynlu.tokenizers.mitie_tokenizer import MitieTokenizer
    tk = MitieTokenizer()

    assert [t.text for t in tk.tokenize("Forecast for lunch")] == ['Forecast', 'for', 'lunch']
    assert [t.offset for t in tk.tokenize("Forecast for lunch")] == [0, 9, 13]

    assert [t.text for t in tk.tokenize("hey ńöñàśçií how're you?")] == ['hey', 'ńöñàśçií', 'how', '\'re', 'you', '?']
    assert [t.offset for t in tk.tokenize("hey ńöñàśçií how're you?")] == [0, 4, 13, 16, 20, 23]

    
def test_jieba():
    from mynlu.tokenizers.jieba_tokenizer import JiebaTokenizer
    tk = JiebaTokenizer()
    
    assert [t.text for t in tk.tokenize("我想去吃兰州拉面")] == ['我', '想', '去', '吃', '兰州', '拉面']
    assert [t.offset for t in tk.tokenize("我想去吃兰州拉面")] == [0, 1, 2, 3, 4, 6]

        
    assert [t.text for t in tk.tokenize("Micheal你好吗？")] == ['Micheal', '你好', '吗', '？']
    assert [t.offset for t in tk.tokenize("Micheal你好吗？")] == [0, 7, 9, 10]