# RedditReader
A bot that scrapes posts off Reddit. It keeps track of posts for x hours, checking popularity every y minutes. Then, various predictive models are used to estimate the ultimate popularity of each post using as little time data as possible.

# Motivation

RedditReader: Motivation and Details

I have been an active and well known writer for years on the subreddit r/WritingPrompts – an online board where people post story ideas, and others respond to these prompts with stories. When I was starting, I quickly realized that how popular my stories became was highly dependent on what prompt I wrote on. I could write a Nobel-worthy short story on a prompt that had one upvote (think “likes” on other social media), and no one would care for my story as they wouldn’t see it! So, the trick was to pick prompts that would get exposure and write on those. However, pick them too late, and my story would be buried since Reddit shows stories by order of points a story has. And early stories had time to accumulate points uncontested. I became pretty good at eyeballing prompts and picking out potential toppers, but then I began wondering if there was some way to automate the process, to guess much better than I or any other prompt hunter, which prompt was going to be a topper. 

RedditReader aims to do exactly that. Using the Reddit API, I scrape Writing Prompts, collecting data on every single post on the subreddit every 20 minutes. It continues to gather data until a post is 20 hours old, after which the upvotes generally plateau. I track many variables, such as age, upvote count, and number of comments on individual posts, but also the age and upvote count of the posts that are currently at the top on the subreddit. The rationale being, if a relatively new post is on top, it is unlikely to be dethroned for quite a bit, as the Reddit algorithm favors newer posts to display at the top. After a few months of collecting data (I’m collecting more right this second in fact) I put the data in a DataFrame in Python and tuned and ran various machine learning algorithms on the data ranging from basic Feed-Forward Neural Networks in TensorFlow to Random Forests, basic logistic regression, and Gradient Boosters in Sklearn. With a custom ensemble that combines a few of the aforementioned methods, I was able to correctly identify which prompts would be successful (reach greater than 2000 upvotes) with 84 percent accuracy within just two hours. 

I will, however, exploit still more features of my data. The next step is to use natural language processing to take account the quality of the prompt itself and use Recurrent Neural Networks to better leverage the time-series like nature of the data. With a robust enough model, we can go beyond WritingPrompts to any subreddit – it could be a powerful tool; able to predict which posts will gain traction early and have your content seen on one of the most popular websites in the world.  

# The Scraper

We use the PRAW reddit API to scrape our data. See [here](https://praw.readthedocs.io/en/latest/getting_started/quick_start.html) to see how you can set up your own ID and secret to scrape data. In a given subreddit, every X minutes (default 20) the scraper performs a "Check." The scraper maintains a bench, an array that contains currently tracked posts. At each Check, the scraper will:
* Add to the bench any new post that was not already in the bench. 
  * In essence, add to the bench any new posts made since the last check
* Update each post already on the bench. At each update add:
  * Current upvotes, ratio, comments, etc
  * Hot Information - since the success of each post relies heavily on how old the current top posts are, we keep track of how the top posts are doing by looking at upvote ratio, age, comments, and the growth of each. 
 * Remove "matured" posts from bench
  * We only keep track of a post for 20 hours as, after this, upvote count mostly stagnates. Once removed from bench, it is added to MLfile

# The Data

There is a sample file called "miniMLfile." Rename this to MLfile for the code to work. This only has 800 posts, with 20 hours of data each. The columns start with the period they belong to: 1,2,3... and then follow self characteristics, then the characteristics of the top 5. The second top will be, say, 4age2 - this means in the 4th period, the age of the second top post, and so on. Note that it is in csv format. Consider moving to a database of some sort when approaching 10000+ posts. 

# The Analysis
* See [RedditAnalysis.ipynb](RedditAnalysis.ipynb) for a guided walkthrough of the sklearn models

* ## TensorFlow Model ##
  * Using tensorflow, straightforward neural network to predict score of post based on 2 hours of data. (3 periods per hour if using 20 minute intervals)
  * Not very good results. 
  * Tried:
    * dropout - very good results
    * Recurrent Neural Network - similar results
    * Hypertuning of layers and numbers of neurons per layer
    * Appending rows to one another, so as to take as input the neighbors of each post as well - complete failure, this leads to awful results
  * To try:
    * Further tuning
    * Tuning with Recurrent Neural Networks. 
    * Using classifier instead of regressor
    * Using word2vec or other models to codify the titles
* ## SKlearn Models ##

  * Various regressors and classifiers using off shelf sklearn machines
  * Solid results using Gradient Boosting - our current goto
  * RegTestPipeline:
    * Any regression model can be tested using this file. Gives you psuedo K-fold Cross Validation, with custom reports showing perfomance. Correct - correctly identified. Incorrect - Posts that were incorrectly identified. Missed - posts that weren't identified, but should've been. Also included are actual and predicted results for comparison's sake.  
