import sqlite3
import pandas as pd
from tabulate import tabulate

try:
    conn = sqlite3.connect("movies.db") # specify directory to sqlite db.
except sqlite3.Error as e:
    print(f"Error connecting to SQLite3 database: {e}")

df = pd.read_sql_query("SELECT date, movie_title, IMDb_rating, tomatometer, featured_user_review FROM amc_movies WHERE date = (SELECT MAX(date) FROM amc_movies);", conn)
print(tabulate(df, headers='keys', tablefmt='fancy_grid'))
