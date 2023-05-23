''' IMPORTS '''
import pandas as pd
import json
import os
from datetime import date
from IPython.display import display


''' GLOBAL VARIABLES'''
data_path = os.getenv('DATA_PATH')
index_cols = ['company_name', 'date_applied']
today = date.today().strftime("%Y-%m-%d")


'''
READING & WRITING TO JSON
'''
def read_df(folder_name='jobs'):
    folder_path = f'{data_path}{folder_name}/'
    folder_contents = sorted(os.listdir(folder_path))
    file = folder_contents[-1]
    file_path = folder_path + file
    try:
        new_df = pd.read_json(file_path, orient='table', convert_dates=False)
    except FileNotFoundError:
        new_df = pd.DataFrame()

    return new_df

def verify_data(new_df, old_fpath):
    if os.path.exists(old_fpath):
        old_json_df = pd.read_json(old_fpath, orient="table")
        if len(old_json_df) > len(new_df):
            x = input("Rows have been deleted, continue anyway? (y/n): ")
            if x == 'y':
                return 0
            elif x == 'n':
                return -1
            else:
                print("Incorrect input value")
                return -1

        elif old_json_df.isna().sum().sum() < new_df.isna().sum().sum() \
            and len(old_json_df) == len(new_df):
            z = input("Values have been deleted, continue anyway? (y/n): ")
            if z == 'y':
                return 0
            elif z == 'n':
                return -1
            else:
                print("Incorrect input value")
                return -1
    else:
        return 1

def add_to_json(new_df, idx=None, comp_name=None, date_comp=None, folder_name='jobs'):

    # verify data
    folder_path = f'{data_path}{folder_name}/'
    file = os.listdir(folder_path)[-1]
    old_fpath = folder_path + file
    verify = verify_data(new_df, old_fpath)
    if verify == -1:
        return "Write to json stopped; values/rows deleted"
    if verify == 1:
        return "No older files found."

    # create filepath
    else:
        filepath = f'{folder_path}{file[:-6]}{int(file[-6])+1}.json'

    # verify file path
    print(f'The new file path is: {filepath}')
    path = input("Continue? (y/n): ")
    if path == 'n':
        return -1

    # load df to json
    result = new_df.to_json(orient='table')
    parsed = json.loads(result)

    # write to json
    with open(filepath, "w") as jsonFile:
        json.dump(parsed, jsonFile, indent=4)
        print(f'new data added sucessfully to {filepath}')

    # read from json
    new_json_df = pd.read_json(filepath, orient='table')

    # show new row
    if idx:
        display(new_json_df.loc[idx])
    if comp_name:
        display(new_json_df.loc[new_json_df['company_name'] == comp_name])
    elif date_comp == 'date_completed':
        display(new_json_df.loc[new_json_df['date_completed'] == date_comp])

    return new_json_df


'''
UTILS
'''
def get_app_info(pattern):
    jobs_df = read_df('jobs')
    l = pattern.lower()
    u = pattern.upper()
    c = pattern.capitalize()
    app_df = jobs_df.loc[jobs_df['company_name'].str.contains(f'{l}|{u}|{c}')]
    return app_df

def add_row(new_row, folder_name='jobs', on='company_name'):
    old_df = read_df(folder_name)
    full_df = pd.concat([old_df, new_row])
    sorted_df = full_df.sort_values(on).reset_index(drop=True)
    return sorted_df

def check_company_name(app_index):
    l = len(list(app_index))
    if l == 0:
        print("Error with company name: returned 0 rows")
        return -1
    elif l > 1:
        print(f"ATTENTION, company name returned {l} rows")
        df = read_df('jobs')
        display(df.iloc[app_index[0]:app_index[-1]+1])
        idx = int(input('which row (index no.) would you like to choose? (-1 for none)'))
        return idx
    else:
        return 1

def update_add(idx, app, cols, data):

    for i, c in enumerate(cols):
        app.loc[c] = data[i]

    old_jobs_df = read_df('jobs')
    old_jobs_df.loc[idx] = app
    new_jobs_df = add_to_json(old_jobs_df, idx=idx)

    return old_jobs_df.compare(new_jobs_df)


'''
WRITING DATA
'''
# ADD APP
def add_app(date_applied, company_name, job_title, job_cat, department,
            location, recruiter, referral, method, url):

    app_columns = [
        'date_applied', 'company_name', 'job_title',
        'job_cat', 'department', 'location', 'recruiter',
        'referral', 'method', 'url', 'initial_response', 'final_outcome'
    ]

    data = [
        date_applied, company_name, job_title, job_cat, department,
        location, recruiter, referral, method, url, 'No Response', 'No Response'
    ]

    new_row = pd.DataFrame([data], columns=app_columns)
    new_jobs_df = add_row(new_row)
    jobs_json_df = add_to_json(new_jobs_df, comp_name=company_name)

    return jobs_json_df.info(verbose=False)

# ADD INITIAL RESPONSE
def add_init_response(company_name_like,
                      date_init_resp, initial_response,
                      date_interview1=None, interview1_details=None):

    app = get_app_info(company_name_like)
    cr = check_company_name(app.index)
    if cr == -1:
        return
    elif cr != 1:
        row = app.loc[cr]
    else:
        row = app.loc[app.index[0]]

    idx = row.name

    if initial_response == 'Rejected':
        cols = ['date_init_resp', 'initial_response', 'final_outcome']
        data = [date_init_resp, initial_response, 'Immediate Rejection']

    elif initial_response == 'Passed':
        cols = ['date_init_resp', 'initial_response',
                'date_interview1', 'interviewers', 'final_outcome']
        data = [date_init_resp, initial_response,
                date_interview1, interview1_details, 'In Interviews']
    else:
        return "Error, invalid initial response (Passed/Rejected)"

    return update_add(idx, row, cols, data)


# ADD MORE INTERVIEW NOTES/DATES
def add_more_ints(company_name_like, int_no,
                  date_interview, interview_details):

    app = get_app_info(company_name_like)
    cr = check_company_name(app.index)
    if cr == -1:
        return
    elif cr != 1:
        row = app.loc[cr]
    else:
        row = app.loc[app.index[0]]

    idx = row.name
    cols = [f'date_interview{int_no}', f'interview{int_no}_details']
    data = [date_interview, interview_details]

    return update_add(idx, row, cols, data)

# ADD FINAL RESPONSE
def add_final_outcome(company_name_like, final_outcome, feedback):

    app = get_app_info(company_name_like)
    cr = check_company_name(app.index)
    if cr == -1:
        return
    elif cr != 1:
        row = app.loc[cr]
    else:
        row = app.loc[app.index[0]]

    while final_outcome not in ['Rejected Post-Interview', 'Offer']:
        final_outcome = input("Error, invalid final outcome. Enter valid response: \
             (Rejected Post-Interview/Offer)")

    idx = row.name
    cols = ['final_outcome', 'feedback']
    data = [final_outcome, feedback]

    return update_add(idx, row, cols, data)


# ADD PREP DATA
def add_prep(new_data, date=today):

    prep_cols = ['site', 'submissions']

    for r in new_data:
        r.append(date)

    new_row = pd.DataFrame([new_data], columns=prep_cols)
    prep_df = add_row(new_row, folder_name="prep", on='date')
    new_df = add_to_json(prep_df, date_comp=date, folder_name='prep')

    if new_df == -1:
        return f"Filepath Error."

    return new_df.info(verbose=False)


# ADD WORK DATA
def add_work(new_data, date=None):

    work_cols = ['job', 'category', 'date']
    data = new_data.copy()

    if date:
        data.append(date)
    else:
        data.append(today)

    new_row = pd.DataFrame([data], columns=work_cols)
    work_df = add_row(new_row, folder_name="work", on='date')
    new_df = add_to_json(work_df, date_comp=date, folder_name='work')

    if new_df == -1:
        return f"Filepath Error."

    return new_df.info(verbose=False)


# EDIT DF
def edit_df(column, new_info, company_name_like=None, idx=None, folder_name='jobs'):

    if company_name_like != None:
        app = get_app_info(company_name_like)
        cr = check_company_name(app.index)
        if cr == -1:
            return
        elif cr != 1:
            row = app.loc[cr]
        else:
            row = app.loc[app.index[0]]

        idx = row.name
        cols = [column]
        data = [new_info]

        return update_add(idx, row, cols, data)

    if idx != None:
        old_df = read_df(folder_name)
        old_df[column] = new_info
        new_df = add_to_json(old_df, idx=idx)

        return old_df.compare(new_df)
