# redditScraper
personal subreddit web scraper to return back all items on sale on marketplace subreddits. Tested with r/hardwareswap, r/buildapcsales, r/gamesale and r/mechmarket. Writes to and returns a .csv file that is kept in ./output folder of root as well as uploads final copy of .csv to Google Drive (upload is optional).

# How to use: 
    Clone repo
    activate Google Drive API on google dev console and retrieve credentials.json file 
    change filename of generated credentials to client_secrets.json and move to root dir of redditScraper
    cd into root dir
    run python3 -m index
    answer questions when prompted!
