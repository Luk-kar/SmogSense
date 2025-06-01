/*
 --------------------------------------------------------------
 -- Calculates total engagement metrics (likes, retweets, quotes, 
 -- replies, and views) for each pollution-related hashtag. The 
 -- query aggregates engagement data by hashtag and retrieves the 
 -- top 10 most engaged hashtags.
 --
 -- Steps:
 -- 1) Joins tweet, hashtag, and engagement tables.
 -- 2) Aggregates engagement metrics per hashtag.
 -- 3) Orders results by total engagement in descending order.
 -- 4) Limits output to the top 10 hashtags.
 --
 -- This output identifies the most impactful pollution-related 
 -- hashtags, supporting social media strategy and analysis.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS most_engaged_hashtags;

CREATE VIEW most_engaged_hashtags AS
SELECT
    h.hashtag_name,
    SUM(e.like_count) AS like_sum,
    SUM(e.retweet_count) AS retweet_sum,
    SUM(e.quote_count) AS quote_sum,
    SUM(e.reply_count) AS reply_sum,
    SUM(e.view_count) AS view_sum,
    RANK() OVER (
        ORDER BY
            (
                SUM(e.like_count),
                SUM(e.retweet_count),
                SUM(e.quote_count),
                SUM(e.reply_count),
                SUM(e.view_count)
            ) DESC
    ) AS rank
FROM
    social_media_dim.tweet_hashtag th
    JOIN social_media_dim.hashtag h ON th.id_hashtag = h.id_hashtag
    JOIN social_media_dim.tweet t ON th.id_tweet = t.id_tweet
    JOIN social_media_dim.engagement e ON t.id_tweet = e.id_tweet
GROUP BY
    h.id_hashtag
ORDER BY
    like_sum DESC,
    retweet_sum DESC,
    quote_sum DESC,
    reply_sum DESC,
    view_sum DESC
LIMIT
    10;