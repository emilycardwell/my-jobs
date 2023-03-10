''' IMPORTS '''
import pandas as pd

import matplotlib.dates as mpld
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from matplotlib.colors import ListedColormap as lc
import seaborn as sns
sns.set_theme(style='white')

from py_files.data_functions import read_df
from py_files.get_df_functions import get_slim_cats, get_ohe_df, \
                                        get_responses, get_encoded_cols, \
                                        get_location_df, get_timeline_df, \
                                        get_outcomes, get_prep_df


''' GLOBAL VARIABLES'''
jobs_df = read_df()
cat_pal = sns.color_palette('viridis', 9, desat=.75)
init_pal_list = [cat_pal[0], cat_pal[3], cat_pal[6]]
cat_cols = ['job_cat', 'location', 'department', 'recruiter',
            'referral', 'method', 'date_applied']

'''
SINGLE GRAPHS
'''
def show_job_categories():
    cat_slim_ser = get_slim_cats()
    fig, ax = plt.subplots(figsize=(10,4))
    fig = sns.countplot(x=cat_slim_ser, palette='magma')
    ax.set_title('Job Category Counts')
    ax.set_xlabel('Category')
    plt.xticks(rotation=45)

    return plt.show(fig)


def show_initial_responses():

    r_df= get_ohe_df()

    r_fig, ax = plt.subplots(figsize=(10,4))
    cmap = lc(init_pal_list)

    r_fig = r_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Applied',
        title='Initial Responses by Date',
        ax=ax,
        width=.9
    )
    plt.xticks(rotation='horizontal')

    return plt.show(r_fig)


def show_outcomes():

    responses_df = get_responses()
    responses_df.index = \
        [str(pd.to_datetime(x).strftime('%b %-d')) for x in responses_df.index]

    o_fig, ax = plt.subplots(figsize=(10,4))
    cmap = lc([cat_pal[0], cat_pal[3], 'maroon', cat_pal[8]])

    o_fig = responses_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Applied',
        title='Final Outcomes by Date',
        ax=ax,
        width=.9
    )

    plt.xticks(rotation='horizontal')

    return plt.show(o_fig)

def show_practice():

    prep_df = get_prep_df()

    fig, ax = plt.subplots(figsize=(15,4))

    fig = prep_df.plot(
        kind='bar',
        colormap=lc(['lightsteelblue', 'wheat', 'silver', 'thistle']),
        stacked=True,
        xlabel='Date Completed',
        title='Coding Practice Problems',
        ax=ax,
        width=.9
    )
    plt.xticks(rotation='horizontal')

    return plt.show(fig)


'''
MULTIPLOTS
'''
def show_subplt():

    cat_ser = get_slim_cats()
    loc_df = get_location_df()
    X = loc_df.join(cat_ser)

    # set figure
    fig = plt.figure(constrained_layout=True, figsize=(20,10))
    spec = gs.GridSpec(ncols=3, nrows=2, figure=fig)
    ax1 = fig.add_subplot(spec[0, 0:1])
    ax1_1 = fig.add_subplot(spec[0, 1:])
    ax2 = fig.add_subplot(spec[1, 0:1])
    ax2_2 = fig.add_subplot(spec[1, 1:])

    # location plot (basic)
    sns.countplot(ax=ax1, x=loc_df.location, palette='magma')
    ax1.set_title('Job Location Counts')
    ax1.set_xlabel('')

    # category plot
    sns.countplot(ax=ax1_1, x=cat_ser, palette='magma')
    ax1_1.set_title('Job Type Counts')
    ax1_1.set_xlabel('')

    # location plot (by initial response)
    sns.countplot(
        data=X,
        ax=ax2,
        x="location",
        hue="initial_response",
        palette=init_pal_list,
        width=.5,
        # saturation=1
    )

    ax2.set_title('Location & Initial Responses')
    ax2.set_xlabel('')
    ax2.legend(loc='upper right')

    # category plot (by initial response)
    sns.countplot(
        data=X.sort_values('job_cat'),
        ax=ax2_2,
        x="job_cat",
        hue="initial_response",
        palette=init_pal_list,
        width=.5,
        # saturation=1
    )

    ax2_2.set_title('Job Type & Initial Responses')
    ax2_2.set_xlabel('')
    ax2_2.legend(loc='best')

    return plt.show()

# timeline
def show_timeline():

    tl_df = get_timeline_df()
    feats = tl_df.reset_index(drop=True)
    x = list(tl_df.index)

    fig = plt.figure(constrained_layout=True, figsize=(25,6))
    spec = gs.GridSpec(ncols=4, nrows=1, figure=fig)
    ax1 = fig.add_subplot(spec[0, 0:3])
    ax1_1 = fig.add_subplot(spec[0, 3])

    cat_pal_list = [cat_pal[0], cat_pal[3], "maroon", cat_pal[8], 'silver']
    t_accum = [0] * len(feats)

    for col, color in zip(feats.columns, cat_pal_list):
        ax1.bar(
            x=pd.to_datetime(x),
            height=feats[col],
            bottom=t_accum,
            width=1,
            label=col,
            color=color
        )
        t_accum += feats[col]

    xform = mpld.DateFormatter('%b %-d')
    ax1.xaxis.set_major_formatter(xform)
    ax1.xaxis.set_major_locator(mpld.DayLocator(bymonthday=[1,15]))
    ax1.set_xlabel('Date Applied or Practice Problem Completed')

    ax1.set_ylim(top=10.5)
    ax1.set_ylabel('Count')
    ax1.set_title('Timeline of Job Applications and Coding Practice')
    ax1.legend(loc='upper right')

    totals_df = get_outcomes()
    sns.countplot(totals_df, x='final_outcome', ax=ax1_1, width=.5,
                  palette=[cat_pal[0], cat_pal[3], "maroon", cat_pal[8]])
    ax1_1.set_title('Job Application Outcomes')
    ax1_1.set_xlabel('')

    return plt.show(fig)


'''
DATA EXPLORATION
'''
def show_cat_compare(columns=cat_cols):

    df = get_encoded_cols()
    myVars = locals()

    fig_rows = 0
    fig_cols = 0
    for c in columns:
        if c == cat_cols[0] or c == cat_cols[1] or c == cat_cols[-1]:
            fig_rows += 1
        else:
            fig_cols += 1
    if fig_cols:
        fig_rows += 1

    fig = plt.figure(constrained_layout=True, figsize=(20,15))
    spec = gs.GridSpec(ncols=max(1, fig_cols), nrows=fig_rows, figure=fig)

    r = 0
    k = 0
    for i in range(len(columns)):
        ax = f'ax{i}'
        c = columns[i]

        if c == cat_cols[0] or c == cat_cols[1] or c == cat_cols[-1]:
            myVars[ax] = fig.add_subplot(spec[r, :])
            r += 1
        else:
            myVars[ax] = fig.add_subplot(spec[r, k])
            k += 1
            if k == fig_cols:
                r += 1
                k = 0

        sns.countplot(
            data=df, x=c, hue='initial_response',
            palette=init_pal_list, ax=myVars[ax]
        )
        myVars[ax].set_title(c)
        myVars[ax].set_xlabel("")
        if r != 1:
            myVars[ax].legend_ = None

    return plt.show(fig)



def show_cat_ref():

    X = jobs_df.loc[:, ['job_cat', 'location', 'initial_response']]
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
        palette=init_pal_list,
        ax=ax
    )

    ax.set_title('Job Category, Location, & Initial Response')
    ax.set_xlabel('Category')
    ax.set_ylabel('Location')
    # ax.get_legend().remove()

    return plt.show(fig)


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
