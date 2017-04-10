import pandas as pd
import datetime
import dateutil.relativedelta


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
    return result_dict


df = pd.read_csv("submissions.csv", sep=",")
# feature_one = percentage_of_success_submissions(df)
# print(feature_one)
feature_two = average_subbmissions_per_day(df)
# grouped = df.groupby(by=['user_id'])
# for i in grouped.size().index:
#    print(i)
#    print(len(grouped.get_group(i)))
