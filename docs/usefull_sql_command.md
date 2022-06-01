# Some useful sql command


## To delete all tables from a given schema

In below example, we remove everything from the schema `public` (e.g. tables, views, functions, etc.)

```sql

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public IS 'standard public schema';
```