from sklearn import svm, model_selection
from sklearn.metrics import recall_score, precision_score, f1_score
import json
import sys

categories = ['서비스', '가격', '청결도', '객실', '침대의 퀄리티', '장소']
C = 1


def load_true_reviews():
    with open('true_review_scores.json', 'r') as rf:
        print('Loading all reviews with category scores...')
        return json.load(rf)


def svm_learn(category, data):
    extracted_data = list()
    for scores in data:
        if ((scores['analyzed'][category] == 0)
                or (category not in scores['recommend'])):
            continue
        extracted_data.append(
            (scores['analyzed'][category], scores['recommend'][category]))

    print()
    print(category, len(extracted_data))
    X = list(map(lambda x: [x[0]], extracted_data))
    y = list(map(lambda x: 0 if x[1] < 5 else 1,
                 extracted_data))
    print(float(sum(y) / len(y)))
    # y = list(map(lambda x: x[1], extracted_data))

    print('Start training %s' % category)
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        X, y, test_size=0.2)

    for kernel in ['linear', 'rbf', 'sigmoid']:
        clf = svm.SVC(kernel=kernel, C=C)
        # clf = neighbors.KNeighborsClassifier()
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        accuracy = clf.score(X_test, y_test)
        recall = recall_score(y_test, y_pred, average="macro")
        precision = precision_score(y_test, y_pred, average="macro")
        f1 = f1_score(y_test, y_pred, average="macro")
        print(kernel, 'accuracy:', accuracy)
        print(kernel, 'recall:', recall)
        print(kernel, 'precision:', precision)
        print(kernel, 'f1_score:', f1)

    '''
    for x_test in X_test:
        if clf.predict([x_test])[0] < 5.0:
            print(x_test, clf.predict([x_test])[0])
    '''


if __name__ == '__main__':
    data = load_true_reviews()
    categories_to_learn = list()

    if len(sys.argv) > 1:
        for argv in sys.argv:
            if argv in categories:
                categories_to_learn.append(argv)
            elif argv == 'all':
                categories_to_learn = categories
                break
    else:
        print('Give arguments like \'서비스\', \'가격\', \'청결도\', \'객실\', \'침대의 퀄리티\', \'장소\', or \'all\'')

    print('C:', C)
    for category in categories_to_learn:
        svm_learn(category, data)
