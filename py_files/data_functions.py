''' IMPORTS '''
import pandas as pd
import json
import os


''' GLOBAL VARIABLES'''
index_cols = ['company_name', 'date_applied']
data_path = os.getenv('DATA_PATH')


'''
WRITING DATA
'''

def read_df(file_name='/job_data.json'):
    file_path = data_path + file_name
    jobs_df = pd.read_json(file_path, orient='table')
    return jobs_df


def make_df(cols, data):
    ser = pd.DataFrame(data, index=cols)
    df = ser.T.set_index(index_cols).sort_index()
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

    return make_df(app_columns, company_app)


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


'''
CONCATTING DFS
'''

def concat_dfs(old_jobs_df, df_list):

    for x in range(len(df_list)):
        new_jobs_df = pd.concat([old_jobs_df, df_list[x]]).sort_index()

    return new_jobs_df

'''
READING & WRITING TO JSON
'''

# JOIN MULTIPLE ADDED DFS
def add_to_json(new_jobs_df, show='all'):

    filename = "job_data.json"
    result = new_jobs_df.to_json(orient='table')
    parsed = json.loads(result)

    with open(filename, "w") as jsonFile:
        json.dump(parsed, jsonFile, indent=4)
        print(f'new data added sucessfully to {filename}')

    jobs_df = pd.read_json('job_data.json', orient='table')

    if show == 'all':
        return jobs_df
    else:
        return jobs_df.head(show)
