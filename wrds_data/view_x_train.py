import duckdb

# Connect to DuckDB and query the CSV directly
con = duckdb.connect()
# Get the number of rows
length = con.execute("SELECT COUNT(*) FROM 'wrds_data/X_train.csv.gz'").fetchone()[0]
print(f"Number of rows: {length}")

# View event_date and neg_date for the first few rows
result = con.execute("SELECT event_date, neg_date FROM 'wrds_data/X_train.csv.gz' LIMIT 5").fetchdf()
print(result)

result = con.execute("""
SELECT 
    event_date,
    neg_date,
    epoch_ms(CAST(-neg_date * 1000 AS BIGINT)) AS date_converted_back,
    epoch_ms(CAST(-neg_date * 1000 AS BIGINT)) - CAST(event_date AS DATE) AS days_after
FROM 'wrds_data/X_train.csv.gz'
LIMIT 10;
""").df()
print(result)

con = duckdb.connect("ml-fa.duckdb")

# Get column names first
cols = con.execute("DESCRIBE X_train").df()["column_name"].tolist()
print(cols)
total = con.execute("SELECT COUNT(*) FROM X_train").fetchone()[0]

null_counts = con.execute(f"""
SELECT {', '.join([f'COUNT(*) FILTER (WHERE "{c}" IS NULL) AS "{c}"' for c in cols])}
FROM X_train
""").df()

null_summary = null_counts.T.rename(columns={0: 'null_count'})
null_summary['null_pct'] = (null_summary['null_count'] / total * 100).round(1)
null_summary = null_summary.sort_values('null_count', ascending=False)
print(null_summary[null_summary['null_count'] > 0])
print(con.execute("SELECT DISTINCT permno FROM X_technical WHERE permno = 93436").df())
# Build WHERE clause dynamically
# not_null_conditions = " AND ".join([f'"{c}" IS NOT NULL' for c in cols])
# total = con.execute("SELECT COUNT(*) FROM X_train").fetchone()[0]
# clean = con.execute(f"SELECT COUNT(*) FROM X_train WHERE {not_null_conditions}").fetchone()[0]
# print(f"Dropping {total - clean} rows ({100*(total-clean)/total:.1f}%), keeping {clean}")
# con.execute(f"""
# COPY (
#     SELECT * FROM X_train
#     WHERE {not_null_conditions}
# ) TO 'wrds_data/X_train_no_nulls.csv.gz' (FORMAT CSV, HEADER true, COMPRESSION gzip);
# """)
