import sqlite3
import random
from datetime import datetime, timedelta
import os

# Connect to SQLite
connection = sqlite3.connect("comprehensive_student.db")
cursor = connection.cursor()

# Create a comprehensive student table
cursor.execute("""
CREATE TABLE IF NOT EXISTS STUDENT (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FIRST_NAME VARCHAR(25),
    LAST_NAME VARCHAR(25),
    DATE_OF_BIRTH DATE,
    GENDER VARCHAR(10),
    EMAIL VARCHAR(50),
    PHONE VARCHAR(15),
    ADDRESS VARCHAR(100),
    CITY VARCHAR(30),
    STATE VARCHAR(20),
    COUNTRY VARCHAR(20),
    MAJOR VARCHAR(30),
    ADMISSION_DATE DATE,
    GPA FLOAT,
    CREDITS_EARNED INT,
    EXPECTED_GRADUATION DATE,
    SCHOLARSHIP_AMOUNT FLOAT,
    EXTRACURRICULAR_ACTIVITIES TEXT,
    INTERNSHIP_COMPANY VARCHAR(50),
    INTERNSHIP_POSITION VARCHAR(30),
    INTERNSHIP_START_DATE DATE,
    INTERNSHIP_END_DATE DATE
);
""")

print("Table created successfully.")

# Check if the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

# Function to generate random dates
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())))

# List of sample data
first_names = ['John', 'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason', 'Isabella']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
genders = ['M', 'F']
majors = ['Computer Science', 'Business Administration', 'Mechanical Engineering', 'Psychology', 'Biology']
cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA']
countries = ['USA'] * 10
extracurriculars = ['Student Council', 'Debate Team', 'Chess Club', 'Basketball Team', 'Volunteer Society']
companies = ['Google', 'Microsoft', 'Amazon', 'Apple', 'Facebook', 'IBM', 'Intel', 'Cisco', 'Oracle', 'Adobe']
positions = ['Software Engineer Intern', 'Data Analyst Intern', 'Marketing Intern', 'Research Assistant', 'Product Manager Intern']

# Generate 1000 student records
students = []
for i in range(1000):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    dob = random_date(datetime(1990, 1, 1), datetime(2003, 12, 31))
    admission_date = random_date(datetime(2018, 1, 1), datetime(2023, 12, 31))
    expected_graduation = admission_date + timedelta(days=1460)  # roughly 4 years
    internship_start = random_date(admission_date, expected_graduation)
    internship_end = internship_start + timedelta(days=90)  # 3-month internship

    students.append((
        first_name,
        last_name,
        dob.strftime('%Y-%m-%d'),   #major 
        random.choice(genders),
        f"{first_name.lower()}.{last_name.lower()}@example.com",
        f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        f"{random.randint(100,9999)} Main St",
        random.choice(cities),
        random.choice(states),
        random.choice(countries),
        random.choice(majors),
        admission_date.strftime('%Y-%m-%d'),
        round(random.uniform(2.0, 4.0), 2),
        random.randint(0, 120),
        expected_graduation.strftime('%Y-%m-%d'),
        round(random.uniform(0, 50000), 2),
        ', '.join(random.sample(extracurriculars, random.randint(1, 3))),
        random.choice(companies),
        random.choice(positions),
        internship_start.strftime('%Y-%m-%d'),
        internship_end.strftime('%Y-%m-%d')
    ))

# Insert the student records
cursor.executemany("""
INSERT INTO STUDENT (
    FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, GENDER, EMAIL, PHONE, ADDRESS, CITY, STATE, COUNTRY,
    MAJOR, ADMISSION_DATE, GPA, CREDITS_EARNED, EXPECTED_GRADUATION, SCHOLARSHIP_AMOUNT,
    EXTRACURRICULAR_ACTIVITIES, INTERNSHIP_COMPANY, INTERNSHIP_POSITION, INTERNSHIP_START_DATE, INTERNSHIP_END_DATE
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", students)

print(f"{len(students)} records generated and inserted successfully.")

# Display a subset of the inserted records
data = cursor.execute('SELECT * FROM STUDENT').fetchall()

print("The first 10 inserted records are:")
for row in data[:10]:
    print(row)

# Commit changes and close connection
connection.commit()
connection.close()

print("Comprehensive student database created successfully with 1000 records.")

def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"An error occurred while executing the SQL query: {str(e)}")  # Log the error
        return None
    finally:
        conn.close()  # Ensure the connection is closed
