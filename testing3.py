import MySQLdb
import jira.client
from jira.client import JIRA
import time


def check_statuses(jira,project):
    final_dict ={}
    #Used to search for specfici JIRA issues based on issue type
    issues1 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=0,   maxResults=100)
    issues2 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=100,   maxResults=100)

    list_of_issues = [issues2]
    for issues in list_of_issues:
        for issue in issues:
            print(issue)
            sql_string = """ UPDATE EFW_STATUSES_2 SET """
            print(issue.fields.priority)
            sql_string += "Priority = '" + str(issue.fields.priority) + "' WHERE Issue = '" + str(issue) + "';"
            print(sql_string)
            execute_sql(sql_string)
            # if issue.fields.customfield_11016 == None:
            #     print(None)
            # elif len(issue.fields.customfield_11016) > 1:
            #     for mode in issue.fields.customfield_11016:
            #         print(mode)
            #         sql_string += str(mode) + "= '"+str(mode)+"' WHERE " + "Issue = '" + str(issue) + "';"
            #         print(sql_string)
            #         execute_sql(sql_string)
            #         sql_string = """ UPDATE EFW_STATUSES_2 SET """
            # else:
            #     print(issue.fields.customfield_11016[0])
            #     sql_string += str(issue.fields.customfield_11016[0]) + " = '"+ str(issue.fields.customfield_11016[0]) +"' WHERE " + "Issue = '"+str(issue)+"';"
            #     print(sql_string)
            #     execute_sql(sql_string)
            print()

def execute_sql(sql):
    # Open database connection
    db = MySQLdb.connect("df-db.cvppgrc7bsks.us-west-2.rds.amazonaws.com", "yeyoflx", "V0lkswagen!", "JIRA")

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # execute SQL query using execute() method.
    cursor.execute("SELECT VERSION()")

    try:
        # execute SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        print("Successfully executed SQL statement")
    except:
        # Rollback in case there is any error
        print("Failed to execute SQL statement")
        db.rollback()
    # disconnect from server
    db.close()

if __name__ == '__main__':
    start_time = time.time()
    # Used to connect to the Schenker JIRA Database using personal credentials
    options = {'server': 'https://schenkereservices.atlassian.net'}
    jira = JIRA(options, basic_auth=('Diego.Felix@DBSchenker.com', 'V0lkswagen00151637?'))
    print("Successfully connected to JIRA")
    projects = ["EFW"]
    check_statuses(jira,projects[0])

    print(time.time() - start_time, 'seconds it took to run')