''' IMPORTS '''
import pandas as pd
from dateutil.relativedelta import relativedelta

import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import seaborn as sns
sns.set_theme(style='white')

from py_files.data_functions import read_df
from py_files.get_df_functions import get_slim_cats, get_ohe_df, \
                                        get_responses, get_encoded_cols, \
                                        get_location_df, get_prep_df


''' GLOBAL VARIABLES'''
jobs_df = read_df()


'''
DATA EXPLORATION
'''
def show_pair():
    X = get_encoded_cols()
    fig = sns.pairplot(
        data=X,
        hue='initial_response',
        palette=['tomato', 'silver', 'royalblue'],
        corner=True,
        diag_kind='kde',
        kind='hist'
    )
    return plt.show(fig)


def show_cat_ref():

    X = jobs_df.loc[:, ['job_cat', 'location', 'initial_response']].reset_index(drop=True)
    X.loc[:, 'job_cat'] = get_slim_cats()

    for idx, r in X.location.items():
        if 'remote' in r.lower():
            X.loc[idx, 'location'] = 'Remote'

    fig, ax = plt.subplots(figsize=(10,5))

    sns.swarmplot(
        data=X,
        y="location",
        x="job_cat",
        size=10,
        hue="initial_response",
        palette=['black', 'silver', 'limegreen'],
        ax=ax,
    )

    ax.set_title('Job Category, Location, & Initial Response')
    ax.set_xlabel('Category')
    ax.set_ylabel('Location')
    ax.get_legend().remove()

    return plt.show(fig)


'''
SINGLE GRAPHS
'''
def show_job_categories():
    cat_slim_ser = get_slim_cats()
    fig, ax = plt.subplots(figsize=(6,4))
    fig = sns.countplot(x=cat_slim_ser, palette='magma')
    ax.set_title('Job Category Counts')
    ax.set_xlabel('Category')
    plt.xticks(rotation=45)

    return plt.show(fig)


def show_initial_responses():

    r_df, formatted_dates = get_ohe_df()
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

    plt.xticks(
        [0, len(formatted_dates)-1],
        [formatted_dates[0], formatted_dates[-1]],
        rotation='horizontal'
    )

    return plt.show(r_fig)


def show_apps_timeline():

    responses_df, x_tick_values, x_tick_labels = get_responses()
    cat_pal = sns.color_palette("viridis", 8)
    cat_pal_list = [cat_pal[0], cat_pal[3], 'silver', cat_pal[7]]
    t_accum = [0] * len(responses_df)

    fig, ax = plt.subplots(figsize=(12,4))

    for responses, color in zip(responses_df.columns, cat_pal_list):
        ax.bar(
            x=responses_df.index,
            height=list(responses_df[responses]),
            bottom=t_accum,
            width=1,
            label=responses,
            color=color
        )
        t_accum += responses_df[responses]

    ax.set_xticks(x_tick_values)
    ax.set_xticklabels(x_tick_labels)
    ax.set_ybound(0, 7)
    ax.set_xlabel('Date Applied')
    ax.set_ylabel('Count')
    ax.set_title('Dates Applied and Outcomes of Job Applications')
    ax.legend(loc='upper center')

    return plt.show(fig)


'''
MULTIPLOTS
'''
def two_by_two_subplt():

    cat_ser = get_slim_cats()
    loc_df = get_location_df()

    # set figure
    fig = plt.figure(constrained_layout=True, figsize=(15,15))
    spec = gs.GridSpec(ncols=2, nrows=3, figure=fig)
    ax1 = fig.add_subplot(spec[0, 0])
    ax1_1 = fig.add_subplot(spec[0, 1])
    ax2 = fig.add_subplot(spec[1, 0])
    ax2_2 = fig.add_subplot(spec[1, 1])
    ax3 = fig.add_subplot(spec[2, :])


    # category plot
    sns.countplot(ax=ax1, x=cat_ser, color='blueviolet', saturation=.3)
    ax1.set_title('Job Type Counts')
    ax1.set_xlabel('Job Type')

    # location plot (basic)
    sns.countplot(ax=ax1_1, x=loc_df.location, color='crimson', saturation=.5)
    ax1_1.set_title('Job Location Counts')
    ax1_1.set_xlabel('Location')

    # category plot (by initial response)
    sns.countplot(
        ax=ax2,
        x=cat_ser,
        hue=loc_df.initial_response,
        palette='Purples_r'
    )

    ax2.set_title('Job Type & Initial Responses')
    ax2.set_xlabel('Job Type')
    ax2.legend(loc='upper left')

    # location plot (by initial response)
    sns.countplot(
        ax=ax2_2,
        x=loc_df.location,
        hue=loc_df.initial_response,
        palette='Reds_r'
    )

    ax2_2.set_title('Location & Initial Responses')
    ax2_2.set_xlabel('Location')
    ax2_2.legend(loc='upper right')

    # timeline
    responses_df = get_responses()
    cat_pal = sns.color_palette("viridis", 10)
    cat_pal_list = [cat_pal[0], cat_pal[3], cat_pal[5], cat_pal[9]]
    t_accum = [0] * len(responses_df)
    print(responses_df.index)

    for responses, color in zip(responses_df.columns, cat_pal_list):
        ax3.bar(
            x=pd.to_datetime(responses_df.index),
            height=list(responses_df[responses]),
            bottom=t_accum,
            width=1,
            label=responses,
            color=color
        )
        t_accum += responses_df[responses]

    x_ticks = ax3.get_xticks()
    print(x_ticks)
    # x axis date labels
    x_tick_values = pd.date_range(pd.to_datetime(x_ticks[0]),
                                  pd.to_datetime(x_ticks[-1]),
                                  freq='SMS')
    x_tick_labels = [x.strftime('%d %m') for x in x_tick_values]

    ax3.set_xticks(x_tick_values)
    ax3.set_xticklabels(x_tick_labels)
    ax3.set_ybound(0, 7)

    ax3.set_alpha(.5)
    ax3.set_xlabel('Date Applied')
    ax3.set_ylabel('Count')
    ax3.set_title('Timeline of Job Applications and Coding Practice')
    ax3.legend(loc='upper right')

    plt.show()

    return
