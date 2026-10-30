-- ============================================================================
-- 008_create_triggers.sql
-- ColdChain IQ Platform: Audit & Timestamp Triggers
-- ============================================================================

-- 1. Product updated_at trigger
DROP TRIGGER IF EXISTS trg_products_updated_at ON products;
CREATE TRIGGER trg_products_updated_at
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_column();

-- 2. Users updated_at trigger
DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_column();
