# fix_admin_status.py

"""
This script is responsible for fixing the blocked admin user status in the PostgreSQL database.

Usage:
Run this script to update the blocked admin status.
"""

import psycopg2
import os

# Database connection settings
HOST = os.getenv('DB_HOST')
DATABASE = os.getenv('DB_NAME')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')

try:
    # Establish a database connection
    connection = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )

    cursor = connection.cursor()

    # SQL query to fix the blocked admin status
    update_query = """
    UPDATE users
    SET status = 'active'
    WHERE username = 'admin' AND status = 'blocked';
    """
    cursor.execute(update_query)

    # Commit the changes
    connection.commit()
    print("Blocked admin user status updated successfully.")

except Exception as e:
    print(f"Error updating admin status: {e}")

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()