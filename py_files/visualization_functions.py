''' IMPORTS '''
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
from dateutil.relativedelta import relativedelta
import seaborn as sns
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
    graph_df = X.groupby('date_applied').value_counts().unstack(fill_value=0)
    graph_df.index.name = None

    c_dict = {'No Response': 'wheat', 'Rejected': 'darksalmon', 'Passed': 'yellowgreen'}

    resp_graph = graph_df.loc[:, ['No Response', 'Rejected', 'Passed']].plot(
        figsize=(10,5),
        kind='bar',
        stacked=True,
        color=c_dict,
        ylabel='Count',
        ylim=(0,7),
        xlabel='Date Applied',
        title='Initial Responses'
    )

    formatted_dates = [pd.to_datetime(x).strftime('%b %-d') for x in graph_df.index]
    resp_graph.set_xticklabels(formatted_dates, rotation=0)

    return plt.show(resp_graph)

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


    fig2, ax2 = plt.subplots(figsize=(12,4))

    cat_palette = ['black', 'crimson', 'lightskyblue', '#ceaddc', 'yellowgreen']
    w = 1

    second = np.array(rejected_post_int) + np.array(immediate_rejection)
    top = second + np.array(no_response)

    ax2.bar(
        dts_array, immediate_rejection, width=w, label='Immediate Rejection',
        color=cat_palette[0], edgecolor='black', linewidth=0.5
    )
    ax2.bar(
        dts_array, rejected_post_int, width=w, bottom=immediate_rejection,
        label='Rejected Post-Interview', color=cat_palette[1],
        edgecolor='black', linewidth=0.5
    )
    ax2.bar(
        dts_array, no_response, width=w, bottom=second, label='No Response',
        color=cat_palette[2], edgecolor='black', linewidth=0.5
    )
    ax2.bar(
        dts_array, waiting, width=w, bottom=top, label='Waiting',
        color=cat_palette[3], edgecolor='black', linewidth=0.5
    )

    ax2.vlines(
        datetime.today(), 0, 7,
        linestyles='dashed', color='blue', label='Today'
    )

    ax2.set_xticks(x_lines)
    ax2.set_xticklabels(x_labes)
    ax2.set_ybound(0, 7)

    ax2.set_xlabel('Date Applied')
    ax2.set_ylabel('Count')
    ax2.set_title('Dates Applied and Outcomes of Job Applications')
    ax2.legend(loc='upper left')

    return plt.show(fig2)
