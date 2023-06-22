WITH cte AS (
    SELECT
        batter_name,
        SUM(batter_runs) AS total_runs,
        COUNT(*) AS total_balls,
        SUM(CASE WHEN extras > 0  THEN 1 ELSE 0 END) AS total_extras
    FROM
        INNINGS_ODI
    INNER JOIN
        MATCH_DETAILS_ODI ON INNINGS_ODI.id = MATCH_DETAILS_ODI.id
    WHERE
        strftime('%Y', date) = '2019'
    GROUP BY
        batter_name
)
SELECT
    batter_name,
    (total_runs * 100.0) / (total_balls - total_extras) AS strike_rate
FROM
    cte
ORDER BY
    strike_rate DESC;
