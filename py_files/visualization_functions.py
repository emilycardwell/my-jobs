''' IMPORTS '''
import pandas as pd
import numpy as np
from IPython.display import display

import matplotlib.dates as mpld
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import squarify
from matplotlib.colors import ListedColormap as lc
from matplotlib.colors import LinearSegmentedColormap as lscm
import seaborn as sns
from matplotlib.ticker import MaxNLocator
sns.set_theme(style='white')

from py_files.data_functions import read_df
from py_files.get_df_functions import get_slim_cats, get_init_responses, \
                                        get_responses, get_encoded_cols, \
                                        get_timeline_df, get_outcomes, \
                                        get_prep_df, get_work_df, \
                                        get_work_col, get_ohe_df


''' GLOBAL VARIABLES'''
cat_pal = sns.color_palette('viridis', 10, desat=.75)
init_pal_list = ['maroon', 'silver', cat_pal[7]]
outcomes_pal = ['maroon', 'silver', cat_pal[3], cat_pal[9], #'gold'
                ]
hue_order = ['Rejection', 'No Response', 'No Offer',
             'In Interviews', #'Offer'
             ]

''' CHECK DFS FOR CONTENT'''
def check_dfs(file_names):
    for file in file_names:
        df = read_df(file)
        if df.empty:
            print(f"{file} dataframe is empty, try adding some {file} data")
            return False

'''
SINGLE GRAPHS
'''
def show_job_categories():
    if check_dfs(['jobs']) == False:
        return "No data to show"

    cat_slim_ser = get_slim_cats()

    fig, ax = plt.subplots(figsize=(15,5))
    fig = sns.countplot(x=cat_slim_ser, palette='magma')

    ax.set_title('Job Category Counts')
    ax.set_xlabel('Category')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(top=20)
    plt.xticks(rotation=20)

    return plt.show(fig)


def show_initial_responses():
    if check_dfs(['jobs']) == False:
        return "No data to show"

    r_df= get_ohe_df()

    r_fig, ax = plt.subplots(figsize=(15,5))
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

    ax.xaxis.set_major_locator(mpld.DayLocator(interval=3))
    plt.xticks(rotation='horizontal')

    return plt.show(r_fig)


def show_outcomes():
    if check_dfs(['jobs']) == False:
        return "No data to show"

    responses_df = get_responses()
    responses_df.index = \
        [str(pd.to_datetime(x).strftime('%b %-d')) for x in responses_df.index]

    o_fig, ax = plt.subplots(figsize=(15,5))

    cmap = lc(outcomes_pal)

    o_fig = responses_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Applied',
        title='Final Outcomes by Date',
        ax=ax,
        width=.9
    )

    ax.xaxis.set_major_locator(mpld.DayLocator(interval=3))
    plt.xticks(rotation='horizontal')

    return plt.show(o_fig)

def show_practice():
    if check_dfs(['prep']) == False:
        return "No data to show"

    prep_df = get_prep_df()

    fig, ax = plt.subplots(figsize=(15,5))

    colors = ['wheat', '#eba9ae', 'thistle']
    nodes = [0.0, 0.5, 1.0]
    cmap = lscm.from_list("mycmap", list(zip(nodes, colors)))

    fig = prep_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Completed',
        title='Coding Practice Problems',
        ax=ax,
        width=1
    )

    ax.xaxis.set_major_locator(mpld.DayLocator(interval=3))
    plt.xticks(rotation='horizontal')

    return plt.show(fig)

def show_work():
    if check_dfs(['work']) == False:
        return "No data to show"

    work_df = get_work_df()

    fig, ax = plt.subplots(figsize=(15,5))

    colors = ["#cff075", "#88d1aa", "#78d2de", "#b9b7ed"]
    nodes = [0.0, 0.33, 0.66, 1.0]
    cmap = lscm.from_list("mycmap", list(zip(nodes, colors)))

    fig = work_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Completed',
        title='Coding Practice Problems',
        ax=ax,
        width=1
    )

    ax.xaxis.set_major_locator(mpld.DayLocator(interval=5))
    ax.set_ylim(top=5)

    plt.xticks(rotation='horizontal')

    return plt.show(fig)

def show_work_categories():
    if check_dfs(['work']) == False:
        return "No data to show"

    work_df = get_work_col('category')
    fig, ax = plt.subplots(figsize=(10,5))
    fig = sns.countplot(x=work_df, palette='Blues')
    ax.set_title('Work Category Counts')
    ax.set_xlabel('Category')
    plt.xticks(rotation='horizontal')

    return plt.show(fig)

def show_work_projects():
    if check_dfs(['work']) == False:
        return "No data to show"

    work_df = get_work_col('job')
    fig, ax = plt.subplots(figsize=(15,5))
    fig = sns.countplot(x=work_df, palette='Greens')
    ax.set_title('Work Projects')
    ax.set_xlabel('Project')
    plt.xticks(rotation=20)

    return plt.show(fig)


'''
MULTIPLOTS
'''
# timeline
def show_timeline():
    if check_dfs(['jobs', 'prep', 'work']) == False:
        return "No data to show"

    tl_df = get_timeline_df()
    feats = tl_df.reset_index(drop=True)
    x = list(tl_df.index)

    cols = hue_order.copy()
    cols.append('Coding Practice')
    cols.append('Work')

    timeline_pal = outcomes_pal.copy()
    timeline_pal.append('thistle')
    timeline_pal.append("lightsteelblue")

    fig, ax = plt.subplots(figsize=(20,5))

    t_accum = [0] * len(feats)

    for col, color in zip(cols, timeline_pal):
        ax.bar(
            x=pd.to_datetime(x),
            height=feats[col],
            bottom=t_accum,
            width=1,
            label=col,
            color=color
        )
        t_accum += feats[col]

    xform = mpld.DateFormatter('%b %-d')
    ax.xaxis.set_major_formatter(xform)
    ax.xaxis.set_major_locator(mpld.DayLocator(bymonthday=[1,15]))
    ax.set_xlabel('Date Applied or Practice Problem Completed')

    ax.set_ylim(top=10.5)
    ax.set_ylabel('')
    ax.set_title('Timeline of Job Applications and Coding Practice')
    ax.legend(loc='upper right')

    return plt.show(fig)


def show_cats():
    if check_dfs(['jobs']) == False:
        return "No data to show"

    cat_ser = get_slim_cats()
    out_df = get_init_responses()
    X = out_df.join(cat_ser) #.drop(columns="date_applied")

    # set figure
    sns.set_style("whitegrid", {})
    fig, ax = plt.subplots(figsize=(7,15))

    # category plot (by initial response)
    sns.countplot(
        data=X.sort_values('job_cat'),
        ax=ax,
        y="job_cat",
        hue="initial_response",
        order = cat_ser.value_counts().index,
        palette=init_pal_list,
        width=.5,
        # saturation=1
    )

    ax.set_title('Job Type & Outcomes')
    ax.set_ylabel('')
    ax.legend(loc='best')

    return plt.show()

def tree():
    if check_dfs(['jobs']) == False:
        return "No data to show"

    fig = plt.figure(figsize=(15, 5))
    outcomes_df = get_outcomes()
    squarify.plot(
        sizes=outcomes_df['final_outcome'].value_counts(),
        color=outcomes_pal, label=hue_order
        )
    plt.title("Outcomes")
    plt.axis("off")

    return plt.show()

def show_cat_compare():
    if check_dfs(['jobs']) == False:
        return "No data to show"

    df = get_encoded_cols()

    columns = ['department', 'recruiter', 'referral',
               'method', 'location']
    subs = ['a', 'b', 'c', 'd', 'e']

    # set figure
    sns.set_style("whitegrid")
    fig = plt.figure(constrained_layout=True, figsize=(10,10))
    mosaic = """
            abc
            ddd
            eee
            """
    ax_dict = fig.subplot_mosaic(mosaic)

    for col, sub in zip(columns, subs):
        if col == 'final_outcome':
            squarify.plot(
                # df[col].value_counts()
                sizes=[30,20,10,5], color=outcomes_pal,
                label=hue_order, ax=ax_dict[sub], pad=True
                )
            ax_dict[sub].set_title("outcome")
            ax_dict[sub].tick_params(axis='both', which='both', labelleft=False,
                                     labelbottom=False)
        else:
            sns.countplot(
            data=df, x=col, hue='final_outcome', hue_order=hue_order,
            palette=outcomes_pal, ax=ax_dict[sub]
            )
            ax_dict[sub].set_title(col)
        ax_dict[sub].set_xlabel("")
        ax_dict[sub].set_ylim(top=40)
        ax_dict[sub].grid(False,'major','both')
        if sub != 'a' and sub != 'd' and sub != 'e':
            ax_dict[sub].set_ylabel("")
            ax_dict[sub].tick_params(axis='y', which='both', labelleft=False)
        if sub != 'e':
            ax_dict[sub].get_legend().remove()

    return plt.show(fig)

def jobs_multiplot():
    if check_dfs(['jobs']) == False:
        return "No data to show"

    cat_slim_ser = get_slim_cats()
    r_df= get_ohe_df()
    responses_df = get_responses()
    responses_df.index = \
        [str(pd.to_datetime(x).strftime('%b %-d')) for x in responses_df.index]

    # set figure
    sns.set_style("whitegrid")
    fig = plt.figure(constrained_layout=True, figsize=(15,15))
    mosaic = """
            aaa
            bbb
            ccc
            """
    ax_dict = fig.subplot_mosaic(mosaic)

    # categories
    sns.countplot(ax=ax_dict['a'], x=cat_slim_ser, palette='magma')
    ax_dict['a'].set_title('Job Category Counts')
    ax_dict['a'].set_xlabel('Category')
    ax_dict['a'].yaxis.set_major_locator(MaxNLocator(integer=True))
    ax_dict['a'].set_ylim(top=20)
    ax_dict['a'].tick_params(labelrotation=20)
    ax_dict['a'].grid(False, 'both', 'both')

    # initial responses
    cmap = lc(init_pal_list)
    r_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Applied',
        title='Initial Responses by Date',
        ax=ax_dict['b'],
        width=.9
    )
    ax_dict['b'].xaxis.set_major_locator(mpld.DayLocator(interval=3))
    ax_dict['b'].tick_params(labelrotation=0)
    ax_dict['b'].grid(False, 'both', 'both')

    # outcomes
    cmap = lc([cat_pal[8], cat_pal[0], cat_pal[3], 'maroon', 'silver'])
    responses_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Applied',
        title='Final Outcomes by Date',
        ax=ax_dict['c'],
        width=.9
    )
    ax_dict['c'].xaxis.set_major_locator(mpld.DayLocator(interval=3))
    ax_dict['c'].tick_params(labelrotation=0)
    ax_dict['c'].grid(False, 'both', 'both')

    return plt.show()

def work_prep_multiplot():
    if check_dfs(['prep', 'work']) == False:
        return "No data to show"

    prep_df = get_prep_df()
    work_df = get_work_df()
    cat_df = get_work_col('category')
    proj_df = get_work_col('job')

    # set figure
    sns.set_style("whitegrid")
    fig = plt.figure(constrained_layout=True, figsize=(25,10))
    mosaic = """
            aac
            bbd
            """
    ax_dict = fig.subplot_mosaic(mosaic)

    # prep
    colors = ['wheat', '#eba9ae', 'thistle']
    nodes = [0.0, 0.5, 1.0]
    cmap = lscm.from_list("mycmap", list(zip(nodes, colors)))
    prep_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Completed',
        title='Coding Practice Problems',
        ax=ax_dict['a'],
        width=1
    )
    ax_dict['a'].xaxis.set_major_locator(mpld.DayLocator(interval=3))
    ax_dict['a'].tick_params(labelrotation=0)
    ax_dict['a'].grid(False, 'both', 'x')

    # work
    colors = ["#cff075", "#88d1aa", "#78d2de", "#b9b7ed"]
    nodes = [0.0, 0.33, 0.66, 1.0]
    cmap = lscm.from_list("mycmap", list(zip(nodes, colors)))
    work_df.plot(
        kind='bar',
        colormap=cmap,
        stacked=True,
        xlabel='Date Completed',
        title='Coding Practice Problems',
        ax=ax_dict['b'],
        width=1
    )

    ax_dict['b'].xaxis.set_major_locator(mpld.DayLocator(interval=5))
    ax_dict['b'].set_ylim(top=5)
    ax_dict['b'].tick_params(labelrotation=0)
    ax_dict['b'].grid(False, 'both', 'x')

    # work cats
    sns.countplot(x=cat_df, palette='Blues', ax=ax_dict['c'])
    ax_dict['c'].set_title('Work Category Counts')
    ax_dict['c'].set_xlabel('Category')
    ax_dict['c'].tick_params(labelrotation=0, labelsize=8)

    # work projects
    fig = sns.countplot(x=proj_df, palette='Greens', ax=ax_dict['d'])
    ax_dict['d'].set_title('Work Projects')
    ax_dict['d'].set_xlabel('Project')
    ax_dict['d'].tick_params(labelrotation=20, labelsize=8)



    return plt.show()


'''
DATA EXPLORATION
'''
def show_cat_ref():
    if check_dfs(['jobs']) == False:
        return "No data to show"

    jobs_df = read_df("jobs")
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
    if check_dfs(['jobs']) == False:
        return "No data to show"

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


if __name__ == '__main__':
    dec = input('would you like to print the visualizations? (y/n)')
    if dec == 'y':
        work_prep_multiplot()
