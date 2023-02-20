''' IMPORTS '''
import pandas as pd
import numpy as np
from collections import Counter
from dateutil.relativedelta import relativedelta
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.impute import SimpleImputer

jobs_df = pd.read_json('job_data.json', orient='table')

''' SHOWING GRAPHS '''
def job_categories():

    cat_ser = jobs_df['job_cat'].reset_index(drop=True)
    for x in range(len(cat_ser)):
        if 'Engineer' in cat_ser[x]:
            cat_ser[x] = cat_ser[x].replace('Engineer', '')
        elif 'Analyst' in cat_ser[x]:
            cat_ser[x] = 'Analyst'

    sns.set_theme(style='white')
    fig1, ax1 = plt.subplots(figsize=(6,4))
    fig1 = sns.countplot(x=cat_ser, palette='magma')
    ax1.set_title('Job Categories')
    ax1.set_xlabel('Job Category')
    plt.xticks(rotation=45)
    plt.show(fig1)

    return fig1

def initial_responses():

    X = jobs_df.loc[:, ['initial_response']].reset_index('company_name', drop=True)
    X = X.reset_index().sort_values('date_applied')

    gb_df = X.groupby('date_applied').value_counts().unstack(fill_value=0)
    u_dates = sorted(list(set(X.date_applied)))
    formatted_dates = [str(pd.to_datetime(x).strftime('%b %-d')) for x in u_dates]

    r_dict = {'date_applied': formatted_dates,
                'Rejected': list(gb_df['Rejected']),
                'No Response': list(gb_df['No Response']),
                'Passed': list(gb_df['Passed'])
    }

    r_df = pd.DataFrame(data=r_dict)

    sns.set_theme(style='white')
    r_fig, ax = plt.subplots(figsize=(6,4))

    r_fig = r_df.plot(
        kind='bar',
        colormap=sns.color_palette('viridis', as_cmap=True),
        stacked=True,
        xlabel='Date Applied',
        title='Initial Responses',
        ax=ax,
        width=1
    )

    plt.xticks([0, len(formatted_dates)-1], [formatted_dates[0], formatted_dates[-1]], rotation='horizontal')
    plt.show(r_fig)

    return r_fig

def apps_timeline():

    outcomes_df = jobs_df.loc[:, ['initial_response', 'final_outcome']].droplevel(level=0).sort_index().reset_index()
    for idx in outcomes_df.index:
        row = outcomes_df.loc[idx]
        if row.final_outcome == 'Rejected' and row.initial_response == "Passed":
            row.final_outcome = 'Rejected Post-Interview'
        elif row.initial_response == 'Rejected':
            row.final_outcome = 'Immediate Rejection'
        elif row.initial_response == 'No Response':
            row.final_outcome = 'No Response'
    outcomes_df.drop(columns='initial_response', inplace=True)

    grouped_outcomes_df = outcomes_df.groupby('date_applied')
    outcome_dates = list(grouped_outcomes_df.groups.keys())
    outcomes_counter = [Counter(grouped_outcomes_df.get_group(date).final_outcome)\
        for date in outcome_dates]

    no_response = []
    immediate_rejection = []
    rejected_post_int = []
    waiting = []

    for x in outcomes_counter:
        no_response.append(x['No Response'])
        immediate_rejection.append(x['Immediate Rejection'])
        rejected_post_int.append(x['Rejected Post-Interview'])
        waiting.append(x['Waiting'])

    outcome_dts = [pd.to_datetime(x).strftime('%Y-%m-%d') for x in outcome_dates]
    dts_array = np.array(outcome_dts, dtype='datetime64')

    x_lines = pd.date_range(
        pd.to_datetime(dts_array[0]) - relativedelta(days=5),
        pd.to_datetime(dts_array[-1]) + relativedelta(days=2), freq='SMS'
    )
    x_labes = [x.strftime('%b %-d') for x in x_lines]

    sns.set_theme(style='white')
    fig2, ax2 = plt.subplots(figsize=(12,4))

    # cat_palette = ['black', 'crimson', 'grey', 'lightskyblue']
    cat_palette = sns.color_palette("viridis", 8)
    w = 1

    second = np.array(rejected_post_int) + np.array(immediate_rejection)
    top = second + np.array(no_response)

    fig2 = ax2.bar(
        dts_array, immediate_rejection, width=w, label='Immediate Rejection',
        color=cat_palette[0]
    )
    fig2 = ax2.bar(
        dts_array, rejected_post_int, width=w, bottom=immediate_rejection,
        label='Rejected Post-Interview', color=cat_palette[3]
    )
    fig2 = ax2.bar(
        dts_array, no_response, width=w, bottom=second, label='No Response',
        color='silver'
    )
    fig2 = ax2.bar(
        dts_array, waiting, width=w, bottom=top, label='In Interviews',
        color=cat_palette[7]
    )

    ax2.set_xticks(x_lines)
    ax2.set_xticklabels(x_labes)
    ax2.set_ybound(0, 7)

    ax2.set_xlabel('Date Applied')
    ax2.set_ylabel('Count')
    ax2.set_title('Dates Applied and Outcomes of Job Applications')
    ax2.legend(loc='upper center')

    plt.show(fig2)

    return fig2

def explore_data():

    X = jobs_df.loc[:][:'url'].reset_index(drop=True)
    print(X)
    y = jobs_df['initial_response']

    cat_columns = ['job_cat', 'location']
    bi_columns = ['department', 'recruiter', 'referral', 'method']

    cat_trans = make_pipeline(
        SimpleImputer(strategy='constant', fill_value='missing'),
        OneHotEncoder(handle_unknown='ignore')
    )

    bi_trans = make_pipeline(
        SimpleImputer(strategy='most_frequent'),
        OneHotEncoder(handle_unknown='ignore')
    )

    preproc = make_column_transformer(
        (cat_trans, cat_columns),
        (bi_trans, bi_columns)
    )

    X_trans = pd.DataFrame(preproc.fit_transform(X))
    print(X_trans)

    fig = sns.pairplot(
        X_trans,
        hue = y
    )

    return plt.show(fig)
