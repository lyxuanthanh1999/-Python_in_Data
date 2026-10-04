SELECT 'brand' AS table_name, COUNT(*) AS total_rows FROM brand
UNION ALL
SELECT 'category', COUNT(*) FROM category
UNION ALL
SELECT 'seller', COUNT(*) FROM seller
UNION ALL
SELECT 'customer', COUNT(*) FROM customer
UNION ALL
SELECT 'product', COUNT(*) FROM product
UNION ALL
SELECT 'promotion', COUNT(*) FROM promotion
UNION ALL
SELECT 'promotion_product', COUNT(*) FROM promotion_product;
