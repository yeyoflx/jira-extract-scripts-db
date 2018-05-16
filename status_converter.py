import MySQLdb
from jira.client import JIRA
import datetime
from datetime import date
import time

def check_statuses(jira,project):

    final_dict ={}
    #Used to search for specfici JIRA issues based on issue type
    issues1 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=0,   maxResults=100)
    issues2 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=100, maxResults=500)
    #issues3 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=200, maxResults=500)

    list_of_searches = [issues1,issues2]
    list_of_statuses = ["Recording", "Verification Phase", "Redirected", "Rejected", "On Hold",
                        "Solution Concept Phase - Open", "Merged", "Solution Concept Phase - In Creation",
                        "Solution Concept Phase - Internal Review", "Solution Concept Phase - Technical Review",
                        "Sign-Off Phase", "Product Backlog", "TO DO", "IN PROGRESS", "Review", "DEV Review", "Done",
                        "Issue Owner Review","Ready to Deploy","Functional Acceptance Test","Production","Delivered","Retired"]
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
                            if item.fromString == "Recording":
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
                            cleaned_dict[k] = [date1, date2, difference]
                    else:
                        pass
                if str(issue2) not in final_dict:
                    final_dict[str(issue2)] = cleaned_dict
    return final_dict

def create_new_statuses(statuses):
    result = {}
    new_statuses = {"User Story Definition": ["Recording", "Verification Phase"],
                        "Solution Concept Creation": ["Solution Concept Phase - In Creation",
                                                      "Solution Concept Phase - Internal Review",
                                                      "Solution Concept Phase - Technical Review",
                                                      "Sign-Off Phase"],
                        "Development": ["TO DO", "IN PROGRESS", "Review","DEV Review", "Done"],
                        "DevOps": ["Ready to Deploy","Functional Acceptance Test", "Production"]
                        }
    user_story_start, user_story_end = None, None
    solution_concept_start, solution_concept_end = None, None
    development_start, development_end = None, None
    devops_start, devops_end = None, None
    for k1,v1 in statuses.items():
        print(k1,v1)
        for k, v in new_statuses.items():
            counter = -1
            if k == "User Story Definition":
                user_story_start = v1[v[0]]
                user_story_start = user_story_start[0]
                user_story_end = v1[v[counter]]
            elif k == "Solution Concept Creation":
                solution_concept_start = v1[v[0]]
                if type(solution_concept_start) == list:
                    solution_concept_start = solution_concept_start[0]
                if solution_concept_start != None and user_story_end == None:
                    user_story_end = solution_concept_start
                solution_concept_end = v1[v[counter]]
            elif k == "Development":
                development_start = v1[v[0]]
                if type(development_start) == list:
                    development_start = development_start[0]
                if development_start != None and user_story_end == None and user_story_start != None:
                    user_story_end = development_start
                if development_start != None and solution_concept_end == None and solution_concept_start != None:
                    solution_concept_end = development_start
                development_end = v1[v[counter]]
            elif k == "DevOps":
                devops_start = v1[v[0]]
                if type(devops_start) == list:
                    devops_start = devops_start[0]
                if devops_end != None and user_story_end == None and user_story_start != None:
                    user_story_end = devops_start
                if devops_end != None and solution_concept_end == None and solution_concept_start != None:
                    solution_concept_end = devops_start
                if devops_end != None and development_end == None and development_start != None:
                    development_end = devops_start
                devops_end = v1[v[counter]]
        status_dates = {"User Story Definition": (user_story_start, user_story_end),
                        "Solution Concept Creation": (solution_concept_start, solution_concept_end),
                        "Development": (development_start, development_end),
                        "DevOps": (devops_start, devops_end)
                        }
        for k2,v2 in  new_statuses.items():
            start = status_dates[k2][0]
            end = status_dates[k2][1]
            if type(end) == list:
                end = end[1]
            if start == None or end == None:
                print(k2,start,end,0)
                if k1 not in result.keys():
                    result[k1] = [start,end,0]
                else:
                    result[k1].extend([start,end,0])
            else:
                difference = (end-start).days
                print(k2,start,end,difference)
                if k1 not in result.keys():
                    result[k1] = [start,end,difference]
                else:
                    result[k1].extend([start,end,difference])
            # while v1[v[counter]] == None:
            #     counter -= 1
            #     if abs(counter) > len(v):
            #         counter += 1
            #         break
            # #(k,"|",v1[v[0]],"|",v1[v[counter]])
            #start_date = v1[v[0]]
            #end_date = v1[v[counter]]
            # if end_date != None and end_date[1] == None:
            #     print(print(k, "|", start_date[0], "|", end_date[1]),v[counter])
            # elif start_date and end_date != None:
            #     print(k,"|",start_date[0],"|",end_date[1],v[counter])
            # elif start_date != None and end_date == None:
            #     print(k, "|",start_date[0], "|", end_date,v[counter])
            # else:
            #     print(k, "|", start_date, "|", end_date,v[counter])
        print()
    return result
def execute_sql(sql):
    # Open database connection
    db = MySQLdb.connect("jira-project.clnssjscsqc7.us-east-2.rds.amazonaws.com", "schenker01","goSchenker01!", "jira_status_tracking")

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

def create_sql_jira(statuses,list_of_statuses):
    for k,v in statuses.items():
        print(k,v)
        stored_values = []
        stored_values.append(k)
        stored_values.extend(v)
        print(len(stored_values))
        counter = 1
        sql_string = """ INSERT INTO EFW_STATUSES_2 (Issue,"""
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
    projects = ["EFW"]
    list_of_statuses = ["UserStoryDefinition","SolutionConceptCreation","Development","DevOps"]
    delete_table_sql = """DELETE FROM EFW_STATUSES_2;"""
    execute_sql(delete_table_sql)
    statuses = check_statuses(jira, projects[0])
    new_statuses = create_new_statuses(statuses)

    create_sql_jira(new_statuses,list_of_statuses)

    print(time.time() - start_time, 'seconds it took to run')