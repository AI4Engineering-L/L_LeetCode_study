SELECT DISTINCT c.customer_id
FROM Customer AS c
WHERE NOT EXISTS (
    SELECT 1 FROM Product AS p
    WHERE NOT EXISTS (
        SELECT 1 FROM Customer AS bought
        WHERE bought.customer_id = c.customer_id AND bought.product_key = p.product_key
    )
);
