import sqlite3

# Create SQLite connection to a Database
connection = sqlite3.connect("database.db")

# Set Database tables
with open("schema.sql") as f:
    connection.executescript(f.read())

# Create a cursor object to interact with the database
cur = connection.cursor()

# Commit the transaction
connection.commit()

# Close the connection
connection.close()