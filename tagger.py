from konlpy.tag import Kkma
import glob
import sys
import json
import csv


def tag_all_reviews(norm, stem):
    kkma = Kkma()
    recommend_categories = set()
    nouns = dict()

    for filename in glob.glob('reviews/*.json'):
        with open(filename, 'r') as raw_file:
            print('parsing %s...' % filename)
            raw_data = json.load(raw_file)

            for review in raw_data:
                raw_tags = kkma.pos(
                    review['text'])
                review['tagged'] = list()
                for tag in raw_tags:
                    if tag[1][0] in ['N', 'V']:
                        review['tagged'].append(tag)
                    if tag[1][0] == 'N':
                        if tag[0] in nouns:
                            nouns[tag[0]] += 1
                        else:
                            nouns[tag[0]] = 0
                recommend_categories.update(list(review['recommend'].keys()))

            new_filename = 'tagged_reviews/%s' % filename.split('/')[1]
            with open(new_filename, 'w') as tagged_file:
                json.dump(raw_data, tagged_file, ensure_ascii=False,
                          sort_keys=True, indent=2, separators=(',', ': '))

    c = 0
    with open('nouns.csv', 'w') as nouns_file:
        nf = csv.writer(nouns_file)
        for key in nouns.keys():
            if nouns[key] >= 100:
                c += 1
                nf.writerow([key, nouns[key]])
    print(c)
    return recommend_categories


if __name__ == '__main__':
    norm, stem = False, False
    if len(sys.argv) > 1:
        if 'norm' in sys.argv:
            norm = True
        if 'stem' in sys.argv:
            stem = True

    print(tag_all_reviews(norm, stem))
