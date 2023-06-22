with temp AS (
    SELECT
        DISTINCT p.team AS team,
        strftime('%Y', m.date) AS year,
        m.gender,
        SUM(CASE WHEN p.team = m.team1 or p.team = m.team2 THEN 1 ELSE 0 END) AS totalmatches,
        SUM(CASE WHEN p.team = m.result  THEN 1 ELSE 0 END) AS winCount
    FROM 
        MATCH_DETAILS_ODI AS m
    JOIN 
        PLAYER_ODI AS p ON p.id = m.id
    WHERE
        strftime('%Y', date) = '2019'
    GROUP BY 
        year, gender, team
    ORDER BY 
        YEAR DESC
)
SELECT 
    year,
    team,
    gender,
    winCount,
    round(winCount * 100.0 / totalMatches) AS winPercentage
FROM 
    temp
WHERE
winPercentage = (
    SELECT MAX((winCount * 100.0) / totalmatches)
    FROM temp
  );
