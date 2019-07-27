import praw
import datetime
import numpy as np
import pandas as pd

#Using praw create an instance of reddit. 
reddit = praw.Reddit(client_id='[YOUR ID]',
					client_secret='[YOUR SECRET]',
					password = '[YOUR PASSWORD]',
					user_agent='[YOUR USER AGENT]',
					username = '[YOUR USERNAME]')



print(reddit.read_only)


#The subreddit you want to deal with
subreddit = reddit.subreddit("WritingPrompts")

master = {}#store the id's and repeated info for the posts we're tracking. Used for Panel data storage
masterML = {}#store the id's and repeated info for the posts we're tracking. Used for Machine Learning data storage


#Helper functions to make column names with repeated names with different numbers
def makeColumnNames(names, num):
    ans = []
    for it in range(0, num):
        for name in names:
            ans.append(str(it) + name)
    return ans

def makeColumnNamesAfter(names, num):
    ans = []
    for it in range(1, num+1):
        for name in names:
            ans.append(name + str(it))
    return ans

#get the age of a submission
def get_age(subId):
    submission = praw.models.Submission(reddit, id = subId)
    date = datetime.datetime.fromtimestamp(submission.created_utc)
    dif = datetime.datetime.now() - date
    return dif.total_seconds()/3600

#get number of top level comments (assuming one automod post which is disregarded)
def numStories(subId):
    x = praw.models.Submission(reddit, id = subId).comments
    return len(x) - 1

#function to get last index of a list
def getLastIndex(myList):
    return(len(myList) -  1)

#Get the information for top X posts
def getHotInfo(lim = 5):
    cnt = 0
    arr = []
    for submission in (subreddit.hot()):
        if(submission.stickied):
            continue
        subId = submission.id
        y = submission.created_utc
        arr.append(y)
        arr.append(submission.score)
        arr.append(get_age(submission.id))
        arr.append(numStories(subId))
        arr.append(submission.upvote_ratio)
        arr.append(submission.num_comments)
        cnt += 1
        if cnt == lim:
            break
    return arr

#function to write information to a file
def writeArr(fileName, arr):
    with open(fileName, 'a+') as f:
        for item in arr:
            f.write("%s," % item)
        f.write("\n")


#record info (in order given below) when first encountering an unseen post 
#id, title, created_utc, age, observation #, max score, t1s, t1a, t2s, t2a, t3s, t3a, t4s, t4a, t5s, t5a,
#score, number stories, upvote ratio, num_coms, #t1s, #t1a, #t2s, #t2a, #t3s, #t3a, #t4s, #t4a, #t5s, #t5a
def newEntry(subId, hots):
    submission = praw.models.Submission(reddit, id = subId)
    arr = []
    sc= submission.score
    arr.append(subId)
    arr.append(submission.title.replace(',', ''))
    y = submission.created_utc
    arr.append(y)
    date = datetime.datetime.fromtimestamp(y)
    dif = datetime.datetime.now() - date
    arr.append(dif/3600)
    arr.append(0)
    arr.append(np.nan)
    arr += hots
    arr.append(sc)
    arr.append(numStories(subId))
    arr.append(submission.upvote_ratio)
    arr.append(submission.num_comments)
    arr += hots
    master[subId] = arr
    masterML[subId] = arr
    writeArr("panelfile.txt", arr)


#update data the posts we are currently tracking
#stop tracking a post after it has been observed for (periods)
def updatePanel(hots, periods):
    rejects = []
    for key, value in master.items():
        itrInd = getLastIndex(value)
        temp = value[0:36]
        temp[4] += 1
        arr = []
        subId = key
        submission = praw.models.Submission(reddit, id = key)
        sc= submission.score
        arr.append(sc)
        arr.append(numStories(subId))
        arr.append(submission.upvote_ratio)
        arr.append(submission.num_comments)
        arr += hots
        #print("before", len(temp))
        temp += arr
        #print("after", len(temp))
        master[subId] = temp
        #print("after", len(master[subId]))
        masterML[subId] += arr
        masterML[subId][4] += 1
        writeArr("panelfile.txt", master[subId])
        if masterML[subId][4] > periods:
            writeArr("MLfile.txt", masterML[subId])
            rejects.append(subId)
    for ID in rejects:
        del masterML[ID]
        del master[ID]


#get the ids of previously untracked posts
def getNews(lastTime, hots):
    for i, submission in enumerate(subreddit.new(limit=237)):
        date = datetime.datetime.fromtimestamp(submission.created_utc)
        subId = submission.id
        if subId not in master:
            newEntry(subId, hots)
        else:
            print("overlap detected", subId, "conflict logged and succesfully avoided")
        if date < lastTime:
            print(i+1, "submissions added")
            break;

#sleep till given time
#https://stackoverflow.com/questions/5677853/how-to-run-a-python-script-at-a-specific-times
def sleep_till_future(f_hour, f_minute):
    import time,datetime
    t = datetime.datetime.today()
    future = datetime.datetime(t.year,t.month,t.day,f_hour,f_minute)

    if (future.minute <= t.minute) and (future.hour <= t.hour):
        print("ERROR! Enter a valid minute in the future. Didn't sleep")
        print("Current time: " + str(t.hour)+":"+str(t.minute))
    else:
        print("Current time: " + str(t.hour)+":"+str(t.minute))
        print("Sleep until : " + str(future.hour)+":"+str(future.minute))

        seconds_till_future = (future-t).seconds
        time.sleep( seconds_till_future )
        print("I slept for "+str(seconds_till_future)+" seconds!")



#core loop
master = {}
masterML = {}
startTime = datetime.datetime.now()
cnt = 0
interval = 20#how many minte long our periods are
mins = startTime.minute
h = datetime.datetime.today().hour
#log time information
while(True):
    print("iteration", cnt)#what iteration our bot is on
    print("getting hots", datetime.datetime.now())
    hots = getHotInfo()
    print("updating", datetime.datetime.now())
    updatePanel(hots, 60)
    print("getting news", datetime.datetime.now())
    getNews(startTime, hots)
    startTime = datetime.datetime.now()
    sleep_till_future(h, mins)
    cnt += 1
    mins += interval
    #calculating time to wake up at
    if(mins > 60):
        h += 1
        if h >= 24:
            h = 0
        mins = mins % 60
