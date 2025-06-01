/*
 --------------------------------------------------------------
 -- Retrieves the top 10 most engaged tweets associated with 
 -- pollution-related hashtags. The query links hashtags with 
 -- tweet engagement metrics (likes, retweets, quotes, replies, 
 -- and views).
 --
 -- Steps:
 -- 1) Joins tweet, hashtag, and engagement tables.
 -- 2) Orders results by engagement metrics (likes, retweets, etc.).
 -- 3) Limits output to the top 10 tweets.
 --
 -- This output highlights the most interacted-with pollution-related 
 -- tweets, supporting social media impact analysis.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS most_engaged_tweets_on_pollution_hashtags;

CREATE VIEW most_engaged_tweets_on_pollution_hashtags AS
SELECT
    h.hashtag_name,
    e.like_count,
    e.retweet_count,
    e.quote_count,
    e.reply_count,
    e.view_count
FROM
    social_media_dim.tweet_hashtag th
    JOIN social_media_dim.hashtag h ON th.id_hashtag = h.id_hashtag
    JOIN social_media_dim.tweet t ON th.id_tweet = t.id_tweet
    JOIN social_media_dim.engagement e ON t.id_tweet = e.id_tweet
ORDER BY
    e.like_count DESC,
    e.retweet_count DESC,
    e.quote_count DESC,
    e.reply_count DESC,
    e.view_count DESC
LIMIT
    10;