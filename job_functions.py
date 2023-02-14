''' IMPORTS '''
import pandas as pd


''' ADDING DATA '''

index_cols = ['company_name', 'date_applied']

# APPS

def add_app(company_name, date_applied, job_title,
            job_cat, department, location, recruiter,
            referral, method, url):

    app_columns = [
        'company_name', 'date_applied', 'job_title', 'job_cat',
        'department', 'location', 'recruiter', 'referral', 'method', 'url'
    ]

    company_app = [
        company_name, date_applied, job_title, job_cat,
        department, location, recruiter, referral, method, url
    ]

    applications_df = pd.DataFrame(company_app, columns=app_columns)\
                                  .set_index(index_cols).sort_index()

    return applications_df

# RESPONSES


def add_response(company_name, date_applied,
                 initial_response, date_init_resp,
                 status='Immediate Rejection',
                 date_interview1=None, interviewers=None,
                 interview_notes=None, next_steps=None,
                 next_interviews=None, final_outcome=None, feedback=None):

    if status == 'Immediate Rejection':
        im_rejection(company_name, date_applied, initial_response, date_init_resp)

    elif status == 'Passed':
        first_pass(company_name, date_applied, initial_response,
                   date_init_resp, date_interview1, interviewers)


def im_rejection(company_name, date_applied, initial_response, date_init_resp):

    rejection_cols = ['initial_response', 'date_init_resp']

    company_rejection = [
        company_name, date_applied, initial_response, date_init_resp
    ]

    rej_cols = index_cols + rejection_cols
    immediate_rejections_df = pd.DataFrame(company_rejection, columns=rej_cols)\
                                          .set_index(index_cols).sort_index()

    return immediate_rejections_df


def first_pass(company_name, date_applied,
               initial_response, date_init_resp,
               date_interview1, interviewers):

    f_pass_cols = [
        'initial_response', 'date_init_resp',
        'date_interview1', 'interviewers'
    ]

    company_rejection = [
        company_name, date_applied, initial_response,
        date_init_resp, date_interview1, interviewers
    ]

    pass_cols = index_cols + f_pass_cols
    f_pass_df = pd.DataFrame(company_rejection, columns=pass_cols)\
                            .set_index(index_cols).sort_index()

    return f_pass_df




# SHOWING DATA


# SHOWING GRAPH
