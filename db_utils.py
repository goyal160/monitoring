# db_utils.py
import sqlite3
import pandas as pd

DB_PATH = "noc_dashboard.db"

# Connect to the SQLite database
def get_connection():
    return sqlite3.connect(DB_PATH)

# Load all data from the database
def load_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM noc_data", conn)
    conn.close()
    return df

# Update NOC status for a specific area
def update_noc_status(area_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE noc_data
        SET `NOC Status` = 'Received'
        WHERE Area = ?
    """, (area_name,))
    conn.commit()
    conn.close()

# Load data filtered by type of crossing
def get_data_by_crossing_type(crossing_type):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM noc_data WHERE `Type of Crossing` = ?", conn, params=(crossing_type,))
    conn.close()
    return df

# Load data filtered by district
def get_data_by_district(district):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM noc_data WHERE District = ?", conn, params=(district,))
    conn.close()
    return df
