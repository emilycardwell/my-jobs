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
def read_df(folder_name, file=None):

    if file != None:
        file_path = f'{data_path}{folder_name}/{file}.json'
        try:
            new_df = pd.read_json(file_path, orient='table', convert_dates=False)
            return new_df
        except FileNotFoundError:
            return "FileNotFound Error"

    folder_path = f'{data_path}{folder_name}/'
    folder_contents = os.listdir(folder_path)

    versions = []
    for file in folder_contents:
        v = int(file[4:-5])
        versions.append(v)
    last_ver = sorted(versions)[-1]

    last_file = f'{file[:4]}{last_ver}.json'
    file_path = folder_path + last_file

    try:
        new_df = pd.read_json(file_path, orient='table', convert_dates=False)
        return new_df
    except FileNotFoundError:
        return "FileNotFound Error"



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

def add_to_json(new_df, folder_name, idx=None, comp_name=None, date_comp=None):

    # verify data
    folder_path = f'{data_path}{folder_name}/'
    folder_contents = os.listdir(folder_path)
    versions = []
    for file in folder_contents:
        v = int(file[4:-5])
        versions.append(v)
    last_ver = sorted(versions)[-1]

    last_file = f'{file[:4]}{last_ver}.json'
    old_fpath = folder_path + last_file

    verify = verify_data(new_df, old_fpath)
    if verify == -1:
        return "Write to json stopped; values/rows deleted"
    if verify == 1:
        return "No older files found."

    # verify file path
    print(f'The latest file is: {last_file}')
    cont = input("Continue? (y/n): ")
    if cont == 'y':
        pass
    else:
        return -1

    gen = input("Auto-generate a new file? (y/n): ")
    if gen == 'y':
        filepath = f'{folder_path}{last_file[:4]}{int(last_file[4:-5])+1}.json'
    elif gen == 'n':
        inp = input("Would you like to overwrite the last file? (y/n): ")
        if inp == 'y':
            filepath = old_fpath
        elif inp == 'n':
            new_file_name = input("Enter your new file name (ex: test): ")
            filepath = f'{folder_path}{new_file_name}.json'
        else:
            return -1
    else:
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
    app_df = jobs_df[jobs_df['company_name'].str.contains(f'{l}|{u}|{c}')]
    return app_df

def add_row(new_row, folder_name, on='company_name'):
    old_df = read_df(folder_name)
    full_df = pd.concat([old_df, new_row])
    sorted_df = full_df.sort_values(on).reset_index(drop=True)
    return sorted_df

def check_company_name(app_index):
    l = len(list(app_index))
    if l == 0:
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

    display(pd.DataFrame(app).T)

    old_jobs_df = read_df('jobs')
    old_jobs_df.loc[idx] = app
    new_jobs_df = add_to_json(old_jobs_df, "jobs", idx=idx)

    if type(new_jobs_df) == int:
        return "add_to_json was stopped due to user input"

    display(old_jobs_df.compare(new_jobs_df))

    return "Finished"


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
    display(new_row)

    new_jobs_df = add_row(new_row, 'jobs')
    jobs_json_df = add_to_json(new_jobs_df, "jobs", comp_name=company_name)

    if type(jobs_json_df) == int:
        return "add_to_json was stopped due to user input"

    return jobs_json_df.info(verbose=False)

# ADD INITIAL RESPONSE
def add_init_response(company_name_like,
                      date_init_resp, initial_response,
                      date_interview1=None, interview1_details=None):

    app = get_app_info(company_name_like)

    cr = check_company_name(app.index)
    if cr == -1:
        return "Error with company name: returned 0 rows"
    elif cr != 1:
        row = app.loc[cr]
    else:
        row = app.loc[app.index[0]]

    idx = row.name

    if initial_response == 'Rejection':
        cols = ['date_init_resp', 'initial_response', 'final_outcome']
        data = [date_init_resp, initial_response, 'Rejection']

    elif initial_response == 'Passed':
        cols = ['date_init_resp', 'initial_response',
                'date_interview1', 'interviewers', 'final_outcome']
        data = [date_init_resp, initial_response,
                date_interview1, interview1_details, 'In Interviews']
    else:
        return "Error, invalid initial response (Passed/Rejection)"

    new_row = update_add(idx, row, cols, data)

    return new_row


# ADD MORE INTERVIEW NOTES/DATES
def add_more_ints(company_name_like, int_no,
                  date_interview, interview_details):

    app = get_app_info(company_name_like)
    cr = check_company_name(app.index)
    if cr == -1:
        return "Error with company name: returned 0 rows"
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
        return "Error with company name: returned 0 rows"
    elif cr != 1:
        row = app.loc[cr]
    else:
        row = app.loc[app.index[0]]

    while final_outcome not in ['No Offer', 'Offer']:
        final_outcome = input("Error, invalid final outcome. Enter valid response: \
             (No Offer/Offer)")

    idx = row.name
    cols = ['final_outcome', 'feedback']
    data = [final_outcome, feedback]

    return update_add(idx, row, cols, data)


# ADD PREP DATA
def add_prep(new_data, date=today):

    prep_cols = ['site', 'submissions', 'date']

    for r in new_data:
        r.append(date)

    new_row = pd.DataFrame(new_data, columns=prep_cols)
    prep_df = add_row(new_row, "prep", on='date')
    new_df = add_to_json(prep_df, "prep", date_comp=date)

    if type(new_df) == int:
        return "add_to_json was stopped due to user input"

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
    work_df = add_row(new_row, "work", on='date')
    new_df = add_to_json(work_df, "work", date_comp=date)

    if type(new_df) == int:
        return "add_to_json was stopped due to user input"

    return new_df.info(verbose=False)


# EDIT DF
def edit_df(column, new_info, folder_name, rows_to_delete=None,
            company_name_like=None, idx=None, old_info=None):

    if company_name_like != None:
        app = get_app_info(company_name_like)
        cr = check_company_name(app.index)
        if cr == -1:
            return "Error with company name: returned 0 rows"
        elif cr != 1:
            row = app.loc[cr]
        else:
            row = app.loc[app.index[0]]

        print("The old data is: ", row)
        print("The new data is: ", new_info)

        idx = row.name
        cols = [column]
        data = [new_info]

        return update_add(idx, row, cols, data)

    if idx != None:
        old_df = read_df(folder_name)
        print("The old data is: ", old_df.loc[idx][column])
        old_df.loc[idx][column] = new_info
        print("The new data is: ", old_df.loc[idx][column])
        new_df = add_to_json(old_df, folder_name, idx=idx)

        if type(new_df) == int:
            return "add_to_json was stopped due to user input"

        display(old_df.compare(new_df))

        return "Finished!"

    if rows_to_delete != None:
        old_df = read_df(folder_name)

        start_idx = rows_to_delete[0]
        end_idx = rows_to_delete[-1] + 1

        display(old_df[start_idx:end_idx])
        conf = input('really delete rows: (y/n) ')
        if conf == 'y':
            old_df = old_df.drop(rows_to_delete).reset_index(drop=True)
            new_df = add_to_json(old_df, folder_name)
            display(old_df.compare(new_df))
            return "Finished!"

        return "Cancelled"

    if old_info != None:
        old_df = read_df(folder_name)
        old_col = old_df[column]
        print("The old data is: ", old_info, "and the new info is: ", new_info)

        for i, v in old_col.items():
            if old_info in v:
                old_col[i] = v.replace(old_info, new_info)

        old_df[column] = old_col
        new_df = add_to_json(old_df, folder_name)

        if type(new_df) == int:
            return "add_to_json was stopped due to user input"

        display(old_df.compare(new_df))

        return "Finished!"

    return "Error, one of the Keyword args must be given"


# VERIFY DATA FILES AND CONSOLIDATE
def verify_consolidate():

    folders = ['jobs', 'work', 'prep']

    for f in folders:
        old_df = read_df(folder_name=f, file=f'{f}1')
        new_df = read_df(f)
        old_path = f'{data_path}{f}/{f}1.json'

        verify = verify_data(new_df, old_path)
        if verify == -1:
            return "Write to json stopped; values/rows deleted"
        if verify == 1:
            return "No older files found."

        diff_df = pd.concat([old_df,new_df]).drop_duplicates(keep=False)
        print("data added:")
        display(diff_df)

    return
