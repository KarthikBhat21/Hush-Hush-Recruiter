from email.mime.multipart import MIMEMultipart
import logging
from os import read
import sys
import mysql.connector
from datetime import date
from numpy.core.fromnumeric import mean
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.io import json
import requests
from pprint import pprint
from types import SimpleNamespace
from bs4 import BeautifulSoup
import time 
import threading
import csv
import smtplib
import numpy as np
from scipy.stats.stats import mode
from sklearn import impute
import statsmodels.api as sm
from sklearn.impute import SimpleImputer
import statistics


from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from email.mime.text import MIMEText

from requests.api import delete, options
from tkinter import *
from tkinter import ttk
 
root = Tk()
root.title('Hush Hush Recruitment Agency')
root.geometry("400x400")

start = time.perf_counter()

github_skillListCombo = []

github_dataList = []

# Fetching the Github data from the csv file.

def func_github():
    count1 = 0
    reader = None

    # This 'GithubData.csv' file will be fetched from the current working directory
    fname = 'GithubData.csv'
    try:
        f = open(fname, 'r')
            #reader = csv.reader(csvfile)
    except OSError:
        print("Could not open/read file:", fname)
        sys.exit()

    with f:
        reader = csv.reader(f)
        for row in reader:
            print(row)
            github_dataList.append(row)

    print("Github Data fetched successfully")

skillsList_for_combo = []


username = "tapati93"
# url = f"https://api.stackexchange.com/2.3/users/{636656}/answers?order=desc&sort=activity&site=stackoverflow"
url = f"https://api.stackexchange.com/2.3/users?pagesize=100&order=desc&sort=reputation&site=stackoverflow"

user_data = requests.get(url).json()

#print(user_data)

mydb = mysql.connector.connect(host='localhost',
                               user='root',
                               password='',
                               database='recruiter') 

if mydb.is_connected():
    print("connected")

mycursor = mydb.cursor()

sql3 = ("delete from stackoverflow_details")
mycursor.execute(sql3)

mydb.commit()



sql4 = ("INSERT INTO stackoverflow_details (Acc_id, User_Name, Top_Skill, Skill_Score, Gold_count, Silver_Count, Bronze_count, Reputation, Stack_overflow_link, Email_Address) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")           


Acc_id = []
User_Name = []
Location = []
Gold_count = []
Silver_Count = []
Bronze_count = []
Accept_rate = []
Reputation = []
stack_overflow_link = []

userMailId = 'hushhush.rec@gmail.com'

def func_stackOverflow():
    count = 0
    for item in user_data['items']:
        flag = False
        firstSkill = False
        count = count + 1
        
        Acc_id.append(item['account_id'])
        User_Name.append(item['display_name'])
        
        Gold_count.append(item['badge_counts']['gold'])
        Silver_Count.append(item['badge_counts']['silver'])
        Bronze_count.append(item['badge_counts']['bronze'])
        
        Reputation.append(item['reputation'])
        stack_overflow_link.append(item['link'])
        accept_rate = None

        if 'accept_rate' in item:
            accept_rate = item['accept_rate']

        # Fetching the Skills and Skill score by making use of web scraping 

        res = requests.get(item['link'])
        
        soup = BeautifulSoup(res.text, "html.parser")

        skill = soup.find_all('a', {'class' : 'post-tag js-gps-track'})


        skillScore = soup.find_all('span', {'class' : 'fc-medium fs-title'})

        skillScore_str = skillScore[0].text.replace(",", "")

        
        val2 = [(item['account_id'], item['display_name'], skill[0].text, skillScore_str, item['badge_counts']['gold'], item['badge_counts']['silver'], item['badge_counts']['bronze'],
                                item['reputation'], item['link'], userMailId)]

        # This will be used inorder to fetch the skills present in stack overdlow and put it in combobox
        if(len(skillsList_for_combo) == 0):
            
            skillsList_for_combo.append("Select a Skill!!")
        else:
            for item in range(len(skillsList_for_combo)):
                if(skillsList_for_combo[item] == skill[0].text):
                    flag = True
        
        if((flag == False)):
            skillsList_for_combo.append(skill[0].text)
        
        mycursor.executemany(sql4, val2)
        
    
    # Gold_count_mean = statistics.mean(Gold_count)

    # Silver_Count_mean = statistics.mean(Silver_Count)

    # Bronze_count_mean = statistics.mean(Bronze_count)

    # Reputation_mean = statistics.mean(Reputation)

    mydb.commit()

    print(f"Stack Overflow Records Inserted: {count}")



# Threading function is being used for fetching the data from Github and Stack Overflow.

t1 = threading.Thread(target=func_github)
t2 = threading.Thread(target = func_stackOverflow)

t1.start()
t2.start()

t1.join() 
t2.join()


# Fetch Stackoverflow details from Database and put in the csv file
###################################################################

sql12 = mycursor.execute("SELECT * FROM stackoverflow_details")
stkoflw_data = mycursor.fetchall()
stkoflw_data_df = pd.DataFrame(stkoflw_data)

stkoflw_data_df.to_csv("StackOverflow_records.csv")


print("StackOverflow details written successfully")

####################################################################

# Sending the mail for the selected candidates
################################################
def sendMail(shortlistedMails):
    # Q1 = Question1.get(1.0, END)
    # Q2 = Question2.get(1.0, END)
    # Q3 = Question3.get(1.0, END)

    gmail_user = 'hushhush.rec@gmail.com'
    gmail_password = 'Hushhush@123'
    test = '1.task1<br/>2.task2<br/>'
    sent_from = gmail_user
    #to = ['rimy5693@gmail.com', 'karthikbhat.sit@gmail.com']

    to = shortlistedMails

    leng = len(shortlistedMails)

    subject = 'Congratulations'

    html ="""\<html><h3>Complete the given task</h3><p>There are a few steps you need to complete for the next round of the interview.</p><p>Click <a href="https://www.hackerrank.com/challenges/py-hello-world/problem">here</a> for a programming task.</p><h4>Thank & Regards</h4><h4>Doodle</h4></html>"""
    body = MIMEText(html,'html')
    
    email_text = """\
    From: %s
    To: %s
    Subject: %s
    
    %s
    """ % (sent_from, ", ".join(to), subject, body)
    
    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        #print ("Email sent successfully!")
        print(f'Emails sent to {leng} people successfully')
    except Exception as ex:
        print ("Something went wrong….",ex)

################################################


print(github_dataList)
print(len(github_dataList))
github_dataList_df = pd.DataFrame(github_dataList)


print(type(github_dataList_df))

print(github_dataList_df[5].mean())
 
shortlistedNames = []

# Applying the logistic regression algorithm for the dataset

def algo():
    skillFilter = myCombo.get()
    skill = skillFilter
    shortlistedNames = []
    # Fetch the Stackoverflow details from excel file
    ####################################################################
    stckOvrflw_dataList = []

    # The StkOverflow_records.csv file is being fetched from the current working directory
    with open('StkOverflow_records.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            stckOvrflw_dataList.append(row)
            print(row)

    print("Stackoverflow data fetched successfully from file")
    ####################################################################

    stckOvrflw_dataList_df = pd.DataFrame(stckOvrflw_dataList)

    print("It works man!!")
    print(stckOvrflw_dataList_df)

    sql1 = mycursor.execute("SELECT * FROM stackoverflow_details WHERE Top_Skill = '"+skill+"'")
    
    result = mycursor.fetchall()
    for i in result:
        print(i)

    # Merging both the Stack Overflow and Github data using Outer join on the User Names:

    merge_result = pd.merge(github_dataList_df, stckOvrflw_dataList_df, left_on=1, right_on=1,how='outer')


    merge_result.columns = ["GitLogin_ID", "GitCandidate_Names", "Git_no_of_foll", "Git_No_of_reps", "Git_Skill", "Git_StarsCount", "Git_link", "Github_flag",
                            "SO_Acc_ID", "SO_Skill", "SO_Skill_score", "SO_Gold_count", "SO_Silver_count", "SO_Bronze_count", "SO_Reputation",
                               "SO_Link", "Email_addr", "SO_flag"]


    print(merge_result)
    print(type(merge_result))

    merge_result.to_csv('Merged_data.csv')
    
    print("Merged Data Inserted successfully")

    dataset = pd.read_csv(r"Merged_data.csv")

    print(dataset)

    # Taking the Stack Overflow and Github flag and ORing it to get the final Flag value for both the datasets

    dataset['Dep_var'] = np.logical_or(dataset['Github_flag'] == 1, dataset['SO_flag'] == 1)

    # Imputing the independent variables using Mean of the particular column and make a csv file after imputing the data
    #####################################################################################################

    dataset['SO_Reputation'] = dataset['SO_Reputation'].replace(np.nan,dataset['SO_Reputation'].mean())

    dataset['Git_StarsCount'] = dataset['Git_StarsCount'].replace(np.nan,dataset['Git_StarsCount'].mean())

    dataset['SO_Skill_score'] = dataset['SO_Skill_score'].replace(np.nan,dataset['SO_Skill_score'].mean())

    dataset['SO_Gold_count'] = dataset['SO_Gold_count'].replace(np.nan,dataset['SO_Gold_count'].mean())

    dataset['SO_Silver_count'] = dataset['SO_Silver_count'].replace(np.nan,dataset['SO_Silver_count'].mean())

    dataset['SO_Bronze_count'] = dataset['SO_Bronze_count'].replace(np.nan,dataset['SO_Bronze_count'].mean())

    dataset.to_csv('Merged_data1.csv')

    #####################################################################################################
    
    print("The results are as follows:")
    print(dataset['Dep_var'])


    github_dataList1 = []

    # The merged dataset with imputed values and the final flag will be in Merged_data1.csv and has to be fetched from the current
    # working directory

    with open('Merged_data1.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        print(type(reader))
        for row in reader:
            #print(row)
            github_dataList1.append(row)

        print("Github Data fetched successfully")

    print(type(github_dataList1))
    print(github_dataList1)

    # This code snippet will fetch only those rows from the merged dataset whose skill is equal to the combobox skill selected
    # and will be put in a list and for this the Logistic Regression will be applied.

    dataset1 = []

    for item in range(len(github_dataList1)):
        present_skill = github_dataList1[item][6]
        present_skill1 = github_dataList1[item][11]

        if((github_dataList1[item][6] == skillFilter) or (github_dataList1[item][11] == skillFilter)):
            dataset1.append(github_dataList1[item])

    
    print(dataset1)

    #The dataset1 list will be converted to tuple inorder to fetch the data column wise.

    tlist = list(zip(*dataset1))

    datatype = print(type(tlist[7]))

    dependent_var = pd.DataFrame(tlist[20]).values.reshape(-1, 1)


    # Converting the string values in tuple to float
    ################################################

    ind_star_cnt_f = [float(x) for x in tlist[7]] 

    ind_skl_scr_f = [float(x) for x in tlist[12]]

    ind_gld_cnt_f = [float(x) for x in tlist[13]]

    ind_slvr_cnt_f = [float(x) for x in tlist[14]]

    ind_brnz_cnt_f = [float(x) for x in tlist[15]]

    ind_reput_f = [float(x) for x in tlist[16]]

    ################################################

    # Reshape the values of the float converted values to fit in a 2D array
    #######################################################################

    ind_star_cnt_df = pd.DataFrame(ind_star_cnt_f).values.reshape(-1, 1)

    ind_skl_scr_df = pd.DataFrame(ind_skl_scr_f).values.reshape(-1, 1)

    ind_gld_cnt_df = pd.DataFrame(ind_gld_cnt_f).values.reshape(-1, 1)

    ind_slvr_cnt_df = pd.DataFrame(ind_slvr_cnt_f).values.reshape(-1, 1)

    ind_brnz_cnt_df = pd.DataFrame(ind_brnz_cnt_f).values.reshape(-1, 1)

    ind_reput_df = pd.DataFrame(ind_reput_f).values.reshape(-1, 1)

    #######################################################################


    dependent_var_df = pd.DataFrame(dependent_var).values.reshape(-1, 1)    # Reshape changes 1D to 2D array

    # Applying the logistic regression for the dataset

    log_reg = LogisticRegression(solver='lbfgs', max_iter=1000)

    result = log_reg.fit(ind_star_cnt_df + ind_gld_cnt_df + ind_reput_df, np.ravel(dependent_var_df))
    
    y_pred = log_reg.predict(ind_star_cnt_df + ind_gld_cnt_df + ind_reput_df)

    # Confusion Matrix

    print("Confusion matrix")
    print("\n")
    print(confusion_matrix(dependent_var_df, y_pred))

    # Calculating the Accuracy of the model

    accuracy = log_reg.score(ind_star_cnt_df + ind_gld_cnt_df + ind_reput_df, dependent_var_df)

    print(accuracy)

    # Shortlisting only those people whose Flag value is equal to 'True'

    shortlisted = []

    for item in range(len(dataset1)):
        if(dataset1[item][20] == 'True'):
            shortlisted.append(dataset1[item])

    #shortlisted_len = print(len(shortlisted))

    mailsList = []
    for item in range(len(shortlisted)):
        if(shortlisted[item][8] != ''):
            mailsList.append(shortlisted[item][8])
        else:
            mailsList.append(shortlisted[item][18])
        
    # Send the mail to the shortlisted candidates.

    sendMail(mailsList)

    shortlistedNames = []
    for item in range(len(shortlisted)):
        shortlistedNames.append(shortlisted[item][3])

######################################################################

finish = time.perf_counter()

print(f'Finished in {round(finish-start, 2)} second(s)')

# The skillsList_for_combo consists of all the skills found in the Github and Stackoverflow data sources
options = skillsList_for_combo

# Putting the Combobox in the GUI
myCombo = ttk.Combobox(root, value=options,)
myCombo.current(0)
myCombo.pack()
myCombo.place(x = 135 ,y = 100)

# QtnLabel1 = Label(root, text = "Question 1:")
# QtnLabel1.place(x = 40, y = 115)
# Question1 = Text(root, height = 3, width = 31)
# Question1.place(x=110, y=100)

# QtnLabel2 = Label(root, text = "Question 2:")
# QtnLabel2.place(x = 40, y = 180)
# Question2 = Text(root, height = 3, width = 31)
# Question2.place(x=110, y=165)

# QtnLabel3 = Label(root, text = "Question 3:")
# QtnLabel3.place(x = 40, y = 245)
# Question3 = Text(root, height = 3, width = 31)
# Question3.place(x=110, y=230)

# Putting the Button in the GUI
w = Button(root, text="Go", command = algo)
w.pack()
w.place(x=180,y = 140)

root.mainloop()

mycursor.close()
mydb.close()

