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
def read_df(file_name='job_data'):
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

def add_to_json(new_df, company_name, file_name='job_data'):

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

    # verify overwrite older file
    display(new_json_df.loc[new_json_df['company_name'] == company_name])
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
def get_app_info(pattern, file_name='job_data'):
    jobs_df = read_df(file_name)
    l = pattern.lower()
    u = pattern.upper()
    c = pattern.capitalize()
    app_df = jobs_df.loc[jobs_df['company_name'].str.contains(f'{l}|{u}|{c}')]
    return app_df

def add_rows(data, cols, file_name='job_data', on='company_name'):
    rows = pd.DataFrame([data], columns=cols)

    old_df = read_df(file_name)
    full_df = pd.concat([old_df, rows])
    sorted_df = full_df.sort_values(on).reset_index(drop=True)

    return sorted_df

def check_reg(a_index):
    l = len(list(a_index))
    if l == 0:
        print("Error with company name: returned 0 rows")
        return 0
    elif l > 1:
         print(f"Error with company name: returned {l} rows")
         print(a_index)
         return 0
    else:
        return 1

def update_add(app, cols, data, file_name='job_data'):
    company_name = app['company_name'].values[0]

    for i, c in enumerate(cols):
        app.loc[:, c] = data[i]

    old_jobs_df = read_df(file_name)
    old_jobs_df.loc[old_jobs_df['company_name'] == company_name] = app
    new_jobs_df = add_to_json(old_jobs_df, company_name)

    return old_jobs_df.compare(new_jobs_df)


'''
WRITING DATA
'''
# ADD APP
def add_app(company_name: str, date_applied: str, job_title: str,
            job_cat: str, department: str, location: str, recruiter: str,
            referral: str, method: str, url: str):

    app_columns = [
        'company_name', 'date_applied', 'job_title',
        'job_cat', 'department', 'location', 'recruiter',
        'referral', 'method', 'url', 'initial_response'
    ]

    data = [
        company_name, date_applied, job_title, job_cat,
        department, location, recruiter, referral, method, url, 'No Response'
    ]

    new_jobs_df = add_rows(data, app_columns, 'job_data', 'company_name')
    jobs_json_df = add_to_json(new_jobs_df, company_name)

    return jobs_json_df.info(verbose=False)

# ADD INITIAL RESPONSE
def add_init_response(company_name_like,
                      initial_response, date_init_resp,
                      date_interview1=None, interviewers=None,
                      file_name='job_data'):

    app = get_app_info(company_name_like)
    cr = check_reg(app.index)
    if cr == 0:
        return

    if initial_response == 'Rejected':
        cols = ['initial_response', 'date_init_resp']
        data = [initial_response, date_init_resp]

    elif initial_response == 'Passed':
        cols = ['initial_response', 'date_init_resp',
                'date_interview1', 'interviewers']
        data = [initial_response, date_init_resp,
                date_interview1, interviewers]
    else:
        return "Error, invalid initial response (Passed/Rejected)"

    return update_add(app, cols, data, file_name)

# ADD INTERVIEW INFO
def add_interview_info(company_name_like, interview_notes, next_steps,
                      file_name='job_data'):

    app = get_app_info(company_name_like, file_name)
    cr = check_reg(app.index)
    if cr == 0:
        return

    cols = ['interview_notes', 'next_steps']
    data = [interview_notes, next_steps]

    return update_add(app, cols, data, file_name)

# ADD MORE INTERVIEW NOTES/DATES
def add_more_ints(company_name_like, next_interviews,
                      file_name='job_data'):

    app = get_app_info(company_name_like, file_name)
    cr = check_reg(app.index)
    if cr == 0:
        return
    return update_add(app, ['next_interviews'], [next_interviews], file_name)

# ADD FINAL RESPONSE
def add_final_response(company_name_like, final_outcome, feedback,
                      file_name='job_data'):

    app = get_app_info(company_name_like, file_name)
    cr = check_reg(app.index)
    if cr == 0:
        return

    cols = ['final_outcome', 'feedback']
    data = [final_outcome, feedback]

    return update_add(app, cols, data, file_name)

# ADD PREP DATA
def add_prep(new_data, date=today, file_name='job_data'):

    prep_cols = ['site', 'submissions']

    for r in new_data:
        r.append(date)

    prep_df = add_rows(new_data, prep_cols, "prep", 'date_completed')
    new_df = add_to_json(prep_df, file_name="prep")

    return new_df.info(verbose=False)
