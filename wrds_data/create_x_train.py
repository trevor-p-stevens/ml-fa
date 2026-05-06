import duckdb

con = duckdb.connect("ml-fa.duckdb")
con.execute("SET memory_limit='4GB';")
con.execute("SET threads=4;")

print("Loading data...")
con.execute("DROP TABLE IF EXISTS X_fundq;")
con.execute("CREATE TABLE X_fundq AS SELECT * FROM read_csv_auto('wrds_data/X_fundq.csv.gz');")

con.execute("DROP TABLE IF EXISTS ccm;")
con.execute("CREATE TABLE ccm AS SELECT * FROM read_csv_auto('wrds_data/merged.gz');")

con.execute("DROP TABLE IF EXISTS X_technical;")
con.execute("CREATE TABLE X_technical AS SELECT * FROM read_csv_auto('wrds_data/X_technical.csv.gz');")

print("Merging and deduplicating...")
con.execute("DROP TABLE IF EXISTS X_fundq_ccm;")
con.execute("""
CREATE TABLE X_fundq_ccm AS
SELECT DISTINCT ON (gvkey, datadate, lpermno) f.*, c.lpermno, c.linkdt_clean AS linkdt, c.linkenddt_clean AS linkenddt
FROM X_fundq f
LEFT JOIN (
    SELECT *,
           try_cast(linkdt AS DATE) AS linkdt_clean,
           try_cast(linkenddt AS DATE) AS linkenddt_clean
    FROM ccm
    WHERE try_cast(linkdt AS DATE) IS NOT NULL
       OR try_cast(linkenddt AS DATE) IS NOT NULL
) c ON f.gvkey = c.gvkey
WHERE CAST(f.event_date AS DATE) BETWEEN c.linkdt_clean AND COALESCE(c.linkenddt_clean, CURRENT_DATE)
ORDER BY lpermno, event_date;
""")

print("ASOF joining technical data...")
con.execute("DROP TABLE IF EXISTS X_train;")
con.execute("""
CREATE TABLE X_train AS
SELECT f.*, t.* EXCLUDE (permno, date)
FROM X_fundq_ccm f
ASOF JOIN (SELECT *, -epoch(date) AS neg_date FROM X_technical ORDER BY permno, neg_date) t
    ON f.lpermno = t.permno
   AND -epoch(CAST(f.event_date AS DATE)) >= t.neg_date;
""")

print("Exporting...")
con.execute("COPY X_train TO 'X_train.csv.gz' (FORMAT CSV, HEADER true, COMPRESSION gzip);")
print("Done — X_train.csv.gz created.")