/*
 --------------------------------------------------------------
 -- Analyzes monthly tweet volume trends for tweets containing 
 -- at least one hashtag. The query ensures all months between 
 -- the earliest and latest tweet are included, even if no tweets 
 -- occurred in a given month.
 --
 -- Steps:
 -- 1) Generates a monthly date series from the earliest to the 
 --    latest tweet date.
 -- 2) Counts tweets per month, including months with zero tweets.
 -- 3) Orders results chronologically for trend analysis.
 --
 -- This output supports the identification of monthly patterns in 
 -- social media activity related to pollution.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS monthly_tweet_volume_trend;

CREATE VIEW monthly_tweet_volume_trend AS WITH date_series AS (
    -- Generate a list of all months from the earliest to the latest tweet date
    SELECT
        EXTRACT(
            YEAR
            FROM
                month_year
        ) AS year,
        EXTRACT(
            MONTH
            FROM
                month_year
        ) AS month
    FROM
        generate_series(
            date_trunc(
                'month',
                (
                    SELECT
                        MIN(created_at)
                    FROM
                        social_media_dim.tweet
                )
            ),
            date_trunc(
                'month',
                (
                    SELECT
                        MAX(created_at)
                    FROM
                        social_media_dim.tweet
                )
            ),
            '1 month' :: interval
        ) AS month_year
)
SELECT
    ds.year,
    TO_CHAR(
        TO_DATE(ds.year || '-' || ds.month, 'YYYY-MM'),
        'Month'
    ) AS month_name,
    COALESCE(COUNT(t.id_tweet), 0) AS tweet_count
FROM
    date_series ds
    LEFT JOIN social_media_dim.tweet t ON EXTRACT(
        YEAR
        FROM
            t.created_at
    ) = ds.year
    AND EXTRACT(
        MONTH
        FROM
            t.created_at
    ) = ds.month
GROUP BY
    ds.year,
    ds.month
ORDER BY
    ds.year DESC,
    ds.month DESC;