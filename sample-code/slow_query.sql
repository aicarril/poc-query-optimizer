-- Unoptimized query against demo_db — intentionally bad for demo
-- Issues: SELECT *, no partition pruning, comma join, no aliases on columns

SELECT *
FROM demo_db.events e, demo_db.users u
WHERE e.user_id = u.id
ORDER BY e.created_at DESC
LIMIT 100;

-- Baseline performance (measured):
-- Execution time: 1,467ms
-- Data scanned: 282,563 bytes (all 7 partitions)
