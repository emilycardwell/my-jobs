''' IMPORTS '''
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
from dateutil.relativedelta import relativedelta
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

jobs_df = pd.read_json('job_data.json', orient='table')

''' SHOWING GRAPHS '''
def job_categories():
    fig1, ax1 = plt.subplots(figsize=(10,3))
    fig1 = sns.countplot(x=jobs_df.job_cat, palette='magma')
    ax1.set_title('Job Categories')
    ax1.set_xlabel('Job Category')
    plt.xticks(rotation=45)
    return plt.show(fig1)

def initial_responses():

    X = jobs_df.loc[:, ['initial_response']].reset_index('company_name', drop=True)
    X = X.reset_index().sort_values('date_applied')

    sns.set_theme(style='white')
    r_fig, ax = plt.subplots(figsize=(6,3))

    r_fig = sns.histplot(
        data=X,
        x='date_applied',
        hue='initial_response',
        hue_order=['Passed', 'No Response', 'Rejected'],
        palette='viridis_r',
        multiple='stack',
        ax=ax
    )

    dates = list(set(X.date_applied))
    formatted_dates = [pd.to_datetime(x).strftime('%b %-d') for x in dates]

    r_fig.set_xticks(dates)
    r_fig.set_xticklabels([None]*len(dates))
    r_fig.set_xlabel('Date (Jan through current)')
    r_fig.set_title('Initial Responses')

    plt.show(r_fig)

    return

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


    fig2, ax2 = plt.subplots(figsize=(10,4))

    # cat_palette = ['black', 'crimson', 'grey', 'lightskyblue']
    cat_palette = sns.color_palette("viridis", 8)
    w = 1

    second = np.array(rejected_post_int) + np.array(immediate_rejection)
    top = second + np.array(no_response)

    ax2.bar(
        dts_array, immediate_rejection, width=w, label='Immediate Rejection',
        color=cat_palette[0]
    )
    ax2.bar(
        dts_array, rejected_post_int, width=w, bottom=immediate_rejection,
        label='Rejected Post-Interview', color=cat_palette[3]
    )
    ax2.bar(
        dts_array, no_response, width=w, bottom=second, label='No Response',
        color='silver'
    )
    ax2.bar(
        dts_array, waiting, width=w, bottom=top, label='In Interviews',
        color=cat_palette[7]
    )

    ax2.vlines(
        datetime.today(), 0, 7,
        linestyles='dashed', color='darkgreen', label='Today'
    )

    ax2.set_xticks(x_lines)
    ax2.set_xticklabels(x_labes)
    ax2.set_ybound(0, 7)

    ax2.set_xlabel('Date Applied')
    ax2.set_ylabel('Count')
    ax2.set_title('Dates Applied and Outcomes of Job Applications')
    ax2.legend(loc='upper center')

    return plt.show(fig2)
