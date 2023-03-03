''' IMPORTS '''
import pandas as pd
import json
import os
from datetime import date
import glob


''' GLOBAL VARIABLES'''
data_path = os.getenv('DATA_PATH')
index_cols = ['company_name', 'date_applied']

def get_file_ver(file='job_data*'):
    current_files = glob.glob(data_path + file)
    latest_file = max(current_files, key=os.path.getctime)
    fname = os.path.basename(latest_file)
    return fname


'''
READING & WRITING TO JSON
'''
def read_df(file_name=None):
    if file_name == None:
        file_name = get_file_ver()
    file_path = data_path + file_name
    jobs_df = pd.read_json(file_path, orient='table')
    return jobs_df

def add_to_json(new_jobs_df, show=None):

    fname = 'job_data' + date.today().strftime('%d_%m') + '.json'
    filename = data_path + fname

    result = new_jobs_df.to_json(orient='table')
    parsed = json.loads(result)

    with open(filename, "w") as jsonFile:
        json.dump(parsed, jsonFile, indent=4)
        print(f'new data added sucessfully to {filename}')

    jobs_df = pd.read_json(filename, orient='table')

    if show:
        return jobs_df.head(show)
    else:
        return jobs_df


'''
UTILS
'''
def get_app_info(pattern):
    jobs_df = read_df()
    l = pattern.lower()
    u = pattern.upper()
    c = pattern.capitalize()
    app_df = jobs_df.loc[jobs_df['company_name'].str.contains(f'{l}|{u}|{c}')]
    return app_df

def make_df(cols, data):
    ser = pd.DataFrame(data, index=cols)
    df = ser.T.sort_values('company_name')
    return df

def concat_dfs(new_df):

    old_jobs_df = read_df()
    new_jobs_df = pd.concat([old_jobs_df, new_df])

    return new_jobs_df.sort_values('company_name').reset_index(drop=True)

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

def update_add(app, cols, data):
    company_name = app['company_name'].values[0]

    for i, c in enumerate(cols):
        app.loc[:, c] = data[i]

    old_jobs_df = read_df()
    old_jobs_df.loc[old_jobs_df['company_name'] == company_name] = app
    new_jobs_df = add_to_json(old_jobs_df)

    return new_jobs_df.loc[new_jobs_df['company_name'] == company_name]


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

    app_df = make_df(app_columns, data)
    jobs_df = concat_dfs(app_df)
    new_jobs_df = add_to_json(jobs_df)

    return new_jobs_df.loc[new_jobs_df['company_name'] == company_name]

# ADD INITIAL RESPONSE
def add_init_response(company_name_like,
                      initial_response, date_init_resp,
                      date_interview1=None, interviewers=None):

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

    return update_add(app, cols, data)

# ADD INTERVIEW INFO
def add_interview_info(company_name_like, interview_notes, next_steps):
    app = get_app_info(company_name_like)
    cr = check_reg(app.index)
    if cr == 0:
        return

    cols = ['interview_notes', 'next_steps']
    data = [interview_notes, next_steps]

    return update_add(app, cols, data)

# ADD MORE INTERVIEW NOTES/DATES
def add_more_ints(company_name_like, next_interviews):
    app = get_app_info(company_name_like)
    cr = check_reg(app.index)
    if cr == 0:
        return
    return update_add(app, ['next_interviews'], [next_interviews])

# ADD FINAL RESPONSE
def add_final_response(company_name_like, final_outcome, feedback):
    app = get_app_info(company_name_like)
    cr = check_reg(app.index)
    if cr == 0:
        return

    cols = ['final_outcome', 'feedback']
    data = [final_outcome, feedback]

    return update_add(app, cols, data)
