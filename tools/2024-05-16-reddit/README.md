### Issue #261 analysis

For context, see https://github.com/hykilpikonna/hyfetch/issues/261

The files in this directory are related to the automated sentiment analysis for the Reddit comments.

* `reddit.js`: JS script to crawl relevant Reddit comments.
* `reddit.json`: Crawled raw data
* `reddit_gpt.py`: Python script categorizing comment sentiment using GPT-4o 
* `reddit_opinions.json`: Categorized sentiment data

These files are not really related to the functionality of hyfetch, but I'm pushing them here to
make my analysis reproducible, and preserve the data in case the reddit post is deleted.
