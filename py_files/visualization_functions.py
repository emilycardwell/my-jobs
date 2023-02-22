''' IMPORTS '''
import pandas as pd
import numpy as np
from collections import Counter
from dateutil.relativedelta import relativedelta
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

jobs_df = pd.read_json('job_data.json', orient='table')

cat_ser = jobs_df['job_cat'].reset_index(drop=True)
for x in range(len(cat_ser)):
    if 'Data Engineer' == cat_ser[x]:
        cat_ser[x] = 'DE'
    elif 'Data Analyst' == cat_ser[x]:
        cat_ser[x] = 'DA'
    elif 'Engineer' in cat_ser[x]:
        cat_ser[x] = cat_ser[x].replace('Engineer', '')

''' SHOWING GRAPHS '''
def job_categories():

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
    # slice and label encode features
    X = jobs_df.loc[:, 'job_cat':'method'].reset_index(drop=True)
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

    fig = sns.pairplot(
        data=df,
        hue='initial_response',
        palette=['silver', 'royalblue', 'chartreuse'],
        corner=True,
        diag_kind='kde',
        kind='hist'
    )

    return plt.show(fig)

def cat_ref_plt():

    X = jobs_df.loc[:, ['job_cat', 'location', 'initial_response']].reset_index(drop=True)

    for idx, r in X.location.items():
        if 'remote' in r.lower():
            X.loc[idx, 'location'] = 'Remote'

    X.loc[:, 'job_cat'] = cat_ser

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10,5))

    sns.swarmplot(
        data=X,
        y="location",
        x="job_cat",
        size=10,
        hue="initial_response",
        palette=['black', 'grey', 'limegreen'],
        ax=ax,
    )

    ax.set_title('Relationship between job category, department, and initial response')
    ax.set_xlabel('Job Category')
    ax.set_ylabel('Small Department?')
    ax.get_legend().remove()

    return plt.show(fig)
