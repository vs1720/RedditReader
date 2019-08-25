# RedditReader
A Bot that Scrapes posts off reddit. It keeps track of posts for x hours, checking popularity every y minutes. Then various modeling techniques are tried and used in order to predict how many upvotes each post gets based on as little hour data as possible. 

# The Scraper

We use the PRAW reddit API to scrape our data. See [here](https://praw.readthedocs.io/en/latest/getting_started/quick_start.html) to see how you can set up your own ID and secret to scrape data. In a given subreddit, every X minutes (default 20) the scraper performs a "Check." The scraper mantains a bench, an array that keeps track of currently tracked posts. At each Check, the scraper:
* Adds to the bench any new post that was not already in the bench. 
  * In essence, add to the bench any new posts made since the last check
* Update each post already on the bench. Each update add:
  * Current upvotes, ratio, comments, etc
  * Hot Information - since the success of each post relies heavily on how old the current top posts are, we keep track of how the top posts are doing
 * Remove "matured" posts from bench
  * We onnly keep track of a post for 20 hours as after this upvote count mostly stagnates. Once removed from bench, it is added to MLfile

# The Data

There is a sample file called "miniMLfile." Rename this to MLfile for the code to work. This simply has 800 psts, with 20 hours of data each. The columns start with the period they belong to: 1,2,3... and then follow self charecteristics, then the charcteristics of the top 5. The second top will be, say, 4age2 - this means in the 4th period, the age of the second top post, and so on. Note that it is in csv format. Consider moving to a database of some sort when approaching 10000+ posts. 

# The Analysis

* ## TensorFlow Model ##
  * Using tensorflow, straighforward nueral network to predict score of post based on 2 hours of data. (3 periods per hour if using 20 minute intervals)
  * Not very good results. 
  * Tried:
    * dropout - very good results
    * Recurrent Neural Network - similar results
    * Various hypertuning of layers and numbers of neurons per layer
    * Appending rows to one another, so as to take as input the neighbors of each post as well - complete failure, this leads to awful results
  * To try:
    * Further tuning
    * tuning with RNN
    * Using classifier instead of regressor
* ## SKlearn Models ##

  * Various regressors and classifiers using off shelf sklearn machines
  * Solid results using Gradient Boosting - our current goto
  * RegTestPipeline:
    * Any regression model can be tested using this file. Gives you psuedo 4-fold Cross Validation, with custom reports showing perfomance. Correct - correctly identified. Incorrect - Posts that were incorrectly identified. Missed - posts that weren't identified, but should've been. Also included are actual and predicted results for comparison's sake.  
