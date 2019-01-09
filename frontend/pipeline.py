# Speech-to-text
import speech_recognition as sr

# NLP
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
import re

import nltk.tokenize as nt
import nltk

import pyttsx3

verb_list = ['VB', 'VBP', '$']
quantity_list = ['CARDINAL']
company_list = ['GPE', 'ORG']
vocab_buy = ['buy', 'purchase', 'acquire', 'get', 'obtain', 'procure', 'take', 'secure', 'procure', 'invest']
vocab_sell = ['sell', 'auction', 'market', 'trade', 'dump', 'exchange', 'unload']

def speech_to_text():
    """
    Function that collect command in audio format.
    """
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something")
        audio = r.listen(source,timeout=1,phrase_time_limit=10)
        print("Time over !")

    try:
        order_en = r.recognize_google(audio)
        print("Text: "+ order_en)
    except:
        order_en = "Nothing"
        pass

    return order_en


def cleaning(order):
    """
    Function that processes the order turned in text.
    """
    # Remove characters
    no_char = " ".join([word for word in order.split() if (len(word) > 1)])

    # Segment sentences
    # clean = " ".join(["." if str(word) in 'please' else word for word in no_char.split()])

    return no_char


def alfred_response(alfred):

    engine = pyttsx3.init()
    engine.say(alfred)
    engine.setProperty('rate',120)
    engine.setProperty('volume', 0.9)
    engine.runAndWait()


def order_sending(pos_sentences, entities):
    """
    Identify the nature of the order.
    """
    # print(pos_sentences[0][1])
    # if("purchase" in pos_sentences[0][1]):
    #     actions = "purchase"
    # Classify the order in buying of selling category or neither
    actions = [action for action in pos_sentences[0] if( action[1] in verb_list) ]
    print(len(actions))
    if( not len(actions)):
        print("I may have misunderstood you Sir.")
        # alfred_response("I may have misunderstood you Sir.")
        return None, None, None

    action_none = [action for action in actions if( action[1] in verb_list and (action[0] not in vocab_sell and action[0] not in vocab_buy)) ]
    if(len(action_none)):
        print("I may have misunderstood you Sir.")
        # alfred_response("I may have misunderstood you Sir.")
        return None, None, None

    todo = [action for action in actions if( action[1] in verb_list and action[0] in vocab_buy) ]
    if(not len(todo)):
        todo = [action for action in actions if( action[1] in verb_list and action[0] in vocab_sell) ]

    action = todo[0]
    number = [number[0] for number in entities if number[1] in quantity_list]
    comp = [company[0] for company in entities if company[1] in company_list]
    if(not len(action) or not len(number) or not len(comp)):
        print("I may have misunderstood you Sir.")
        # alfred_response("I may have misunderstood you Sir.")
        return None, None, None
    else:
        print("Do: " + action[0])
        print("Number: " + number[0])
        print("From: " + comp[0])
        # alfred_response("I will " + action + " a " + number + comp + "stocks")
        return comp[0], number[0], action[0]


def entity_detection(sentence):
    """
    Detects entities (verbs and names) in individual orders.
    """
    nlp = en_core_web_sm.load()
    # Get entities
    order = nlp(sentence)
    entities = [(X.text, X.label_) for X in order.ents]
    print(entities)

    # Get verbs
    ss = nt.sent_tokenize(sentence)
    tokenized_sent = [nt.word_tokenize(sent) for sent in ss]
    pos_sentences = [nltk.pos_tag(sent) for sent in tokenized_sent]
    print(pos_sentences)
    print()
    return order_sending(pos_sentences, entities)


def sentence_segmenting(orders):
    """
    In case the command contained multiple orders, this functions splits them.
    """
    # Get individual order
    while (len(orders)):
        matchObj = re.match(r'(.*) \.', orders, re.M|re.I)

        if matchObj:
            sentence = matchObj.group()
            orders = orders[len(sentence):]
        else:
            sentence = orders
            orders = ""

        print(sentence)
        return entity_detection(sentence)

# if __name__ == '__main__':
#     # order_en, order_fr = speech_to_text()
#     order_en = "Alfred, sell hundred stock from Facebook please buy a thousand stocks from Twitter"
#     # order_en = "hello "
#     processed = cleaning(order_en)
#     sentence_segmenting(processed)
