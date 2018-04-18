import MySQLdb
from jira.client import JIRA
import datetime
from datetime import date
import time

def check_statuses(jira,project):

    final_dict ={}
    #Used to search for specfici JIRA issues based on issue type
    issues1 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=0,   maxResults=25)
    #issues2 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=100, maxResults=500)
    #issues3 = jira.search_issues('project = ' + project + ' AND issuetype = Story ORDER BY created DESC', startAt=200, maxResults=500)

    list_of_searches = [issues1]
    list_of_statuses = ["Recording", "Verification Phase", "Redirected", "Rejected", "On Hold",
                        "Solution Concept Phase - Open", "Merged", "Solution Concept Phase - In Creation",
                        "Solution Concept Phase - Internal Review", "Solution Concept Phase - Technical Review",
                        "Sign-Off Phase", "Product Backlog", "TO DO", "IN PROGRESS", "Review", "DEV Review", "Done",
                        "Issue Owner Review","Ready to Deploy","Functional Acceptance Test","Production","Delivered" "Retired"]
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
                            cleaned_dict[k] = [date1, date2, difference]
                    else:
                        pass
                if str(issue2) not in final_dict:
                    final_dict[str(issue2)] = cleaned_dict
    return final_dict

if __name__ == '__main__':
    start_time = time.time()
    # Used to connect to the Schenker JIRA Database using personal credentials
    options = {'server': 'https://schenkereservices.atlassian.net'}
    jira = JIRA(options, basic_auth=('Diego.Felix@DBSchenker.com', 'V0lkswagen00151637?'))
    print("Successfully connected to JIRA")

    projects = ["EFW"]

    statuses = check_statuses(jira, projects[0])

    new_statuses = {"User Story Definition": ["Recording", "Verification Phase"],
                    "Solution Concept Creation": ["Solution Concept Phase - In Creation",
                                                  "Solution Concept Phase - Internal Review",
                                                  "Solution Concept Phase - Technical Review",
                                                  "Sign-Off Phase"],
                    "Development": ["TO DO", "In Progress", "Review", "Done"],
                    "DevOps": ["Ready to Deploy","Functional Acceptance Test", "Production"]
                    }

    for k1,v1 in statuses.items():
        print(k1,v1)
        for k, v in new_statuses.items():
            counter = -1
            while v1[v[counter]] == None and abs(counter) <= len(v):
                print(len(v))
                print(v1[v[counter]])
                counter -= 1
                print(counter)
            print(k,"|",v1[v[0]], "|", v1[v[counter]])
        print()

