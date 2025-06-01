/*
 --------------------------------------------------------------
 -- Retrieves key user metrics (follower count, total tweets, 
 -- favorite count, and verification status) for the most active 
 -- users. The query groups results by user ID and orders them by 
 -- engagement metrics.
 --
 -- Steps:
 -- 1) Groups user data by ID.
 -- 2) Orders results by follower count, tweet count, favorite 
 --    count, and verification status.
 -- 3) Limits output to the top 10 users.
 --
 -- This output identifies the most influential users.
 -- The IDs are anonymized to protect user privacy.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS most_active_users;

CREATE VIEW most_active_users AS
SELECT
    RANK() OVER (
        ORDER BY
            follower_count DESC,
            tweet_count DESC,
            favourite_count DESC,
            is_verified_paid_blue DESC
    ) AS rank,
    follower_count,
    tweet_count,
    favourite_count,
    is_verified_paid_blue
FROM
    social_media_dim.user
GROUP BY
    id_user
ORDER BY
    follower_count DESC,
    tweet_count DESC,
    favourite_count DESC,
    is_verified_paid_blue DESC
LIMIT
    10;