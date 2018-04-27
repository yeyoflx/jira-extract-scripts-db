import MySQLdb

from jira.client import JIRA
import datetime
from datetime import date
import time

# Fetch a single row using fetchone() method.


def extract_from_jira(jira,project):
    #Used to search for specfici JIRA issues based on issue type
    issues1 = jira.search_issues('project = '+project+' AND issuetype = Story ORDER BY created DESC',startAt = 0  ,maxResults=100)
    issues2 = jira.search_issues('project = '+project+' AND issuetype = Story ORDER BY created DESC',startAt = 100,maxResults=500)
    issues3 = jira.search_issues('project = '+project+' AND issuetype = Story ORDER BY created DESC',startAt = 200,maxResults=500)

    list_of_searches = [issues1,issues2,issues3]
    dict_of_stories = {}
    # Accesses JIRA items changelog and locates changes in status as well as save the date of the changed status
    for list_of_issues in list_of_searches:
        for issue2 in list_of_issues:
            print(issue2)
            issue = jira.issue(str(issue2), expand = 'changelog')
            changelog = issue.changelog
            last_status = issue.fields.created[0:10].split("-")
            first_status = date(int(last_status[0]), int(last_status[1]), int(last_status[2]))
            date_created = date(int(last_status[0]), int(last_status[1]), int(last_status[2]))
            total_days = 0

            # used to determine Number of days from date user sotry was created to todays run date
            todays_date = date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
            datetime.timedelta(7)
            story_age = (todays_date - date_created).days

            #used to determine Date the user story 3was assigned the Current Workflow
            #Also used to determine Number of dats from date user story was assigned to the current to todays run date
            second_date = 0
            for history in changelog.histories[::-1]:
                for item in history.items:
                    if item.field == "status":
                        history_created = history.created[0:10].split("-")
                        second_date = date(int(history_created[0]), int(history_created[1]), int(history_created[2]))
                        datetime.timedelta(7)
                        total_days += (second_date - first_status).days
                        first = second_date
            if second_date == 0:
                second_date = date_created
                status_age = (todays_date - date_created).days
            else:
                status_age = (todays_date - second_date).days

            # Puts values from JIRA api and changelog into a dictionary containing all JIRA issues
            if project != "EFW":
                new_statuses = {"User Story Definition":["Recording","Verification Phase"],
                                "Solution Concept Creation":["Solution Concept Open","Solution Concept in Creation","Solution Concept Int. Review","Solution Concept Tec. Review","Solution Concept Sign-off"],
                                "Development":["Todo","In Progress","DEV Review""Review","Done"],
                                "DevOps":["Issue Owner Review","Ready to Deploy","FAT","PROD"]
                                }
                if str(issue2) not in dict_of_stories.keys():
                    dict_of_stories[str(issue)] = {"Summary":issue2.fields.summary,
                                                   "Priority":issue2.fields.priority.name,
                                                   "Reporter":issue2.fields.reporter.displayName,
                                                   "Date Created":str(date_created),
                                                   "Story Age": str(story_age),
                                                   "Assignee":issue2.fields.assignee.displayName,
                                                   "Current Status":issue2.fields.status.name,
                                                   "Status Date": str(second_date),
                                                   "Status Age": status_age
                                                   }
            else:
                new_statuses = {"User Story Definition": ["Recording", "Verification Phase"],
                                "Solution Concept Creation": ["Solution Concept Phase - Open", "Solution Concept Phase - In Creation",
                                                              "Solution Concept Phase - Internal Review",
                                                              "Solution Concept Phase - Technical Review",
                                                              "Sign-Off Phase"],
                                "Development": ["To Do", "In Progress","DEV Review","Review", "Done"],
                                "DevOps": ["Issue Owner Review", "Ready to Deploy", "Functional Acceptance Test", "Production", "Delivered"]
                                }
                status = issue2.fields.status.name

                for k, v in new_statuses.items():
                    if status in v:
                        status = k
                    else:
                        pass
                if str(issue2) not in dict_of_stories.keys():
                    dict_of_stories[str(issue)] = {"Summary":issue2.fields.summary,
                                                   "Priority":issue2.fields.priority.name,
                                                   "Reporter":issue2.fields.reporter.displayName,
                                                   "Date Created":str(date_created),
                                                   "Story Age": str(story_age),
                                                   "Assignee":issue2.fields.assignee.displayName,
                                                   "Current Status":status,
                                                   "Status Date": str(second_date),
                                                   "Status Age": status_age
                                                   }
    return dict_of_stories


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
    #projects = ["EFO", "EFA", "EFL","EFW"]
    projects = ["EFW"]
    for i in projects:
        delete_table_sql = """DELETE FROM EFW;"""
        execute_sql(delete_table_sql)
        # create_table_sql = """ CREATE TABLE """ + i + """ (
        #                        Issue varchar(255),
        #                        Summary varchar(255),
        #                        Priority varchar(255),
        #                        Reporter varchar(255),
        #                        DateCreated date,
        #                        StoryAge int,
        #                        Assignee varchar(255),
        #                        CurrentStatus varchar(255),
        #                        StatusDate date,
        #                        StatusAge int);
        #                     """
        # execute_sql(create_table_sql)
        stored_dictionary = extract_from_jira(jira,i)
        for k,v in stored_dictionary.items():
            stored_values = []
            sql = ''' INSERT INTO '''+i+''' (Issue, Summary, Priority, Reporter,DateCreated,StoryAge, Assignee, CurrentStatus, StatusDate, StatusAge)
                VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');
                    '''
            stored_values.append(str(k))
            for k1,v1 in v.items():
                stored_values.append(v1)
            sql = sql.format(*stored_values)
            execute_sql(sql)

    print(time.time() - start_time, 'seconds it took to run')

