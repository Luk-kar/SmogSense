/*
 --------------------------------------------------------------
 -- Retrieves the total number of tweets associated with each 
 -- pollution-related hashtag. The query counts occurrences of 
 -- each hashtag and orders them by usage.
 --
 -- Steps:
 -- 1) Joins tweet and hashtag tables to link tweets with hashtags.
 -- 2) Counts tweets per hashtag.
 -- 3) Orders results by tweet count in descending order.
 --
 -- This output identifies the most popular pollution-related 
 -- hashtags.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS tweet_count_by_pollution_hashtags;

CREATE VIEW tweet_count_by_pollution_hashtags AS
SELECT
    h.hashtag_name,
    COUNT(*) AS tweet_count
FROM
    social_media_dim.tweet_hashtag th
    JOIN social_media_dim.hashtag h ON th.id_hashtag = h.id_hashtag
GROUP BY
    h.hashtag_name
ORDER BY
    tweet_count DESC;