-- Optimized version of slow_query.sql — demonstrates what the Query Optimizer Agent produces
-- Improvements: explicit columns, partition pruning, explicit JOIN, CTE, uppercase keywords

WITH high_volume_events AS (
    SELECT event_type
    FROM events
    WHERE partition_date >= DATE_ADD('day', -7, CURRENT_DATE)
    GROUP BY event_type
    HAVING COUNT(*) > 100
)

SELECT
    e.event_id,
    e.event_type,
    e.created_at,
    e.payload,
    u.user_name,
    u.email
FROM events e
INNER JOIN users u ON e.user_id = u.id
INNER JOIN high_volume_events hve ON e.event_type = hve.event_type
WHERE e.partition_date >= DATE_ADD('day', -7, CURRENT_DATE)
ORDER BY e.created_at DESC
LIMIT 1000;
