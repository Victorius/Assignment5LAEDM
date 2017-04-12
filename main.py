import pandas as pd
import datetime
import numpy as np
from sklearn import tree
from sklearn import metrics
from sklearn import neighbors
from sklearn import naive_bayes
from sklearn import ensemble


def percentage_of_success_submissions(data):
    result_dict = {}
    users = data.groupby(by='user_id')
    grouped = data.groupby(by=['user_id', 'status'])
    for i in users.size().index:
        actual_status = users.get_group(i).groupby('status').size().index
        correct_number = 0
        wrong_number = 0
        if 'correct' in actual_status:
            correct_number = len(grouped.get_group((i, 'correct')))
        if 'wrong' in actual_status:
            wrong_number = len(grouped.get_group((i, 'wrong')))
        result_dict[i] = correct_number / (correct_number + wrong_number)
    return result_dict


def average_subbmissions_per_day(dataframe):
    result_dict = {}
    users = dataframe.groupby(by='user_id')
    for i in users.size().index:
        date_per_user = {}
        for index, j in users.get_group(i).iterrows():
            submission = datetime.datetime.fromtimestamp(j['submission_time']).date()
            if submission in date_per_user:
                date_per_user[submission] += 1
            else:
                date_per_user[submission] = 1
        result_dict[i] = np.mean([date_per_user[v] for v in date_per_user])
    return result_dict


def classifier_f1(classifier, boundary_value, y_data, x_data):
    classifier = classifier.fit(x_data[:boundary_value], y_data[:boundary_value])
    result = classifier.predict(x_data[boundary_value:])
    precision = metrics.precision_score(y_data[boundary_value:], result)
    recall = metrics.recall_score(y_data[boundary_value:], result)
    f1 = 2 * precision * recall / (recall + precision)
    return f1


def new_one_feature(dataframe, submissions_df):
    grouped_df_by_user = dataframe.groupby(by='user_id')
    grouped_submissions_by_user = submissions_df.groupby(by='user_id')
    dictionary_comments = {}
    result_dict = {}
    for i in grouped_df_by_user.size().index:
        for j in grouped_df_by_user.get_group(i)['step_id']:
            if i in dictionary_comments:
                dictionary_comments[i].append(j)
            else:
                dictionary_comments[i] = [j]
    for ii in grouped_submissions_by_user.size().index:
        for jj in grouped_submissions_by_user.get_group(ii)['step_id']:
            if ii in dictionary_comments:
                if jj in dictionary_comments[ii]:
                    if ii in result_dict:
                        result_dict[ii] += 1
                    else:
                        result_dict[ii] = 1
                else:
                    if ii not in result_dict:
                        result_dict[ii] = 0
            else:
                result_dict[ii] = 0
    return result_dict


def calculation_the_best_result(submission_df, target_df, comments_df):
    new_feature_df = None
    if comments_df is not None:
        new_feature_df = new_one_feature(dataframe=comments_df, submissions_df=submission_df)
    feature_one = percentage_of_success_submissions(submission_df)
    feature_two = average_subbmissions_per_day(submission_df)
    x = []
    y = []
    count = 0
    for user in feature_one:
        small_array = [feature_one[user], feature_two[user]]
        if comments_df is not None:
            small_array.append(new_feature_df[user])
        var = target_df[target_df['user_id'] == user]['target'].values
        if len(var) > 0:
            x.append(small_array)
            y.append(var[0])
        else:
            count += 1
    boundary = (len(x) * 0.8).__int__()
    dataframe_result = pd.DataFrame(
        {'classifier': pd.Series(['DecisionTree', 'KNeighbors', 'NaiveBayes', 'RandomForest']),
         'value': pd.Series([classifier_f1(tree.DecisionTreeClassifier(), boundary, y, x),
                             classifier_f1(neighbors.KNeighborsClassifier(), boundary, y, x),
                             classifier_f1(naive_bayes.GaussianNB(), boundary, y, x),
                             classifier_f1(ensemble.RandomForestClassifier(), boundary, y, x)])}
        )
    print(dataframe_result)
    result = dataframe_result[dataframe_result['value'] == dataframe_result['value'].max()]
    print(result['classifier'] + ' shows best result: F1=' + result['value'].get_values().__str__())


df = pd.read_csv('submissions.csv', sep=",")
df2 = pd.read_csv('target.csv', sep=",")
df3 = pd.read_csv('comments.csv', sep=',')
print('Classification with two features based submmision.csv:')
calculation_the_best_result(submission_df=df, target_df=df2, comments_df=None)
print('Classification with three features based on submmision.csv and comments.csv:')
calculation_the_best_result(submission_df=df, target_df=df2, comments_df=df3)
