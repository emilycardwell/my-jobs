'''
GET ALL GRAPHS AS SUBPLOTS
'''

''' IMPORTS '''
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from py_files.data_functions import read_df


''' GLOBAL VARIABLES '''
jobs_df = read_df()
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
        elif 'Engineer' in cat_ser[x]:
            cat_ser.iloc[x] = cat_ser[x].replace('Engineer', 'Engr.')

    return cat_ser.sort_values()


def get_ohe_df():

    X = jobs_df.loc[:, ['date_applied', 'initial_response']]
    X = X.sort_values('date_applied', ignore_index=True)

    gb_df = X.groupby('date_applied').value_counts().unstack(fill_value=0)

    r_dict = {
        'Rejected': list(gb_df['Rejected']),
        'No Response': list(gb_df['No Response']),
        'Passed': list(gb_df['Passed'])
    }

    r_df = pd.DataFrame(data=r_dict, index=string_dates)

    return r_df

def get_location_df():

    X = jobs_df.loc[:, ['location', 'initial_response']]

    for idx, r in X.location.items():
        if 'remote' in r.lower():
            X.loc[idx, 'location'] = 'Remote'
        elif 'Germany' in r:
            X.loc[idx, 'location'] = 'DE (not Berlin)'
        elif 'Austria' in r:
            X.loc[idx, 'location'] = 'Austria'
        elif "Berlin" in r:
            X.loc[idx, 'location'] = 'Berlin'
        else:
            X.loc[idx, 'location'] = 'Other'

    return X

def get_responses():

    df = get_outcomes()

    grouped_df = df.groupby('date_applied').value_counts().unstack(fill_value=0)

    keys = ['Immediate Rejection', 'No Response', 'Rejected Post-Interview', 'In Interviews']
    responses_df = pd.DataFrame({x: list(grouped_df[x]) for x in keys}, index=unique_dates)

    return responses_df

def get_outcomes():

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
        elif row.initial_response == 'Passed':
            outcomes_df.loc[idx, ['final_outcome']] = 'In Interviews'
        else:
            print("error:", row.initial_response)

    outcomes_df.drop(columns=['initial_response'], inplace=True)

    return outcomes_df

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


def get_timeline_df():

    rdf = get_responses()
    pdf = get_slim_prep_df()

    jdf = rdf.join(pdf, how='outer').fillna(0).convert_dtypes().reset_index(names='Date')

    tl_df = jdf.set_index('Date')

    return tl_df


def get_encoded_cols():
    # slice and binary features
    bi_columns = ['department', 'recruiter', 'referral', 'method']
    X = jobs_df.loc[:, bi_columns].copy()

    # custom encode binary features
    X.loc[X['method'] != 'linkedin', 'method'] = 'Referral/Web'

    X.loc[X['department'].isna(), 'department'] = 'Company-Wide'
    X.loc[X['department'] != 'Company-Wide', 'department'] = 'Smaller Department'

    for c in ['recruiter', 'referral']:
        X.loc[X[c].isna(), c] = "No"
        X.loc[X[c] != "No", c] = "Yes"

    # add named categorical features
    X1 = get_location_df().drop(columns='initial_response')
    cats = get_slim_cats()
    outcomes = get_outcomes()

    df = X.join(cats).join(X1).join(outcomes)

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
