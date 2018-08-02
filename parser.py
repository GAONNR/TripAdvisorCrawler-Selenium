import konlpy
import nltk
import glob
import sys
import json
import csv

grammar = '''
CLAUSE: {<N.*|V.*|J.*|M.*|I.*|O.*|U.*|X.*>*<E.*|S.*>*}
'''

blacklist = ['안', '하', '분']

hannanum = konlpy.tag.Hannanum()
kkma = konlpy.tag.Kkma()
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
        self.score_num = {
            '서비스': 0,
            '가격': 0,
            '청결도': 0,
            '객실': 0,
            '침대의 퀄리티': 0,
            '장소': 0
        }

    def increase(self, category, amount):
        self.score_dict[category] += amount
        self.score_num[category] += 1

    def get(self, category):
        return self.score_dict[category]

    def get_num(self, category):
        return self.score_num[category]

    def add(self, another_score):
        self.score_dict['서비스'] += another_score.get('서비스')
        self.score_dict['가격'] += another_score.get('가격')
        self.score_dict['청결도'] += another_score.get('청결도')
        self.score_dict['객실'] += another_score.get('객실')
        self.score_dict['침대의 퀄리티'] += another_score.get('침대의 퀄리티')
        self.score_dict['장소'] += another_score.get('장소')

        self.score_num['서비스'] += another_score.get_num('서비스')
        self.score_num['가격'] += another_score.get_num('가격')
        self.score_num['청결도'] += another_score.get_num('청결도')
        self.score_num['객실'] += another_score.get_num('객실')
        self.score_num['침대의 퀄리티'] += another_score.get_num('침대의 퀄리티')
        self.score_num['장소'] += another_score.get_num('장소')

    def divide(self, category):
        if self.score_num[category] == 0:
            return 0
        else:
            return self.score_dict[category] / float(self.score_num[category])

    def result(self):
        res = dict()
        res['서비스'] = self.divide('서비스')
        res['가격'] = self.divide('가격')
        res['청결도'] = self.divide('청결도')
        res['객실'] = self.divide('객실')
        res['침대의 퀄리티'] = self.divide('침대의 퀄리티')
        res['장소'] = self.divide('장소')

        return res

    def __str__(self):
        return str(self.result())


def write_iftest(f, mystr):
    if test is True:
        f.write(mystr)


def split_slash(mystr):
    return mystr.split('/')[0]


def load_senti_dict(senti_dict):
    with open('Emotional_Word_Dictionary_RES_v1.2.txt', 'r') as dict_file:
        dict_reader = csv.reader(dict_file, delimiter='\t')
        for row in dict_reader:
            if len(row) != 12:
                continue
            if 'affect_DIS/SATISFACTION_displeasure' == row[3]:
                continue
            if 'affect_UN/HAPPINESS_misery' == row[3]:
                continue

            word = split_slash(row[2])
            senti_dict[word] = float(row[11])


def load_classification(classification):
    with open('classification.json', 'r') as class_file:
        print('loading classification')
        return json.load(class_file)


def summarize(word, nouns):
    NP_score = Score()
    for noun in nouns:
        if noun[0] in classification and noun[0] != word and word not in blacklist:
            NP_score.increase(classification[noun[0]], senti_dict[word])
            write_iftest(res, '%s %s | %s %s\n' % (
                noun[0], word, classification[noun[0]],
                'Positive' if senti_dict[word] > 0 else 'Negative'))

    return NP_score


def get_nouns(clause):
    nouns = list()
    for word in list(clause):
        if word[1][0] == 'N':
            nouns.append(word)
    return nouns


def sentiment_analysis(clauses):
    review_score = Score()

    for clause in clauses:
        if clause.label() == 'S':
            continue
        nouns = get_nouns(clause)
        if len(nouns) < 1:
            continue

        for word in list(clause):
            if word[1][0] in ['N', 'V'] and word[0] in senti_dict:
                review_score.add(summarize(word[0], nouns))

    return review_score


def parse_review(review):
    # words = hannanum.pos(review['text'])
    words = kkma.pos(review['text'])
    chunks = parser.parse(words)
    clauses = list(chunks.subtrees())
    return (chunks, sentiment_analysis(clauses))


def open_reviews():
    global res
    res = open('result.txt', 'w')

    c = 0
    total_score = Score()

    true_list = list()

    for filename in glob.glob('reviews/*.json'):
        with open(filename, 'r') as raw_file:
            print('parsing %s...' % filename)
            write_iftest(res, '============\nparsing %s...\n' % filename)
            raw_data = json.load(raw_file)

            for review in raw_data:
                write_iftest(res, '\n')
                write_iftest(res, '[%s]' % review['title'])
                write_iftest(res, '\n')
                write_iftest(res, review['text'])
                write_iftest(res, '\n')
                write_iftest(res, '\n')

                temp = parse_review(review)
                c += 1
                total_score.add(temp[1])

                # write_iftest(res, '\n')
                # temp[0].pprint(stream=res)
                write_iftest(res, '\n')
                write_iftest(res, str(temp[1]))
                write_iftest(res, '\n\n')
                review['analyzed'] = temp[1].result()

                if len(review['recommend'].keys()) > 0:
                    true_list.append(
                        {'analyzed': review['analyzed'],
                         'recommend': review['recommend']})

            new_filename = 'analyzed_reviews/%s' % filename.split('/')[1]
            with open(new_filename, 'w') as analyzed_file:
                json.dump(raw_data, analyzed_file, ensure_ascii=False,
                          sort_keys=True, indent=2, separators=(',', ': '))
        if test is True:
            break

    print('\n\n======TOTAL======\n')
    print('서비스: %f\n' % (total_score.get('서비스') / c))
    print('가격: %f\n' % (total_score.get('가격') / c))
    print('청결도: %f\n' % (total_score.get('청결도') / c))
    print('객실: %f\n' % (total_score.get('객실') / c))
    print('침대의 퀄리티: %f\n' % (total_score.get('침대의 퀄리티') / c))
    print('장소: %f\n' % (total_score.get('장소') / c))

    print('\n\nLength of true review scores: %d' % len(true_list))
    with open('true_review_scores.json', 'w') as tf:
        json.dump(true_list, tf, ensure_ascii=False,
                  sort_keys=True, indent=2, separators=(',', ': '))

    res.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test = True
    classification = load_classification(classification)
    load_senti_dict(senti_dict)
    open_reviews()
