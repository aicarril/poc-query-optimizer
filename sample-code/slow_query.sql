-- Sample slow Athena query with intentional performance issues for demo
-- This query has: SELECT *, no partition pruning, comma joins, nested subqueries

select *
from events e, users u
where e.user_id = u.id
and e.event_type in (
    select event_type
    from (
        select event_type, count(*) as cnt
        from events
        group by event_type
        having count(*) > 100
    )
)
order by e.created_at desc
limit 1000;
