
'''
GET ALL GRAPHS AS SUBPLOTS
'''
''' IMPORTS '''
import pandas as pd
import numpy as np
from collections import Counter
from dateutil.relativedelta import relativedelta
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs

jobs_df = pd.read_json('job_data.json', orient='table')

''' SHOWING GRAPHS '''
def job_categories():

    cat_ser = jobs_df['job_cat'].reset_index(drop=True)
    for x in range(len(cat_ser)):
        if 'Engineer' in cat_ser[x]:
            cat_ser[x] = cat_ser[x].replace('Engineer', '')
        elif 'Analyst' in cat_ser[x]:
            cat_ser[x] = 'Analyst'

    return cat_ser


def initial_responses():

    X = jobs_df.loc[:, ['initial_response']].reset_index('company_name', drop=True)
    X = X.reset_index().sort_values('date_applied').reset_index(drop=True)

    # gb_df = X.groupby('date_applied').value_counts().unstack(fill_value=0)

    u_dates = sorted(list(X.date_applied))
    formatted_dates = [str(pd.to_datetime(x).strftime('%b %-d')) for x in u_dates]

    r_dict = {
        'date_applied': formatted_dates,
        'initial_response': list(X.initial_response)
    }

    r_df = pd.DataFrame(data=r_dict)

    return r_df


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
    responses_df = pd.DataFrame([immediate_rejection, rejected_post_int, no_response, waiting],
                                index=dts_array)

    return responses_df


def two_by_two():
    # set figure
    sns.set_theme(style='white')
    fig = plt.figure(constrained_layout=True, figsize=(20,10))
    spec = gs.GridSpec(ncols=2, nrows=2, figure=fig)
    ax1 = fig.add_subplot(spec[0, 0])
    ax2 = fig.add_subplot(spec[0, 1])
    ax3 = fig.add_subplot(spec[1, :])

    # cat plot
    cat_ser = job_categories()
    sns.countplot(ax=ax1, x=cat_ser, palette='ocean')
    ax1.set_title('Job Categories')
    ax1.set_xlabel('Category')

    # responses plot
    r_df = initial_responses()
    r_pal = sns.color_palette('magma', 10)
    sns.countplot(
        ax=ax2,
        x=r_df.date_applied,
        hue=r_df.initial_response,
        palette=[r_pal[2], r_pal[5], r_pal[9]]
    )
    ax2.set_title('Initial Responses')
    ax2.set_xlabel('Date Applied')
    ax2.legend(loc=9)

    # timeline
    responses_df = apps_timeline()
    cat_pal = sns.color_palette("inferno", 10)

    second = np.array(responses_df.loc[:, 'rejected_post_int']) + \
                np.array(responses_df.loc[:, 'immediate_rejection'])
    top = second + np.array(responses_df.loc[:, 'no_response'])

    for responses in responses_df.columns:
        ax3.bar(
            x=responses_df.index,
            height=responses_df.immediate_rejection,
            width=1,
            label=f'Immediate Rejection',
            color=cat_pal[0]
        )

    ax3.bar(
        x=responses_df.index,
        height=responses_df.immediate_rejection,
        width=1,
        label='Immediate Rejection',
        color=cat_pal[0]
    )
    ax3.bar(
        x=dts_array,
        height=rejected_post_int,
        width=1,
        bottom=immediate_rejection,
        label='Rejected Post-Interview',
        color=cat_pal[2]
    )
    ax3.bar(
        x=dts_array,
        height=no_response,
        width=1,
        bottom=second,
        label='No Response',
        color=cat_pal[4]
    )
    ax3.bar(
        x=dts_array,
        height=waiting,
        width=1,
        bottom=top,
        label='In Interviews',
        color='yellowgreen'
    )

    # x axis date labels
    x_lines = pd.date_range(
        pd.to_datetime(dts_array[0]) - relativedelta(days=5),
        pd.to_datetime(dts_array[-1]) + relativedelta(days=5), freq='SMS'
    )
    x_labes = [x.strftime('%b %-d') for x in x_lines]
    ax3.set_xticks(x_lines)
    ax3.set_xticklabels(x_labes)
    ax3.set_ybound(0, 7)

    ax3.set_xlabel('Date Applied')
    ax3.set_ylabel('Count')
    ax3.set_title('Dates Applied and Outcomes of Job Applications')
    ax3.legend(loc=9)

    # plt.xticks(rotation='horizontal')
    plt.show()

    return
