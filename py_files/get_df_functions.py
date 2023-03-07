'''
GET ALL GRAPHS AS SUBPLOTS
'''

''' IMPORTS '''
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from py_files.data_functions import read_df


''' GLOBAL VARIABLES '''
jobs_df = read_df()


''' SHOWING GRAPHS '''
def get_slim_cats():

    # get reformatted categories column to fit on graphs
    cat_ser = jobs_df['job_cat']
    for x in range(len(cat_ser)):
        if 'Data Engineer' == cat_ser[x]:
            cat_ser[x] = 'DE'
        elif 'Data Analyst' == cat_ser[x]:
            cat_ser[x] = 'DA'
        elif 'Engineer' in cat_ser[x]:
            cat_ser[x] = cat_ser[x].replace('Engineer', '')

    return cat_ser.sort_values()


def get_ohe_df():

    X = jobs_df.loc[:, ['date_applied', 'initial_response']]
    X = X.sort_values('date_applied')

    gb_df = X.groupby('date_applied').value_counts().unstack(fill_value=0)

    u_dates = sorted(list(set(X.date_applied)))
    formatted_dates = [str(pd.to_datetime(x).strftime('%b %-d')) for x in u_dates]

    r_dict = {
        'Rejected': list(gb_df['Rejected']),
        'No Response': list(gb_df['No Response']),
        'Passed': list(gb_df['Passed'])
    }

    r_df = pd.DataFrame(data=r_dict, index=formatted_dates)

    return r_df, formatted_dates


def get_responses():

    slim_df = jobs_df.loc[:, ['date_applied', 'initial_response', 'final_outcome']]

    # sort by date
    outcomes_df = slim_df.sort_values('date_applied', ignore_index=True)

    # re-label final outcome by init and final responses
    for idx in outcomes_df.index:
        row = outcomes_df.loc[idx]
        if row.final_outcome == 'Rejected' and row.initial_response == "Passed":
            outcomes_df.loc[idx, ['final_outcome']] = 'Rejected Post-Interview'
        elif row.initial_response == 'Rejected':
            outcomes_df.loc[idx, ['final_outcome']] = 'Immediate Rejection'
        elif row.initial_response == 'No Response':
            outcomes_df.loc[idx, ['final_outcome']] = 'No Response'

    outcomes_df.drop(columns=['initial_response'], inplace=True)

    grouped_df = outcomes_df.groupby('date_applied').value_counts().unstack(fill_value=0)

    keys = ['date_applied', 'Immediate Rejection', 'Rejected Post-Interview', 'No Response', 'In Interviews']
    responses_df = grouped_df.reset_index().reindex(columns=keys)

    return responses_df


def get_prep_df():

    prep_df = read_df('prep*').drop(columns='site')

    grouped_df = prep_df.groupby('date_completed').count().reset_index()

    return grouped_df.rename(columns={'Submissions': 'Practice Problems'})


def get_timeline_df():

    rdf = get_responses().rename(columns={'date_applied': 'date'})
    pdf = get_prep_df().rename(columns={'date_completed': 'date'})

    condf = pd.concat([rdf, pdf]).fillna(0).convert_dtypes()

    grouped_df = condf.groupby('date').sum().reset_index().sort_values('date')

    tl_df = grouped_df.set_index('date')

    return tl_df


def get_encoded_cols():
    # slice and label encode features
    X = jobs_df.loc[:, 'job_cat':'method']
    bi_columns = ['department', 'recruiter', 'referral', 'method']
    cat_columns = ['job_cat', 'location']

    X.loc[X['method'] == 'linkedin', 'method'] = 0
    for c in bi_columns:
        X.loc[X[c].isna(), c] = 0
        X.loc[X[c] != 0, c] = 1

    le = LabelEncoder()
    for c in cat_columns:
        X.loc[:, c] = le.fit_transform(X.loc[:, c])

    # custom encode target (init. response)
    y = jobs_df['initial_response'].reset_index(drop=True)
    for idx, v in y.items():
        if v == 'Rejected':
            y[idx] = -1
        elif v == 'No Response':
            y[idx] = 0
        else:
            y[idx] = 1

    df = X.merge(y.to_frame('initial_response'), left_index=True, right_index=True)

    return df


def get_location_df():

    X = jobs_df.loc[:, ['location', 'initial_response']]

    for idx, r in X.location.items():
        if 'remote' in r.lower():
            X.loc[idx, 'location'] = 'Remote'

    return X.sort_values('location').reset_index()
