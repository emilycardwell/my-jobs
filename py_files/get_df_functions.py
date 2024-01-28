'''
GET ALL GRAPHS AS SUBPLOTS
'''

''' IMPORTS '''
import pandas as pd
import numpy as np
from IPython.display import display

# from sklearn.preprocessing import LabelEncoder

from py_files.data_functions import read_df


''' GLOBAL VARIABLES '''
jobs_df = read_df("jobs")
unique_dates = sorted(list(set(jobs_df.date_applied)))
string_dates = [str(pd.to_datetime(x).strftime('%b %-d')) for x in unique_dates]


''' SHOWING GRAPHS '''
def get_slim_cats():

    # get reformatted categories column to fit on graphs
    cat_ser = jobs_df['job_cat']
    for x in range(len(cat_ser)):
        if 'Data Engineer' == cat_ser[x]:
            cat_ser.iloc[x] = 'Data Engr.'
        elif 'Data Analyst' == cat_ser[x]:
            cat_ser.iloc[x] = 'Data An.'
        # elif 'Python' in cat_ser[x]:
        #     cat_ser.iloc[x] = 'Software'
        elif 'Technical Writer' == cat_ser[x]:
            cat_ser.iloc[x] = 'Tech Writer'
        elif 'Backend' in cat_ser[x]:
            cat_ser.iloc[x] = 'Bknd Engr.'
        elif 'Engineer' in cat_ser[x]:
            cat_ser.iloc[x] = cat_ser[x].replace('Engineer', 'Engr.')

    return cat_ser.sort_values()

def get_location_df():

    X = jobs_df.loc[:, ['location']]

    for idx, r in X.location.items():
        if 'remote' in r.lower():
            X.loc[idx, 'location'] = 'Remote'
        elif 'Germany' in r:
            X.loc[idx, 'location'] = 'Germany'
        elif 'Austria' in r:
            X.loc[idx, 'location'] = 'Austria'
        elif 'Copenhagen' in r:
            X.loc[idx, 'location'] = 'Copenhagen'
        elif "Berlin" in r:
            X.loc[idx, 'location'] = 'Berlin'
        else:
            X.loc[idx, 'location'] = 'Other'

    return X

def get_init_responses():
    slim_df = jobs_df.loc[:, ['date_applied', 'initial_response']]
    outcomes_df = slim_df.sort_values('date_applied').drop(columns='date_applied')
    return outcomes_df

def get_ohe_df():

    X = jobs_df.loc[:, ['date_applied', 'initial_response']]
    X = X.sort_values('date_applied', ignore_index=True)

    gb_df = X.groupby('date_applied').value_counts().unstack(fill_value=0)

    if 'Rejected' not in gb_df.columns:
        gb_df['Rejected'] = 0
    if 'No Response' not in gb_df.columns:
        gb_df['No Response'] = 0
    if 'Passed' not in gb_df.columns:
        gb_df['Passed'] = 0

    r_dict = {
        'Rejected': list(gb_df['Rejected']),
        'No Response': list(gb_df['No Response']),
        'Passed': list(gb_df['Passed'])
    }

    r_df = pd.DataFrame(data=r_dict, index=string_dates).reset_index(drop=True)

    return r_df

def get_outcomes():
    slim_df = jobs_df.loc[:, ['date_applied', 'final_outcome']]
    outcomes_df = slim_df.sort_values('date_applied')
    return outcomes_df

def get_responses():

    df = get_outcomes()
    grouped_df = df.groupby('date_applied').value_counts().unstack(fill_value=0)

    all_keys = ['No Response', 'Rejection', 'No Offer', 'In Interviews',
                'Offer'
                ]

    keys = list(grouped_df.keys())
    nan_keys = list(set(all_keys) - set(keys))
    yes_keys = list(set(all_keys) - set(nan_keys))

    available_df = pd.DataFrame({x: list(grouped_df[x]) for x in yes_keys}, index=unique_dates)

    if nan_keys:
        nan_df = pd.DataFrame({x: len(available_df)*[0] for x in nan_keys}, index=unique_dates)
        responses_df = pd.concat([available_df, nan_df], axis=1)
        return responses_df

    return available_df

def get_prep_df():

    df = read_df('prep').drop(columns='submissions')

    dates = sorted(list(set(df.date_completed)))
    f_dates = [str(pd.to_datetime(x).strftime('%b %-d')) for x in dates]

    grouped_df = df.groupby('date_completed').value_counts().unstack(fill_value=0)

    cols = sorted(list(df.site.unique()))
    keys = [x.replace("_", "").capitalize() for x in cols]

    prep_df = pd.DataFrame(
        {keys[x]: list(grouped_df[cols[x]]) for x in range(len(cols))},
        index=f_dates
    )

    return prep_df

def get_slim_prep_df():

    df = read_df('prep').drop(columns='site')

    grouped_df = df.groupby('date_completed').count().reset_index()

    dates = grouped_df.date_completed.values

    prep_df = pd.DataFrame({"Coding Practice": list(grouped_df["submissions"])},
                           index=dates)

    return prep_df

def get_work_col(column):

    work_df = read_df('work')[column]

    return work_df

def get_work_df():

    df = read_df('work').drop(columns='category')

    dates = sorted(list(set(df.date_completed)))
    f_dates = [str(pd.to_datetime(x).strftime('%b %-d')) for x in dates]

    grouped_df = df.groupby('date_completed').value_counts().unstack(fill_value=0)

    cols = sorted(list(df.job.unique()))
    keys = [x.capitalize() for x in cols]

    work_df = pd.DataFrame(
        {keys[x]: list(grouped_df[cols[x]]) for x in range(len(cols))},
        index=f_dates
    )

    return work_df

def get_slim_work_df():

    df = read_df('work').drop(columns='category')
    grouped_df = df.groupby('date_completed').count().reset_index()
    dates = grouped_df.date_completed.values
    work_df = pd.DataFrame({"Work": list(grouped_df["job"])}, index=dates)

    return work_df

def get_timeline_df():

    rdf = get_responses()
    pdf = get_slim_prep_df()
    wdf = get_slim_work_df()

    jdf = pd.merge(rdf, pdf, how='outer', left_index=True, right_index=True)
    jdf2 = pd.merge(jdf, wdf, how='outer', left_index=True, right_index=True)
    filled_df = jdf2.fillna(0).convert_dtypes().reset_index(names='Date')

    tl_df = filled_df.set_index('Date')

    return tl_df


def get_encoded_cols():
    # slice and binary features
    bi_columns = ['department', 'recruiter', 'referral']
    X = jobs_df.loc[:, bi_columns].copy()

    # custom encode binary features
    X.loc[X['department'].isna(), 'department'] = 'Company'
    X.loc[X['department'] != 'Company', 'department'] = 'Department'

    for c in ['recruiter', 'referral']:
        X.loc[X[c].isna(), c] = f"No {c}"
        X.loc[X[c] != f"No {c}", c] = f"{c.capitalize()}"

    # add named categorical features
    X1 = jobs_df.loc[:, ['method']].copy()
    for x in ['linkedin', 'stepstone', 'indeed']:
        X1.loc[X1['method'] == x, 'method'] = 'Platform'

    outcomes = get_outcomes().drop(columns='date_applied')
    loc_df = get_location_df()

    df = X.join(X1).join(loc_df).join(outcomes)

    return df

'''
unused code for label encoder
'''
    # le = LabelEncoder()
    # for c in cat_columns:
    #     X.loc[:, c] = le.fit_transform(X.loc[:, c])

    # # custom encode target (init. response)
    # y = jobs_df['initial_response'].reset_index(drop=True)
    # for idx, v in y.items():
    #     if v == 'Rejected':
    #         y[idx] = -1
    #     elif v == 'No Response':
    #         y[idx] = 0
    #     else:
    #         y[idx] = 1



'''
replaced with shorter code
'''
# def get_outcomes(jobs_df=read_df()):

#     slim_df = jobs_df.loc[:, ['date_applied', 'company_name', 'initial_response', 'final_outcome']]

#     # sort by date
#     outcomes_df = slim_df.sort_values('date_applied')

#     # re-label final outcome by init and final responses
#     for idx in outcomes_df.index:
#         row = outcomes_df.loc[idx]
#         if row.final_outcome != 'Offer':
#             pass
#         elif row.final_outcome == 'Rejected' and row.initial_response == "Passed":
#             outcomes_df.loc[idx, ['final_outcome']] = 'Rejected Post-Interview'
#         elif row.initial_response == 'Rejected':
#             outcomes_df.loc[idx, ['final_outcome']] = 'Immediate Rejection'
#         elif row.initial_response == 'No Response':
#             outcomes_df.loc[idx, ['final_outcome']] = 'No Response'
#         elif row.initial_response == 'Passed':
#             outcomes_df.loc[idx, ['final_outcome']] = 'In Interviews'
#         else:
#             print("error:", row.initial_response)

#     outcomes_df.drop(columns=['initial_response'], inplace=True)

#     return outcomes_df
