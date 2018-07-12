from selenium import webdriver
import time
import sys
import json

driver = webdriver.PhantomJS('/usr/bin/phantomjs')

baseURL = 'https://www.tripadvisor.co.kr/'

number_of_reviews = 100
number_of_locations = 30

seoul_hotels_url = 'https://www.tripadvisor.co.kr/Hotels-g294197'


def get_full_url(review_kind, location_code, idx):
    if idx > 0:
        return '%s%s-d%d-Reviews-or%d' % (baseURL,
                                          review_kind,
                                          location_code,
                                          idx * 5)
    return '%s%s-d%d-Reviews' % (baseURL, review_kind, location_code)


def process_utf8(webstr):
    return webstr.encode('utf8').decode('utf8')


def get_overview_score(raw_review):
    score_elem = raw_review.find_element_by_css_selector('.ui_bubble_rating')
    return int(score_elem.get_attribute('class')[-2:]) / 10


def get_recommend(raw_review):
    recommend = {}
    raw_recommends = raw_review.find_elements_by_css_selector(
        '.recommend .recommend-answer')
    for raw_recommend in raw_recommends:
        score = get_overview_score(raw_recommend)
        category = process_utf8(raw_recommend.find_element_by_css_selector(
            '.recommend-description').text)
        recommend[category] = score

    return recommend


def get_5reviews(driver, idx, review_kind, location_code):
    reviews = []

    print(get_full_url(review_kind, location_code, idx))
    driver.get(get_full_url(review_kind, location_code, idx))
    time.sleep(5)

    try:
        show_more_buttons = driver.find_element_by_css_selector(
            '.listContainer .review-container .ulBlueLinks')
        show_more_buttons.click()
        time.sleep(3)

        raw_reviews = driver.find_elements_by_css_selector(
            '.listContainer .review-container')
        for raw_review in raw_reviews:
            reviews.append({
                'title': raw_review.find_element_by_css_selector(
                    '.noQuotes').text,
                'score': get_overview_score(raw_review),
                'recommend': get_recommend(raw_review),
                'text': raw_review.find_element_by_css_selector(
                    '.partial_entry').text
            })
    except:
        return []

    return reviews


def parse_hotel_reviews(url):
    print('Crawling hotel....')

    all_hotel_uids = []
    for i in range(number_of_locations // 30):
        back_parameter = ''
        if i != 0:
            back_parameter = '-oa%d' % i * 30

        driver.get(seoul_hotels_url + back_parameter)
        time.sleep(5)
        raw_hotels = driver.find_elements_by_css_selector(
            '.listing_title a')

        hotel_uids = map(lambda x: (process_utf8(x.text).replace(' ', '_'),
                                    int(x.get_attribute('id').split('_')[-1])), raw_hotels)
        all_hotel_uids += list(hotel_uids)

    for uid in all_hotel_uids:
        with open('reviews/%s-%d.json' % uid, 'w', encoding='utf8') as f:
            print('started crawling %d' % uid[1])
            all_reviews = []
            for i in range(number_of_reviews // 5):
                temp = get_5reviews(
                    driver, i, 'Restaurant_Review', uid[1])
                all_reviews += temp

            print(len(all_reviews))
            json.dump(all_reviews, f, ensure_ascii=False)
            print('finished crawling %d' % uid[1])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'hotel':
            parse_hotel_reviews(seoul_hotels_url)

    driver.close()
