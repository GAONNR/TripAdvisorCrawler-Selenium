import glob
import json


print('Number of hotels: %d' % len(glob.glob('reviews/*.json')))
c = 0
for filename in glob.glob('reviews/*.json'):
    with open(filename, 'r') as raw_file:
        raw_data = json.load(raw_file)
        c += len(raw_data)
print('Number of reviews: %d' % c)
