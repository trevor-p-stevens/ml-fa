import duckdb

con = duckdb.connect("ml-fa.duckdb")
con.execute("SET memory_limit='4GB';")
con.execute("SET threads=4;")

con.execute("DROP TABLE IF EXISTS training_data_clean;")
con.execute("""
CREATE TABLE training_data_clean AS
SELECT DISTINCT *
FROM training_data
WHERE mar_30d IS NOT NULL
  AND mar_60d IS NOT NULL
  AND mar_90d IS NOT NULL
  AND mar_1y  IS NOT NULL
""")

before = con.execute("SELECT COUNT(*) FROM training_data").fetchone()[0]
after  = con.execute("SELECT COUNT(*) FROM training_data_clean").fetchone()[0]
print(f"Before: {before:,} → After: {after:,} (dropped {before-after:,} rows)")

con.execute("""
COPY training_data_clean TO 'training_data_clean.csv.gz' (FORMAT CSV, HEADER true, COMPRESSION gzip);
""")
print("Done — training_data_clean.csv.gz created.")