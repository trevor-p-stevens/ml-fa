import duckdb

con = duckdb.connect("ml-fa.duckdb")
con.execute("SET memory_limit='4GB';")
con.execute("SET threads=4;")

con.execute("DROP TABLE IF EXISTS daily_index;")
con.execute("CREATE TABLE daily_index AS SELECT * FROM read_csv_auto('wrds_data/daily_index.csv.gz');")

# Check what it looks like
print(con.execute("SELECT * FROM daily_index LIMIT 5").df())

con.execute("DROP TABLE IF EXISTS y_train;")

con.execute("""
CREATE TABLE y_train AS
WITH fwd_returns AS (
    SELECT 
        permno,
        date,
        EXP(SUM(LN(1 + COALESCE(NULLIF(ret, -1), -0.999))) OVER (PARTITION BY permno ORDER BY date ROWS BETWEEN 1 FOLLOWING AND 21  FOLLOWING)) - 1 AS ret_30d,
        EXP(SUM(LN(1 + COALESCE(NULLIF(ret, -1), -0.999))) OVER (PARTITION BY permno ORDER BY date ROWS BETWEEN 1 FOLLOWING AND 42  FOLLOWING)) - 1 AS ret_60d,
        EXP(SUM(LN(1 + COALESCE(NULLIF(ret, -1), -0.999))) OVER (PARTITION BY permno ORDER BY date ROWS BETWEEN 1 FOLLOWING AND 63  FOLLOWING)) - 1 AS ret_90d,
        EXP(SUM(LN(1 + COALESCE(NULLIF(ret, -1), -0.999))) OVER (PARTITION BY permno ORDER BY date ROWS BETWEEN 1 FOLLOWING AND 252 FOLLOWING)) - 1 AS ret_1y
    FROM X_technical
    ORDER BY permno, date
),
market_returns AS (
    SELECT 
        date,
        EXP(SUM(LN(1 + COALESCE(NULLIF(vwretd, -1), -0.999))) OVER (ORDER BY date ROWS BETWEEN 1 FOLLOWING AND 21  FOLLOWING)) - 1 AS mkt_30d,
        EXP(SUM(LN(1 + COALESCE(NULLIF(vwretd, -1), -0.999))) OVER (ORDER BY date ROWS BETWEEN 1 FOLLOWING AND 42  FOLLOWING)) - 1 AS mkt_60d,
        EXP(SUM(LN(1 + COALESCE(NULLIF(vwretd, -1), -0.999))) OVER (ORDER BY date ROWS BETWEEN 1 FOLLOWING AND 63  FOLLOWING)) - 1 AS mkt_90d,
        EXP(SUM(LN(1 + COALESCE(NULLIF(vwretd, -1), -0.999))) OVER (ORDER BY date ROWS BETWEEN 1 FOLLOWING AND 252 FOLLOWING)) - 1 AS mkt_1y
    FROM (SELECT DISTINCT date, vwretd FROM daily_index)
    ORDER BY date
)
SELECT
    f.gvkey,
    f.LPERMNO,
    f.event_date,
    t.ret_30d - m.mkt_30d AS mar_30d,
    t.ret_60d - m.mkt_60d AS mar_60d,
    t.ret_90d - m.mkt_90d AS mar_90d,
    t.ret_1y  - m.mkt_1y  AS mar_1y
FROM X_fundq_ccm f
ASOF JOIN fwd_returns t
    ON f.LPERMNO = t.permno AND t.date >= CAST(f.event_date AS DATE)
ASOF JOIN market_returns m
    ON m.date >= CAST(f.event_date AS DATE)
WHERE t.ret_1y IS NOT NULL
""")

print("Exporting...")
con.execute("COPY y_train TO 'y_train.csv.gz' (FORMAT CSV, HEADER true, COMPRESSION gzip);")
print("Done — y_train.csv.gz created.")

print(con.execute("SELECT * FROM y_train LIMIT 5").df())
print(con.execute("SELECT COUNT(*) FROM y_train").fetchone()[0])

con.execute("""
CREATE TABLE training_data AS
SELECT DISTINCT *
FROM X_train x
JOIN y_train y
    ON x.gvkey = y.gvkey
    AND x.LPERMNO = y.LPERMNO
    AND x.event_date = y.event_date
""")

print(con.execute("SELECT COUNT(*) FROM training_data").fetchone()[0])
print(con.execute("SELECT * FROM training_data LIMIT 5").df())

con.execute("""
COPY training_data TO 'training_data.csv.gz' (FORMAT CSV, HEADER true, COMPRESSION gzip);
""")
print("Done — training_data.csv.gz created.")