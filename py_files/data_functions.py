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
def read_df(file_name='jobs'):
    file_path = data_path + file_name + '.json'
    new_df = pd.read_json(file_path, orient='table')
    return new_df

def verifty_data(new_df, old_fpath):
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
        print("No older files found.")
        return 1

def add_to_json(new_df, idx=None, comp_name=None, date_comp=None, file_name='jobs'):

    # add final outcomes (if not present)
    outcomes_ser = get_outcomes(new_df).final_outcome.sort_index()
    new_df.loc[:, 'final_outcome'] = outcomes_ser

    # verify data
    old_fpath = data_path + file_name + '.json'
    verify = verifty_data(new_df, old_fpath)
    if verify == -1:
        return "Write to json stopped"

    # create filepath
    if verify == 1:
        fname = file_name + '.json'
    else:
        fname = file_name + '_new' + '.json'
    filepath = data_path + fname

    # verify file path
    if os.path.exists(filepath):
        return f"File Error. Please rename {filepath}."

    # load df to json
    result = new_df.to_json(orient='table')
    parsed = json.loads(result)

    # write to json
    with open(filepath, "w") as jsonFile:
        json.dump(parsed, jsonFile, indent=4)
        print(f'new data added sucessfully to {filepath}')

    # read from json
    new_json_df = pd.read_json(filepath, orient='table')

    # return if no older file exists
    if verify == 1:
        return new_json_df

    # show new row
    if idx:
        display(new_json_df.loc[idx])
    if comp_name:
        display(new_json_df.loc[new_json_df['company_name'] == comp_name])
    elif date_comp == 'date_completed':
        display(new_json_df.loc[new_json_df['date_completed'] == date_comp])

    # verify overwrite older file
    y = input("Would you like to overwrite the old file? (y/n): ")
    if y == 'y':
        os.rename(filepath, old_fpath)
        print('file renamed: ', old_fpath)
    else:
        new_fname = input("New file name: ")
        new_fpath = data_path + new_fname + '.json'
        os.rename(filepath, new_fpath)
        print('file renamed: ', new_fpath)

    return new_json_df


'''
UTILS
'''
def get_app_info(pattern, file_name='jobs'):
    jobs_df = read_df(file_name)
    l = pattern.lower()
    u = pattern.upper()
    c = pattern.capitalize()
    app_df = jobs_df.loc[jobs_df['company_name'].str.contains(f'{l}|{u}|{c}')]
    return app_df

def add_rows(data, cols, file_name='jobs', on='company_name'):
    rows = pd.DataFrame([data], columns=cols)

    old_df = read_df(file_name)
    full_df = pd.concat([old_df, rows])
    sorted_df = full_df.sort_values(on).reset_index(drop=True)

    return sorted_df

def check_reg(a_index):
    l = len(list(a_index))
    if l == 0:
        print("Error with company name: returned 0 rows")
        return -1
    elif l > 1:
        print(f"ATTENTION, company name returned {l} rows")
        for x in a_index:
            print(read_df().loc[x, ['date_applied', 'company_name', 'job_title']])
        idx = int(input('which row (name) would you like to choose? (-1 for none)'))
        return idx
    else:
        return 1

def update_add(idx, app, cols, data, file_name='jobs'):

    for i, c in enumerate(cols):
        app.loc[c] = data[i]

    old_jobs_df = read_df(file_name)
    old_jobs_df.loc[idx] = app
    new_jobs_df = add_to_json(old_jobs_df, idx=idx)

    return old_jobs_df.compare(new_jobs_df)

def get_outcomes(jobs_df=read_df()):

    slim_df = jobs_df.loc[:, ['date_applied', 'company_name', 'initial_response', 'final_outcome']]

    # sort by date
    outcomes_df = slim_df.sort_values('date_applied')

    # re-label final outcome by init and final responses
    for idx in outcomes_df.index:
        row = outcomes_df.loc[idx]
        if row.final_outcome != 'Offer':
            pass
        elif row.final_outcome == 'Rejected' and row.initial_response == "Passed":
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


'''
WRITING DATA
'''
# ADD APP
def add_app(date_applied, company_name, job_title, job_cat, department,
            location, recruiter, referral, method, url):

    app_columns = [
        'date_applied', 'company_name', 'job_title',
        'job_cat', 'department', 'location', 'recruiter',
        'referral', 'method', 'url', 'initial_response'
    ]

    data = [
        date_applied, company_name, job_title, job_cat, department,
        location, recruiter, referral, method, url, 'No Response'
    ]

    new_jobs_df = add_rows(data, app_columns)
    jobs_json_df = add_to_json(new_jobs_df, comp_name=company_name)

    return jobs_json_df.info(verbose=False)

# ADD INITIAL RESPONSE
def add_init_response(company_name_like,
                      date_init_resp, initial_response,
                      date_interview1=None, interview1_details=None,
                      file_name='jobs'):

    app = get_app_info(company_name_like, file_name)
    cr = check_reg(app.index)
    if cr == -1:
        return
    elif cr != 1:
        row = app.loc[cr]
    else:
        row = app.loc[app.index[0]]

    idx = row.name

    if initial_response == 'Rejected':
        cols = ['date_init_resp', 'initial_response']
        data = [date_init_resp, initial_response]

    elif initial_response == 'Passed':
        cols = ['date_init_resp', 'initial_response',
                'date_interview1', 'interviewers']
        data = [date_init_resp, initial_response,
                date_interview1, interview1_details]
    else:
        return "Error, invalid initial response (Passed/Rejected)"

    return update_add(idx, row, cols, data, file_name)


# ADD MORE INTERVIEW NOTES/DATES
def add_more_ints(company_name_like, int_no,
                  date_interview, interview_details,
                  file_name='jobs'):

    app = get_app_info(company_name_like, file_name)
    cr = check_reg(app.index)
    if cr == -1:
        return
    elif cr != 1:
        row = app.loc[cr]
    else:
        row = app.loc[app.index[0]]

    idx = row.name
    cols = [f'date_interview{int_no}', f'interview{int_no}_details']
    data = [date_interview, interview_details]

    return update_add(idx, row, cols, data, file_name)

# ADD FINAL RESPONSE
def add_final_response(company_name_like, final_outcome, feedback,
                      file_name='jobs'):

    app = get_app_info(company_name_like, file_name)
    cr = check_reg(app.index)
    if cr == -1:
        return
    elif cr != 1:
        row = app.loc[cr]
    else:
        row = app.loc[app.index[0]]

    idx = row.name
    cols = ['final_outcome', 'feedback']
    data = [final_outcome, feedback]

    return update_add(idx, row, cols, data, file_name)


# ADD PREP DATA
def add_prep(new_data, date=today):

    prep_cols = ['site', 'submissions']

    for r in new_data:
        r.append(date)

    prep_df = add_rows(new_data, prep_cols, "prep", 'date_completed')
    new_df = add_to_json(prep_df, date_comp='date_completed', file_name='prep')

    return new_df.info(verbose=False)
