-- ============================================================================
-- Olist delivery analysis — reference queries (DuckDB syntax)
-- These mirror src/data_loader.py. Run them ad-hoc while exploring.
-- ============================================================================

-- 1. Base table: one row per DELIVERED order, with delivery time + late flag
WITH delivery AS (
    SELECT
        o.order_id,
        o.customer_id,
        date_diff('day', o.order_purchase_timestamp,
                         o.order_delivered_customer_date)  AS days_to_deliver,
        date_diff('day', o.order_estimated_delivery_date,
                         o.order_delivered_customer_date)  AS days_vs_estimate,
        CASE WHEN o.order_delivered_customer_date
                  > o.order_estimated_delivery_date
             THEN 1 ELSE 0 END                             AS is_late
    FROM orders o
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT * FROM delivery LIMIT 20;


-- 2. THE CORE FINDING: review score for on-time vs late orders
--    (wrap query 1 as a CTE, then join reviews)
WITH delivery AS ( /* ...same as above... */
    SELECT o.order_id,
           CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                THEN 1 ELSE 0 END AS is_late
    FROM orders o
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
    CASE WHEN d.is_late = 1 THEN 'Late' ELSE 'On time' END AS delivery_status,
    COUNT(*)                       AS n_orders,
    ROUND(AVG(r.review_score), 2)  AS avg_review_score
FROM delivery d
JOIN order_reviews r ON d.order_id = r.order_id
GROUP BY 1
ORDER BY 1;


-- 3. WINDOW FUNCTION: rank categories by late-delivery rate (volume-aware)
WITH delivery AS (
    SELECT o.order_id,
           CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                THEN 1 ELSE 0 END AS is_late
    FROM orders o
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
    t.product_category_name_english         AS category,
    COUNT(*)                                AS n_orders,
    ROUND(AVG(d.is_late) * 100, 1)          AS late_pct,
    RANK() OVER (ORDER BY AVG(d.is_late) DESC) AS late_rank
FROM delivery d
JOIN order_items i ON d.order_id = i.order_id
JOIN products    p ON i.product_id = p.product_id
JOIN category_translation t
     ON p.product_category_name = t.product_category_name
GROUP BY category
HAVING COUNT(*) >= 100
ORDER BY late_pct DESC;


-- 4. MONTH-OVER-MONTH late rate with LAG (trend)
WITH delivery AS (
    SELECT
        date_trunc('month', o.order_purchase_timestamp) AS purchase_month,
        CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
             THEN 1 ELSE 0 END AS is_late
    FROM orders o
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
    purchase_month,
    ROUND(AVG(is_late) * 100, 1)                                  AS late_pct,
    ROUND(AVG(is_late) * 100
          - LAG(AVG(is_late) * 100) OVER (ORDER BY purchase_month), 1) AS change_vs_prev_month
FROM delivery
GROUP BY purchase_month
ORDER BY purchase_month;
