/*
 --------------------------------------------------------------
 -- Analyzes daily tweet volume trends for tweets containing 
 -- at least one hashtag. The query ensures all days between the 
 -- earliest and latest tweet are included, even if no tweets 
 -- occurred on a given day.
 --
 -- Steps:
 -- 1) Generates a date series from the earliest to the latest 
 --    tweet date.
 -- 2) Counts tweets per day, including days with zero tweets.
 -- 3) Orders results chronologically for trend analysis.
 --
 -- This output supports the identification of daily patterns in 
 -- social media activity related to pollution.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS daily_tweet_volume_trend;

CREATE VIEW daily_tweet_volume_trend AS WITH date_series AS (
    -- Generate a list of all days from the earliest to the latest tweet date
    SELECT
        day_date :: DATE AS tweet_date
    FROM
        generate_series(
            (
                SELECT
                    date_trunc('day', MIN(created_at))
                FROM
                    social_media_dim.tweet
            ),
            (
                SELECT
                    date_trunc('day', MAX(created_at))
                FROM
                    social_media_dim.tweet
            ),
            '1 day' :: interval
        ) AS day_date
)
SELECT
    ds.tweet_date,
    COALESCE(COUNT(t.id_tweet), 0) AS tweet_count
FROM
    date_series ds
    LEFT JOIN social_media_dim.tweet t ON date_trunc('day', t.created_at) = ds.tweet_date
GROUP BY
    ds.tweet_date
ORDER BY
    ds.tweet_date DESC;