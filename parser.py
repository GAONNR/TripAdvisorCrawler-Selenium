import konlpy
import nltk
import glob
import sys
import json
import csv

grammar = '''
NP: {<N.*>*<X.*>?}      # Noun phrase
VP: {<V.*>*}            # Verb phrase
AP: {<A.*>*}            # Adjective phrase
CLAUSE: {<NP|VP|AP|J.*|P.*|M.*|I.*|F.*>*<E.*|S.*>*}
'''

hannanum = konlpy.tag.Hannanum()
parser = nltk.RegexpParser(grammar)
classification = dict()
senti_dict = dict()

test = False


class Score:
    def __init__(self):
        self.score_dict = {
            '서비스': 0.0,
            '가격': 0.0,
            '청결도': 0.0,
            '객실': 0.0,
            '침대의 퀄리티': 0.0,
            '장소': 0.0
        }

    def increase(self, category, amount):
        self.score_dict[category] += amount

    def get(self, category):
        return self.score_dict[category]

    def add(self, another_score):
        self.score_dict['서비스'] += another_score.get('서비스')
        self.score_dict['가격'] += another_score.get('가격')
        self.score_dict['청결도'] += another_score.get('청결도')
        self.score_dict['객실'] += another_score.get('객실')
        self.score_dict['침대의 퀄리티'] += another_score.get('침대의 퀄리티')
        self.score_dict['장소'] += another_score.get('장소')

    def __str__(self):
        return str(self.score_dict)


def split_slash(mystr):
    return mystr.split('/')[0]


def load_senti_dict(senti_dict):
    with open('Emotional_Word_Dictionary_RES_v1.2.txt', 'r') as dict_file:
        dict_reader = csv.reader(dict_file, delimiter='\t')
        for row in dict_reader:
            if len(row) != 12:
                continue
            word = split_slash(row[2])
            senti_dict[word] = float(row[11])


def load_classification(classification):
    with open('classification.json', 'r') as class_file:
        print('loading classification')
        return json.load(class_file)


def summarize(word, nearest_NP):
    NP_score = Score()
    for NPword in list(nearest_NP):
        if NPword[0] in classification:
            NP_score.increase(classification[NPword[0]], senti_dict[word])

    return NP_score


def sentiment_analysis(subtrees):
    review_score = Score()
    nearest_NP = None
    for i in range(len(subtrees)):
        subtree = subtrees[i]

        if subtree.label() == 'NP':
            nearest_NP = subtree

        if nearest_NP is not None:
            for word in list(subtree):
                if word[0] in senti_dict:
                    review_score.add(summarize(word[0], nearest_NP))

    return review_score


def parse_review(review):
    words = hannanum.pos(review['text'])
    chunks = parser.parse(words)

    subtrees = list(chunks.subtrees())
    return (chunks, sentiment_analysis(subtrees))


def open_reviews():
    res = open('result.txt', 'w')

    c = 0
    total_score = Score()

    for filename in glob.glob('reviews/*.json'):
        with open(filename, 'r') as raw_file:
            print('parsing %s...' % filename)
            res.write('============\nparsing %s...\n' % filename)
            raw_data = json.load(raw_file)

            for review in raw_data:
                temp = parse_review(review)
                c += 1
                total_score.add(temp[1])

                res.write('\n')
                res.write('[%s]' % review['title'])
                res.write('\n')
                res.write(review['text'])
                res.write('\n')
                if test is True:
                    temp[0].pprint(stream=res)
                    res.write('\n')
                res.write(str(temp[1]))
                res.write('\n\n')

                # print(review['title'])
                # print(temp)
        if test is True:
            break

    res.write('\n\n======TOTAL======\n')
    res.write('서비스: %f\n' % (total_score.get('서비스') / c))
    res.write('가격: %f\n' % (total_score.get('가격') / c))
    res.write('청결도: %f\n' % (total_score.get('청결도') / c))
    res.write('객실: %f\n' % (total_score.get('객실') / c))
    res.write('침대의 퀄리티: %f\n' % (total_score.get('침대의 퀄리티') / c))
    res.write('장소: %f\n' % (total_score.get('장소') / c))

    res.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test = True
    classification = load_classification(classification)
    load_senti_dict(senti_dict)
    open_reviews()
