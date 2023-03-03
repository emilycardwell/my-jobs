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
CONCATTING DFS
'''
def concat_dfs(new_df):

    old_jobs_df = read_df()
    new_jobs_df = pd.concat([old_jobs_df, new_df])

    return new_jobs_df.sort_values('company_name').reset_index(drop=True)


'''
WRITING DATA
'''
def make_df(cols, data):
    ser = pd.DataFrame(data, index=cols)
    df = ser.T.sort_values('company_name')
    return df

# ADD APP
def add_app(company_name: str, date_applied: str, job_title: str,
            job_cat: str, department: str, location: str, recruiter: str,
            referral: str, method: str, url: str):

    app_columns = [
        'company_name', 'date_applied', 'job_title',
        'job_cat', 'department', 'location', 'recruiter',
        'referral', 'method', 'url', 'initial_response'
    ]

    company_app = [
        company_name, date_applied, job_title, job_cat,
        department, location, recruiter, referral, method, url, 'No Response'
    ]

    app_df = make_df(app_columns, company_app)

    jobs_df = concat_dfs(app_df)

    new_jobs_df = add_to_json(jobs_df)

    return new_jobs_df.loc[new_jobs_df['company_name'] == company_name]

# ADD INITIAL RESPONSE
def add_init_response(company_name, date_applied,
                      initial_response, date_init_resp,
                      date_interview1=None, interviewers=None):

    if initial_response == 'Rejected':
        cols = index_cols + ['initial_response', 'date_init_resp']
        data = [company_name, date_applied, initial_response, date_init_resp]

    elif initial_response == 'Passed':
        cols = index_cols + ['initial_response', 'date_init_resp',
                            'date_interview1', 'interviewers']
        data = [company_name, date_applied, initial_response,
                date_init_resp, date_interview1, interviewers]

    else:
        return "Error, invalid initial_response"

    return make_df(cols, data)

# ADD INTERVIEW INFO
def add_interview_info(company_name, date_applied, interview_notes, next_steps):
    cols = index_cols + ['interview_notes', 'next_steps']
    data = [company_name, date_applied, interview_notes, next_steps]
    return make_df(cols, data)

# ADD MORE INTERVIEW NOTES/DATES
def add_more_ints(company_name, date_applied, next_interviews):
    cols = index_cols + ['next_interviews']
    data = company_name, date_applied, next_interviews
    return make_df(cols, data)

# ADD FINAL RESPONSE
def add_final_response(company_name, date_applied, final_outcome, feedback):
    cols = index_cols + ['final_outcome', 'feedback']
    data = company_name, date_applied, final_outcome, feedback
    return make_df(cols, data)
