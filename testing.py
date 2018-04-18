import MySQLdb

import jira.client
from jira.client import JIRA
import openpyxl
from openpyxl import Workbook
import datetime
from datetime import date
import time
import json


def check_statuses(jira,project):

    final_dict ={}
    #Used to search for specfici JIRA issues based on issue type
    issues1 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=0,   maxResults=100)
    #issues2 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=100, maxResults=500)
    #issues3 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=200, maxResults=500)

    list_of_searches = [issues1,
                        ]


    #list_of_statuses = ["Recording","Technical Assessment","Prioritization","Planning","Definition","Design","Ready for Development", "Development","Testing on DEV","Ready for Production","Closed"]
    list_of_statuses = ["Recording","Verification Phase","Redirected","Rejected","On Hold","Solution Concept Phase - Open","Merged","Solution Concept Phase - In Creation","Solution Concept Phase - Internal Review","Solution Concept Phase - Technical Review",
                        "Sign-Off Phase","Product Backlog","To Do","In Progress","Review","Dev Review","Done","Issue Owner Review","Retired"]
    # Stores the status and dates for each issue and all the statuses it has passed through
    for list_of_issues in list_of_searches:
        for issue2 in list_of_issues:
            if str(issue2) not in final_dict:
                dict_of_statuses = {}
                cleaned_dict = {}
                print(issue2)
                issue = jira.issue(str(issue2), expand='changelog')
                changelog = issue.changelog
                for history in changelog.histories[::-1]:
                    for item in history.items:
                        if item.field == "status":
                            #print("Date:" + history.created + " From: " + item.fromString + " To:" + item.toString)
                            if item.fromString == "Recording":
                                print(item.fromString)
                                dict_of_statuses[item.fromString] = [("First date:",issue2.fields.created)]
                            if item.fromString in dict_of_statuses:
                                dict_of_statuses[item.fromString].append(("Last date:",history.created))
                            if item.fromString not in dict_of_statuses:
                                dict_of_statuses[item.fromString] = [("First date:",history.created)]
                            if item.toString not in dict_of_statuses:
                                dict_of_statuses[item.toString] = [("First date:",history.created)]
                # Compares the issues statuses to all possible statuses to create a dictionary containing all statuses for one issue
                for status in list_of_statuses:
                    if status in dict_of_statuses:
                        cleaned_dict[status] = dict_of_statuses[status]
                    else:
                        if status == "Recording":
                            cleaned_dict[status] = [("First date:",issue2.fields.created)]
                        else:
                            cleaned_dict[status] = None

                for k,v in cleaned_dict.items():
                    if v != None:
                        a = len(v)
                        if len(v) == 1:
                            first = v[0][1][0:10].split("-")
                            date1 = date(int(first[0]), int(first[1]), int(first[2]))
                            #print(k,date1)
                            if k == "Recording":
                                difference = (datetime.date.today() - date1).days
                                cleaned_dict[k] = [date1,None,difference]
                            else:
                                cleaned_dict[k] = [date1,None,0]
                        else:
                            first = v[0][1][0:10].split("-")
                            second = v[1][1][0:10].split("-")
                            datetime.timedelta(7)
                            date1 = date(int(first[0]),int(first[1]),int(first[2]))
                            date2 = date(int(second[0]),int(second[1]),int(second[2]))
                            difference = (date2-date1).days
                            #print(k,date1 ,date2,difference)
                            cleaned_dict[k] = [date1, date2, difference]
                    else:
                        pass
                        #print("None")
                #print(cleaned_dict)
                if str(issue2) not in final_dict:
                    final_dict[str(issue2)] = cleaned_dict
    return final_dict


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

def create_sql_jira(statuses):
    for k,v in statuses.items():
        print(k,v)
        stored_values = []
        stored_values.append(k)
        for k1,v1 in v.items():
            if v1 == None:
                print(k1,[None,None,None])
                for i in range(3):
                    stored_values.append(None)
            else:
                print(k1,v1)
                for i in v1:
                    stored_values.append(i)
        counter = 1
        sql_string = """ INSERT INTO EFW_STATUSES (Issue,"""
        for status in list_of_statuses:
            start = status + "StartDate,"
            end = status + "EndDate,"
            total = status + "TotalDays,"
            sql_string += start + end + total
            counter += 3
        sql_string = sql_string[:-1]+") VALUES("
        print(counter)
        for i in range(counter):
            sql_string += "'{}',"
        sql_string = sql_string[:-1]+");"
        print(sql_string)
        print(len(stored_values))
        print(stored_values)
        sql_string = sql_string.format(*stored_values)
        execute_sql(sql_string)


if __name__ == '__main__':
    start_time = time.time()
    # Used to connect to the Schenker JIRA Database using personal credentials
    options = {'server': 'https://schenkereservices.atlassian.net'}
    jira = JIRA(options, basic_auth=('Diego.Felix@DBSchenker.com', 'V0lkswagen00151637?'))
    print("Successfully connected to JIRA")

    list_of_statuses = ["Recording", "VerificationPhase", "Redirected", "Rejected", "OnHold",
                        "SolutionConceptPhase_Open", "Merged", "SolutionConceptPhase_InCreation",
                        "SolutionConceptPhase_InternalReview", "SolutionConceptPhase_TechnicalReview",
                        "Sign_OffPhase", "ProductBacklog", "ToDo", "InProgress", "Review", "DevReview", "Done",
                        "IssueOwnerReview", "Retired"]
    # sql_string = """ CREATE TABLE EFW_STATUSES (Issue varchar(255),"""
    # for status in list_of_statuses:
    #     start = status + "StartDate date,"
    #     end = status + "EndDate date,"
    #     total = status + "TotalDays int,"
    #     sql_string += start + end + total
    #
    # sql_table = sql_string[:-1] + ");"
    # print(sql_table)
    # execute_sql(sql_table)

    projects = ["EFW"]

    statuses = check_statuses(jira,projects[0])
    create_sql_jira(statuses)




