from konlpy.tag import Twitter
import glob
import sys
import json


def tag_all_reviews(norm, stem):
    twitter = Twitter()
    recommend_categories = set()
    for filename in glob.glob('reviews/*.json'):
        with open(filename, 'r') as raw_file:
            print('parsing %s...' % filename)
            raw_data = json.load(raw_file)

            for review in raw_data:
                review['tagged'] = twitter.pos(
                    review['text'], norm=norm, stem=stem)
                recommend_categories.update(list(review['recommend'].keys()))

            new_filename = 'tagged_reviews/%s' % filename.split('/')[1]
            with open(new_filename, 'w') as tagged_file:
                json.dump(raw_data, tagged_file, ensure_ascii=False,
                          sort_keys=True, indent=2, separators=(',', ': '))

    return recommend_categories


if __name__ == '__main__':
    norm, stem = False, False
    if len(sys.argv) > 1:
        if 'norm' in sys.argv:
            norm = True
        if 'stem' in sys.argv:
            stem = True

    print(tag_all_reviews(norm, stem))
