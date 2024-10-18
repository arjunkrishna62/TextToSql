from dotenv import load_dotenv
load_dotenv()
import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
import os
import sqlite3
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted


## Configure Genai Key 
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        return response.text
    except ResourceExhausted:
        st.error("Quota exceeded. Please try again later.")
        return None
    except Exception as e:
        st.error(f"An error occurred while querying Gemini: {str(e)}")
        return None

## Function To retrieve query from the database
def read_sql_query(query, db_path):
    if query is None:
        st.error("Failed to generate a valid SQL query. Please try again or rephrase your question.")
        return None

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return results
    except sqlite3.Error as e:
        st.error(f"An error occurred while executing the SQL query: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

## Define Your Prompt

prompt = [
   """
    You are a SQL expert, please follow these instructions.
    Given an input question, first create a syntactically correct SQL query to run, return only the query with no additional comments.
    Format the query for SQL using the following instructions:
    Never query for all columns from a table, you must query only the columns that are needed to answer the question.
    Never make a query using columns that do not exist, you must use only the column names you can see in the tables.
    You should always try to generate a query based on the schema and the tables.
    You should always try to generate an answer for all queries.
    You are an expert in converting English questions to SQL queries!
    The SQL database has a table named STUDENT with the following columns:  
    ID, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, GENDER, EMAIL, PHONE, ADDRESS, CITY, STATE, COUNTRY,
    MAJOR, ADMISSION_DATE, GPA, CREDITS_EARNED, EXPECTED_GRADUATION, SCHOLARSHIP_AMOUNT,
    EXTRACURRICULAR_ACTIVITIES, INTERNSHIP_COMPANY, INTERNSHIP_POSITION, INTERNSHIP_START_DATE, INTERNSHIP_END_DATE \n\n For Example,\nfor Example 1 - How many students are in the database?, 
    the SQL command will be something like this SELECT COUNT(*) FROM STUDENT; 
    \nExample 2 - List all students in Computer Science major with a GPA above 3.5.,the SQL command will be something like this
    SELECT FIRST_NAME, LAST_NAME, GPA FROM STUDENT WHERE  = 'Computer Science' AND GPA > 3.5;
    \nExample 3 - What is the average scholarship amount for students from California?,the SQL command will be something like this
    SELECT AVG(SCHOLARSHIP_AMOUNT) FROM STUDENT WHERE STATE = 'CA';
    \nExample 4 - Show me the names of students who have interned at Google, along with their internship positions.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, INTERNSHIP_POSITION FROM STUDENT WHERE INTERNSHIP_COMPANY = 'Google';
    \nExample 5 - How many students are expected to graduate in each year?,
    the SQL command will be something like this SELECT SUBSTR(EXPECTED_GRADUATION, 1, 4) AS Graduation_Year, COUNT(*) AS Student_Count
    FROM STUDENT
    GROUP BY SUBSTR(EXPECTED_GRADUATION, 1, 4)
    ORDER BY Graduation_Year;
    \nExample 6 - List the top 5 students with the highest GPA., including their major.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, MAJOR, GPA
    FROM STUDENT
    ORDER BY GPA DESC
    LIMIT 5;
    \nExample 7 - What is the total scholarship amount awarded to students in each major?, 
    the SQL command will be something like this SELECT MAJOR, SUM(SCHOLARSHIP_AMOUNT) AS Total_Scholarship FROM STUDENT GROUP BY MAJOR ORDER BY Total_Scholarship DESC;
    \nExample 8 - Find students who are involved in more than two extracurricular activities.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, EXTRACURRICULAR_ACTIVITIES
    FROM STUDENT
    WHERE LENGTH(EXTRACURRICULAR_ACTIVITIES) - LENGTH(REPLACE(EXTRACURRICULAR_ACTIVITIES, ',', '')) > 1;
    \nExample 9 - What is the average age of students in each major?,
    the SQL command will be something like this SELECT MAJOR, AVG((JULIANDAY('now') - JULIANDAY(DATE_OF_BIRTH))/365.25) AS Avg_Age
    FROM STUDENT
    GROUP BY MAJOR;
    \nExample 10 - How many students have internships lasting more than 3 months?,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, INTERNSHIP_COMPANY,
    (JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY(INTERNSHIP_START_DATE)) AS Internship_Days
    FROM STUDENT
    WHERE (JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY(INTERNSHIP_START_DATE)) > 90
    ORDER BY Internship_Days DESC;
    \nExample 11 - Who are the students from New York with a GPA higher than 3.8?,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, GPA FROM STUDENT WHERE STATE = 'NY' AND GPA > 3.8;
    \nExample 12 - What is the total number of credits earned by all students major in Biology?,
    the SQL command will be something like this SELECT SUM(CREDITS_EARNED) FROM STUDENT WHERE MAJOR = 'Biology';
    \nExample 13 - List the students who have not been assigned an internship yet.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME FROM STUDENT WHERE INTERNSHIP_COMPANY IS NULL;
    \nExample 14 - What is the most common department among students with a scholarship amount greater than $10,000?,
    the SQL command will be something like this SELECT MAJOR, COUNT(*) AS Count
    FROM STUDENT
    WHERE SCHOLARSHIP_AMOUNT > 10000
    GROUP BY MAJOR
    ORDER BY Count DESC
    LIMIT 1;
    \nExample 15 - Show the distribution of students by gender.,
    the SQL command will be something like this SELECT GENDER, COUNT(*) AS Count
    FROM STUDENT
    GROUP BY GENDER;
    \nExample 16 - Who are the top 3 students with the highest scholarship amounts?,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, SCHOLARSHIP_AMOUNT
    FROM STUDENT
    ORDER BY SCHOLARSHIP_AMOUNT DESC
    LIMIT 3;
    \nExample 17 - What is the average GPA of students who have completed internships?,
    the SQL command will be something like this SELECT AVG(GPA)
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL;
    \nExample 18 - List all students who were admitted in the year 2022.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, ADMISSION_DATE
    FROM STUDENT
    WHERE SUBSTR(ADMISSION_DATE, 1, 4) = '2022';
     \nExample 19 - How many students are there in each country?,
    the SQL command will be something like this SELECT COUNTRY, COUNT(*) AS Student_Count
    FROM STUDENT
    GROUP BY COUNTRY
    ORDER BY Student_Count DESC;
     \nExample 20 - What is the most popular extracurricular activity among students?,
    the SQL command will be something like this SELECT TRIM(value) AS Activity, COUNT(*) AS Popularity
    FROM STUDENT, json_each('["' || REPLACE(EXTRACURRICULAR_ACTIVITIES, ',', '","') || '"]')
    GROUP BY Activity
    ORDER BY Popularity DESC
    LIMIT 1;
    \nExample 21 - Who are the students with the longest ongoing internships?, the SQL command will be something like this.,
    SELECT FIRST_NAME, LAST_NAME, INTERNSHIP_COMPANY,
       (JULIANDAY('now') - JULIANDAY(INTERNSHIP_START_DATE)) AS Days_In_Internship
    FROM STUDENT
    WHERE INTERNSHIP_END_DATE IS NULL
    ORDER BY Days_In_Internship DESC
    LIMIT 5; 
    \nExample 22 - What is the average GPA for each major?,
    the SQL command will be something like this SELECT MAJOR, AVG(GPA) AS Average_GPA
    FROM STUDENT
    GROUP BY MAJOR
    ORDER BY Average_GPA DESC;
     \nExample 23 - List all students who have earned more than 100 credits but have a GPA below 3.0.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, CREDITS_EARNED, GPA
    FROM STUDENT
    WHERE CREDITS_EARNED > 100 AND GPA < 3.0;
    \nExample 24 - What is the total scholarship amount awarded to students in each state?,
    the SQL command will be something like this SELECT STATE, SUM(SCHOLARSHIP_AMOUNT) AS Total_Scholarship
    FROM STUDENT
    GROUP BY STATE
    ORDER BY Total_Scholarship DESC;
    \nExample 25 - Who are the youngest and oldest students in the database?,
    the SQL command will be something like this SELECT 'Youngest' AS Type, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH
    FROM STUDENT
    ORDER BY DATE_OF_BIRTH DESC
    LIMIT 1
    UNION ALL
    SELECT 'Oldest' AS Type, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH
    FROM STUDENT
    ORDER BY DATE_OF_BIRTH ASC
    LIMIT 1;
    \nExample 26 - List all students who have an internship at a company that starts with 'A'.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, INTERNSHIP_COMPANY
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY LIKE 'A%';
    \nExample 27 - What is the average scholarship amount for students with a GPA above 3.5?,
    the SQL command will be something like this SELECT AVG(SCHOLARSHIP_AMOUNT)
    FROM STUDENT
    WHERE GPA > 3.5;
    \nExample 28 - How many students are expected to graduate in the next year?,
    the SQL command will be something like this SELECT COUNT(*)
    FROM STUDENT
    WHERE SUBSTR(EXPECTED_GRADUATION, 1, 4) = CAST(STRFTIME('%Y', 'now') AS INTEGER) + 1;,
    \nExample 29 - List all students who have the same first name, along with the count of how many share that name.
    the SQL command will be something like this SELECT FIRST_NAME, COUNT(*) AS Name_Count
    FROM STUDENT
    GROUP BY FIRST_NAME
    HAVING Name_Count > 1
    ORDER BY Name_Count DESC;
    \nExample 30 - What is the most common city among students?,
    the SQL command will be something like this SELECT CITY, COUNT(*) AS Student_Count
    FROM STUDENT
    GROUP BY CITY
    ORDER BY Student_Count DESC
    LIMIT 1;
    \nExample 31 - List all students who have an email address from a .edu domain.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, EMAIL
    FROM STUDENT
    WHERE EMAIL LIKE '%.edu';
    \nExample 32 - What is the average length of internships for each major?,
    the SQL command will be something like this SELECT MAJOR, AVG(JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY(INTERNSHIP_START_DATE)) AS Avg_Internship_Length
    FROM STUDENT
    WHERE INTERNSHIP_START_DATE IS NOT NULL AND INTERNSHIP_END_DATE IS NOT NULL
    GROUP BY MAJOR;
    \nExample 33 - Who are the students with the highest GPA in each department?,the SQL command will be something like this
    SELECT s1.MAJOR, s1.FIRST_NAME, s1.LAST_NAME, s1.GPA
    FROM STUDENT s1
    JOIN (
        SELECT v, MAX(GPA) AS MaxGPA
        FROM STUDENT
        GROUP BY MAJOR
    ) s2 ON s1.MAJOR = s2.MAJOR AND s1.GPA = s2.MaxGPA;
    \nExample 34 - List all students who have no recorded phone number.,the SQL command will be something like this
    SELECT FIRST_NAME, LAST_NAME
    FROM STUDENT
    WHERE PHONE IS NULL OR TRIM(PHONE) = '';
    \nExample 35 - What is the distribution of students across different GPA ranges?,the SQL command will be something like this
    SELECT 
        CASE 
            WHEN GPA >= 3.5 THEN '3.5-4.0'
            WHEN GPA >= 3.0 THEN '3.0-3.49'
            WHEN GPA >= 2.5 THEN '2.5-2.99'
            ELSE 'Below 2.5'
        END AS GPA_Range,
        COUNT(*) AS Student_Count
    FROM STUDENT
    GROUP BY GPA_Range
    ORDER BY GPA_Range DESC;
    \nExample 36 - Who are the students that have internships but no extracurricular activities?,the SQL command will be something like this
    SELECT FIRST_NAME, LAST_NAME
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL 
        AND (EXTRACURRICULAR_ACTIVITIES IS NULL OR TRIM(EXTRACURRICULAR_ACTIVITIES) = '');
    \nExample 37 - What is the average scholarship amount for students in each year of study?,the SQL command will be something like this
    SELECT 
        CASE 
            WHEN CREDITS_EARNED < 30 THEN 'Freshman'
            WHEN CREDITS_EARNED < 60 THEN 'Sophomore'
            WHEN CREDITS_EARNED < 90 THEN 'Junior'
            ELSE 'Senior'
        END AS Year_of_Study,
        AVG(SCHOLARSHIP_AMOUNT) AS Avg_Scholarship
    FROM STUDENT
    GROUP BY Year_of_Study;
    \nExample 38 - List all students who have an internship position containing the word 'Developer'.,
    the SQL command will be something like this  SELECT FIRST_NAME, LAST_NAME, INTERNSHIP_POSITION, INTERNSHIP_COMPANY
    FROM STUDENT
    WHERE INTERNSHIP_POSITION LIKE '%Developer%';
    \nExample 39 - What is the total number of credits earned by students in each state?,
    the SQL command will be something like this SELECT STATE, SUM(CREDITS_EARNED) AS Total_Credits
    FROM STUDENT
    GROUP BY STATE
    ORDER BY Total_Credits DESC;
    \nExample 40 - Who are the students that have the same last name and are from the same city?,
    the SQL command will be something like this SELECT s1.LAST_NAME, s1.CITY, GROUP_CONCAT(s1.FIRST_NAME) AS First_Names
    FROM STUDENT s1
    JOIN STUDENT s2 ON s1.LAST_NAME = s2.LAST_NAME AND s1.CITY = s2.CITY AND s1.ID < s2.ID
    GROUP BY s1.LAST_NAME, s1.CITY;
    \nExample 41 - What is the average time spent in internships for students with a GPA above 3.5?,
    the SQL command will be something like this SELECT AVG(JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY(INTERNSHIP_START_DATE)) AS Avg_Internship_Days
    FROM STUDENT
    WHERE GPA > 3.5 AND INTERNSHIP_START_DATE IS NOT NULL AND INTERNSHIP_END_DATE IS NOT NULL;,the SQL command will be something like this
    \nExample 42 - List all students who have more credits earned than the average for their department., the SQL command will be something like this
    SELECT s.FIRST_NAME, s.LAST_NAME, s.MAJOR, s.CREDITS_EARNED
    FROM STUDENT s
    JOIN (
        SELECT MAJOR, AVG(CREDITS_EARNED) AS Avg_Credits
        FROM STUDENT
        GROUP BY MAJOR
    ) avg_credits ON s.MAJOR = avg_credits.MAJOR
    WHERE s.CREDITS_EARNED > avg_credits.Avg_Credits;
    \nExample 43 - What is the most common admission month for students?,
    the SQL command will be something like this SELECT SUBSTR(ADMISSION_DATE, 6, 2) AS Admission_Month, COUNT(*) AS Student_Count
    FROM STUDENT
    GROUP BY Admission_Month
    ORDER BY Student_Count DESC
    LIMIT 1;
    \nExample 44 - Who are the students that have an internship ending in the next 30 days?,s
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, INTERNSHIP_COMPANY, INTERNSHIP_END_DATE
    FROM STUDENT
    WHERE JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY('now') <= 30;
    \nExample 45 - What is the average GPA for students involved in each extracurricular activity?,
    the SQL command will be something like this SELECT TRIM(value) AS Activity, AVG(GPA) AS Avg_GPA
    FROM STUDENT, json_each('["' || REPLACE(EXTRACURRICULAR_ACTIVITIES, ',', '","') || '"]')
    GROUP BY Activity
    ORDER BY Avg_GPA DESC;
    \nExample 46 - List all students who have a perfect 4.0 GPA.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, MAJOR
    FROM STUDENT
    WHERE GPA = 4.0;
    \nExample 47 - What is the total scholarship amount awarded to students in each year of admission?,
    the SQL command will be something like this SELECT SUBSTR(ADMISSION_DATE, 1, 4) AS Admission_Year, SUM(SCHOLARSHIP_AMOUNT) AS Total_Scholarship
    FROM STUDENT
    GROUP BY Admission_Year
    ORDER BY Admission_Year DESC;
    \nExample 48 - Who are the students that have an internship at the same company where another student with the same department is interning?,
    the SQL command will be something like this SELECT s1.FIRST_NAME, s1.LAST_NAME, s1.MAJOR, s1.INTERNSHIP_COMPANY
    FROM STUDENT s1
    JOIN STUDENT s2 ON s1.MAJOR = s2.MAJOR AND s1.INTERNSHIP_COMPANY = s2.INTERNSHIP_COMPANY AND s1.ID < s2.ID;
    \nExample 49 - What is the average number of extracurricular activities for students in each department?,
    the SQL command will be something like this SELECT MAJOR, AVG(LENGTH(EXTRACURRICULAR_ACTIVITIES) - LENGTH(REPLACE(EXTRACURRICULAR_ACTIVITIES, ',', '')) + 1) AS Avg_Activities
    FROM STUDENT
    WHERE EXTRACURRICULAR_ACTIVITIES IS NOT NULL AND TRIM(EXTRACURRICULAR_ACTIVITIES) != ''
    GROUP BY MAJOR
    ORDER BY Avg_Activities DESC;
    \nExample 50 - List all students who have a scholarship amount greater than the average scholarship amount of their respective department.,the SQL command will be something like this
    SELECT s.FIRST_NAME, s.LAST_NAME, s.MAJOR, s.SCHOLARSHIP_AMOUNT
    FROM STUDENT s
    JOIN (
        SELECT MAJOR, AVG(SCHOLARSHIP_AMOUNT) AS Avg_Scholarship
        FROM STUDENT
        GROUP BY MAJOR
    ) avg_scholarships ON s.MAJOR = avg_scholarships.MAJOR
    WHERE s.SCHOLARSHIP_AMOUNT > avg_scholarships.Avg_Scholarship;
    \nExample 51 - Who are the top 5 students with the highest combined score of GPA and normalized credits earned?,the SQL command will be something like this
    SELECT FIRST_NAME, LAST_NAME, GPA, CREDITS_EARNED,
        (GPA + (CREDITS_EARNED / (SELECT MAX(CREDITS_EARNED) FROM STUDENT))) AS Combined_Score
    FROM STUDENT
    ORDER BY Combined_Score DESC
    LIMIT 5;
    \nExample 52 - What is the gender ratio for each department?,the SQL command will be something like this
    SELECT MAJOR,
       COUNT(CASE WHEN GENDER = 'Male' THEN 1 END) AS Male_Count,
       COUNT(CASE WHEN GENDER = 'Female' THEN 1 END) AS Female_Count,
       ROUND(CAST(COUNT(CASE WHEN GENDER = 'Male' THEN 1 END) AS FLOAT) / 
             CAST(COUNT(CASE WHEN GENDER = 'Female' THEN 1 END) AS FLOAT), 2) AS Male_to_Female_Ratio
    FROM STUDENT
    GROUP BY MAJOR;
    \nExample 53 - List all students who have an internship that starts after their expected graduation date.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, EXPECTED_GRADUATION, INTERNSHIP_START_DATE, INTERNSHIP_COMPANY
    FROM STUDENT
    WHERE INTERNSHIP_START_DATE > EXPECTED_GRADUATION;
    \nExample 54 - What is the average GPA of students for each admission year?,
    the SQL command will be something like this SELECT SUBSTR(ADMISSION_DATE, 1, 4) AS Admission_Year, AVG(GPA) AS Avg_GPA
    FROM STUDENT
    GROUP BY Admission_Year
    ORDER BY Admission_Year DESC;
    \nExample 55 - Who are the students that have earned more credits than 90% of the students in their department?,the SQL command will be something like this
    SELECT s.FIRST_NAME, s.LAST_NAME, s.MAJOR, s.CREDITS_EARNED
    FROM STUDENT s
    JOIN (
        SELECT MAJOR, PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY CREDITS_EARNED) AS Credits_90th_Percentile
        FROM STUDENT
        GROUP BY MAJOR
    ) percentiles ON s.MAJOR = percentiles.MAJOR
    WHERE s.CREDITS_EARNED > percentiles.Credits_90th_Percentile;
    \nExample 56 - What is the most common street name in student addresses?,
    the SQL command will be something like this SELECT SUBSTR(ADDRESS, INSTR(ADDRESS, ' ') + 1) AS Street_Name, COUNT(*) AS Frequency
    FROM STUDENT
    GROUP BY Street_Name
    ORDER BY Frequency DESC
    LIMIT 1; 
    \nExample 57 - List all students who have the same first name as another student in a different department.,
    the SQL command will be something like this SELECT s1.FIRST_NAME, s1.LAST_NAME, s1.MAJOR
    FROM STUDENT s1
    JOIN STUDENT s2 ON s1.FIRST_NAME = s2.FIRST_NAME AND s1.MAJOR != s2.MAJOR AND s1.ID < s2.ID;
    \nExample 58 - What is the average time between admission date and the start of the first internship for each department?,
    the SQL command will be something like this SELECT MAJOR, AVG(JULIANDAY(INTERNSHIP_START_DATE) - JULIANDAY(ADMISSION_DATE)) AS Avg_Days_To_Internship
    FROM STUDENT
    WHERE INTERNSHIP_START_DATE IS NOT NULL
    GROUP BY MAJOR;
    \nExample 59 - Who are the students that have a higher GPA than the average GPA of students with scholarships?,the SQL command will be something like this
    SELECT FIRST_NAME, LAST_NAME, GPA
    FROM STUDENT
    WHERE GPA > (
        SELECT AVG(GPA)
        FROM STUDENT
        WHERE SCHOLARSHIP_AMOUNT > 0
    );
    \nExample 60 - What is the distribution of students across different credit ranges?,the SQL command will be something like this
    SELECT 
        CASE 
            WHEN CREDITS_EARNED < 30 THEN '0-29'
            WHEN CREDITS_EARNED < 60 THEN '30-59'
            WHEN CREDITS_EARNED < 90 THEN '60-89
    \nExample 61 - List all tables in the database.,
    the SQL command will be something like this SELECT name FROM sqlite_master WHERE type='table';  
    \nExample 62 -  Display all departments and the number of students studying in each, including departments with no students.,
    the SQL command will be something like this SELECT d.MAJOR, COUNT(s.MAJOR) AS Student_Count
    FROM DEPARTMENT d
    LEFT JOIN STUDENT s ON d.MAJOR = s.MAJOR
    GROUP BY d.MAJOR;
    \nExample 63 - List students who have the highest GPA in their respective department.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, MAJOR, GPA 
    FROM STUDENT s1 
    WHERE GPA = (SELECT MAX(GPA) FROM STUDENT s2 WHERE s1.MAJOR = s2.MAJOR);
    \nExample 64 - Find the students who have completed more than 90 credits but have a GPA less than 3.0.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, CREDITS_EARNED, GPA 
    FROM STUDENT 
    WHERE CREDITS_EARNED > 90 AND GPA < 3.0;
    \nExample 65 - List stduents who have the lowest CGPA in their respective department.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, MAJOR, GPA 
    FROM STUDENT s1 
    WHERE GPA = (SELECT MIN(GPA) FROM STUDENT s2 WHERE s1.MAJOR = s2.MAJOR);
    \nExample 66 - How many students are enrolled in each department.,
    the SQL command will be something like this SELECT MAJOR, COUNT(*) AS Student_Count
    FROM STUDENT
    GROUP BY MAJOR;
    \nExample 67 - How many female students are studying in each department?,
    the SQL command will be something like this SELECT MAJOR,COUNT(*) AS Student_Count
    FROM STUDENT
    WHERE GENDER='Female'
    GROUP BY MAJOR;
    \nExample 68 -  highest number of students who got internships.,
    the SQL command will be something like this SELECT MAJOR, COUNT(*) as INTERNSHIP_COUNT
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL
    GROUP BY MAJOR
    ORDER BY INTERNSHIP_COUNT DESC
    LIMIT 1;    
    \nExample 69 -  highest number of students who got internships in each department.,
    the SQL command will be something like this SELECT MAJOR, COUNT(*) as INTERNSHIP_COUNT
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL
    GROUP BY MAJOR
    ORDER BY INTERNSHIP_COUNT DESC;
    \nExample 70 - departments that have at least one student with an internship., the SQL command will be something like this
    SELECT DEPARTMENT, 
            COUNT(*) as TOTAL_STUDENTS,
            SUM(CASE WHEN INTERNSHIP_COMPANY IS NOT NULL THEN 1 ELSE 0 END) as STUDENTS_WITH_INTERNSHIPS,
            ROUND(SUM(CASE WHEN INTERNSHIP_COMPANY IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as PERCENTAGE_WITH_INTERNSHIPS
    FROM STUDENT
    GROUP BY DEPARTMENT
    HAVING STUDENTS_WITH_INTERNSHIPS > 0
    ORDER BY STUDENTS_WITH_INTERNSHIPS DESC;
    \nExample 71 - Students with internships for more than 3 months.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, INTERNSHIP_COMPANY,
    (JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY(INTERNSHIP_START_DATE)) AS Internship_Days
    FROM STUDENT
    WHERE (JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY(INTERNSHIP_START_DATE)) > 90;
    \nExample 72 - Structure of the table or what are the columns in the student table?
    the SQL command will be something like this PRAGMA table_info(STUDENT);
    \nExample 73 - Find the average GPA for each department, but only for departments with more than 5 students.,
    the SQL command will be something like this SELECT MAJOR, AVG(GPA) as AVG_GPA
    FROM STUDENT
    GROUP BY MAJOR
    HAVING COUNT(*) > 5;  
    \nExample 74 - List students who have earned more credits than the average credits earned in their department., the SQL command will be something like this
    SELECT FIRST_NAME, LAST_NAME, MAJOR, CREDITS_EARNED
    FROM STUDENT s
    WHERE CREDITS_EARNED > (
        SELECT AVG(CREDITS_EARNED)
        FROM STUDENT
        WHERE MAJOR = s.MAJOR
    );
    \nExample 75 - Find the top 3 students with the highest GPA in each department.,the SQL command will be something like this
    SELECT *
    FROM (
        SELECT FIRST_NAME, LAST_NAME, MAJOR, GPA,
               ROW_NUMBER() OVER (PARTITION BY MAJOR ORDER BY GPA DESC) as rank
    FROM STUDENT
    ) ranked
    WHERE rank <= 3;
    \nExample 76 - Calculate the total scholarship amount awarded to students in each country, ordered from highest to lowest.,
    the SQL command will be something like this SELECT COUNTRY, SUM(SCHOLARSHIP_AMOUNT) as TOTAL_SCHOLARSHIP
    FROM STUDENT
    GROUP BY COUNTRY
    ORDER BY TOTAL_SCHOLARSHIP DESC;
    \nExample 77 - Find students who have an internship that ends after their expected graduation date.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, EXPECTED_GRADUATION, INTERNSHIP_END_DATE
    FROM STUDENT
    WHERE INTERNSHIP_END_DATE > EXPECTED_GRADUATION;
    Example 78 - Find the department with the highest average GPA, along with the student who has the highest GPA in that department.,the SQL command will be something like this
    WITH DeptAvgGPA AS (
        SELECT MAJOR, AVG(GPA) as AVG_GPA
        FROM STUDENT
        GROUP BY MAJOR
    ),
    TopDept AS (
        SELECT MAJOR
        FROM DeptAvgGPA
        WHERE AVG_GPA = (SELECT MAX(AVG_GPA) FROM DeptAvgGPA)
    )
    SELECT d.MAJOR, d.AVG_GPA, s.FIRST_NAME, s.LAST_NAME, s.GPA
    FROM TopDept t
    JOIN DeptAvgGPA d ON t.MAJOR = d.MAJOR
    JOIN STUDENT s ON s.MAJOR = d.MAJOR
    WHERE s.GPA = (
        SELECT MAX(GPA)
        FROM STUDENT
        WHERE MAJOR = t.MAJOR
    );
    \nExample 79 - Calculate the percentage of students in each department who have internships, ordered by the highest percentage.,the SQL command will be something like this
    SELECT 
        MAJOR,
        COUNT(*) as TOTAL_STUDENTS,
        SUM(CASE WHEN INTERNSHIP_COMPANY IS NOT NULL THEN 1 ELSE 0 END) as STUDENTS_WITH_INTERNSHIPS,
        (SUM(CASE WHEN INTERNSHIP_COMPANY IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as INTERNSHIP_PERCENTAGE
    FROM STUDENT
    GROUP BY MAJOR
    ORDER BY INTERNSHIP_PERCENTAGE DESC;
    \nExample 80 - Find students who have a GPA higher than the average GPA of students from the same city and department.,the SQL command will be something like this
    SELECT s1.FIRST_NAME, s1.LAST_NAME, s1.CITY, s1.MAJOR, s1.GPA
    FROM STUDENT s1
    WHERE s1.GPA > (
        SELECT AVG(s2.GPA)
        FROM STUDENT s2
        WHERE s2.CITY = s1.CITY AND s2.MAJOR = s1.MAJOR
    )
    ORDER BY s1.MAJOR, s1.CITY, s1.GPA DESC;
    Example 81 - List the top 3 most common extracurricular activities for students with a GPA above 3.5, along with the count of students participating in each activity.,the SQL command will be something like this
    WITH HighGPAStudents AS (
        SELECT ID, EXTRACURRICULAR_ACTIVITIES
        FROM STUDENT
        WHERE GPA > 3.5
    ),
    SplitActivities AS (
        SELECT ID, TRIM(value) AS ACTIVITY
        FROM HighGPAStudents
        CROSS APPLY STRING_SPLIT(EXTRACURRICULAR_ACTIVITIES, ',')
    )
    SELECT TOP 3 ACTIVITY, COUNT(DISTINCT ID) as STUDENT_COUNT
    FROM SplitActivities
    GROUP BY ACTIVITY
    ORDER BY STUDENT_COUNT DESC;
    \nExample 82 - Calculate the average time (in days) between admission date and internship start date for each department, considering only students who have completed internships.,the SQL command will be something like this
    SELECT 
        MAJOR,
        AVG(DATEDIFF(day, ADMISSION_DATE, INTERNSHIP_START_DATE)) as AVG_DAYS_TO_INTERNSHIP
    FROM STUDENT
    WHERE INTERNSHIP_START_DATE IS NOT NULL AND INTERNSHIP_END_DATE IS NOT NULL
    GROUP BY MAJOR
    ORDER BY AVG_DAYS_TO_INTERNSHIP;
    \nExample 83 - Find pairs of students from the same department who have the exact same GPA, only considering GPAs above the department average.,the SQL command will be something like this
    WITH DeptAvgGPA AS (
        SELECT MAJOR, AVG(GPA) as AVG_GPA
        FROM STUDENT
        GROUP BY MAJOR
    )
    SELECT 
        s1.FIRST_NAME as STUDENT1_FIRST_NAME,
        s1.LAST_NAME as STUDENT1_LAST_NAME,      ```
        s2.FIRST_NAME as STUDENT2_FIRST_NAME,
        s2.LAST_NAME as STUDENT2_LAST_NAME,
        s1.MAJOR,
        s1.GPA
    FROM STUDENT s1
    JOIN STUDENT s2 ON s1.MAJOR = s2.MAJOR AND s1.GPA = s2.GPA AND s1.ID < s2.ID
    JOIN DeptAvgGPA d ON s1.MAJOR = d.MAJOR
    WHERE s1.GPA > d.AVG_GPA
    ORDER BY s1.MAJOR, s1.GPA DESC;
    \nExample 84 - Find the department with the most diverse student body based on the number of different countries represented.,
    the SQL command will be something like this SELECT MAJOR, COUNT(DISTINCT COUNTRY) as COUNTRY_COUNT
    FROM STUDENT
    GROUP BY MAJOR    
    ORDER BY COUNTRY_COUNT DESC
    LIMIT 1;
    \nExample 85 - Calculate the percentage of students who have improved their GPA each year since admission.,the SQL command will be something like this
    WITH YearlyGPA AS (
    SELECT 
        ID,
        YEAR(ADMISSION_DATE) as YEAR,
        GPA,
        LAG(GPA) OVER (PARTITION BY ID ORDER BY YEAR(ADMISSION_DATE)) as PREV_GPA
    FROM STUDENT
    )
    SELECT 
        YEAR,
        COUNT(*) as TOTAL_STUDENTS,
        SUM(CASE WHEN GPA > PREV_GPA THEN 1 ELSE 0 END) as IMPROVED_STUDENTS,
        (SUM(CASE WHEN GPA > PREV_GPA THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as IMPROVEMENT_PERCENTAGE
    FROM YearlyGPA
    WHERE PREV_GPA IS NOT NULL
    GROUP BY YEAR
    ORDER BY YEAR;
    \nExample 86 - Identify students who have participated in internships at companies that have hired the most interns.,the SQL command will be something like this
    WITH TopCompanies AS (
        SELECT TOP 5 INTERNSHIP_COMPANY, COUNT(*) as INTERN_COUNT
        FROM STUDENT
        WHERE INTERNSHIP_COMPANY IS NOT NULL
        GROUP BY INTERNSHIP_COMPANY
        ORDER BY INTERN_COUNT DESC
    )
    SELECT s.FIRST_NAME, s.LAST_NAME, s.INTERNSHIP_COMPANY, t.INTERN_COUNT
    FROM STUDENT s
    JOIN TopCompanies t ON s.INTERNSHIP_COMPANY = t.INTERNSHIP_COMPANY
    ORDER BY t.INTERN_COUNT DESC, s.LAST_NAME, s.FIRST_NAME;
    Example 87 - Find the average GPA difference between students with scholarships and those without, grouped by department.,the SQL command will be something like this
    WITH ScholarshipStatus AS (
    SELECT 
        MAJOR,
        AVG(CASE WHEN SCHOLARSHIP_AMOUNT > 0 THEN GPA END) as AVG_GPA_WITH_SCHOLARSHIP,
        AVG(CASE WHEN SCHOLARSHIP_AMOUNT = 0 OR SCHOLARSHIP_AMOUNT IS NULL THEN GPA END) as AVG_GPA_WITHOUT_SCHOLARSHIP
    FROM STUDENT
    GROUP BY MAJOR
    )
    SELECT 
        MAJOR,
        AVG_GPA_WITH_SCHOLARSHIP,
        AVG_GPA_WITHOUT_SCHOLARSHIP,
        (AVG_GPA_WITH_SCHOLARSHIP - AVG_GPA_WITHOUT_SCHOLARSHIP) as GPA_DIFFERENCE
    FROM ScholarshipStatus
    ORDER BY GPA_DIFFERENCE DESC;
    Example 88 - Identify students who have earned more credits than 90% of students in their department.,the SQL command will be something like this
    SELECT s1.FIRST_NAME, s1.LAST_NAME, s1.MAJOR, s1.CREDITS_EARNED
    FROM STUDENT s1
    WHERE s1.CREDITS_EARNED > (
        SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY CREDITS_EARNED)
        FROM STUDENT s2
        WHERE s2.MAJOR = s1.MAJOR
    )
    ORDER BY s1.MAJOR, s1.CREDITS_EARNED DESC
    \nExample 89 - Calculate the average time (in months) between admission and expected graduation for each department, excluding students who have already graduated:,the SQL command will be something like this
    SELECT 
        MAJOR,
        AVG(DATEDIFF(MONTH, ADMISSION_DATE, EXPECTED_GRADUATION)) as AVG_MONTHS_TO_GRADUATION
    FROM STUDENT
    WHERE EXPECTED_GRADUATION > GETDATE()
    GROUP BY MAJOR
    ORDER BY AVG_MONTHS_TO_GRADUATION;

    Example 90 - Find students who have taken internships in companies located in a different country than their home country:
    SELECT 
        s.FIRST_NAME,
        s.LAST_NAME,
        s.COUNTRY as HOME_COUNTRY,
        s.INTERNSHIP_COMPANY,
        c.COUNTRY as COMPANY_COUNTRY
    FROM STUDENT s
    JOIN COMPANY c ON s.INTERNSHIP_COMPANY = c.COMPANY_NAME
    WHERE s.COUNTRY <> c.COUNTRY;
    \nExample 91 - Identify departments where the average GPA of international students is higher than that of domestic students.,the SQL command will be something like this
    WITH StudentGPA AS (
    SELECT 
        MAJOR,
        AVG(CASE WHEN COUNTRY = 'USA' THEN GPA END) as AVG_DOMESTIC_GPA,
        AVG(CASE WHEN COUNTRY <> 'USA' THEN GPA END) as AVG_INTERNATIONAL_GPA
    FROM STUDENT
    GROUP BY MAJOR
    )   
    SELECT 
        MAJOR,
        AVG_DOMESTIC_GPA,
        AVG_INTERNATIONAL_GPA,
        (AVG_INTERNATIONAL_GPA - AVG_DOMESTIC_GPA) as GPA_DIFFERENCE
    FROM StudentGPA
    WHERE AVG_INTERNATIONAL_GPA > AVG_DOMESTIC_GPA
    ORDER BY GPA_DIFFERENCE DESC;
    Example 92 - List the top 5 most common pairs of extracurricular activities.,the SQL command will be something like this
    WITH SplitActivities AS (
        SELECT ID, TRIM(value) AS ACTIVITY
        FROM STUDENT
        CROSS APPLY STRING_SPLIT(EXTRACURRICULAR_ACTIVITIES, ',')
    ),
    ActivityPairs AS (
        SELECT 
            a1.ACTIVITY as ACTIVITY1,
            a2.ACTIVITY as ACTIVITY2,
            COUNT(*) as PAIR_COUNT
        FROM SplitActivities a1
        JOIN SplitActivities a2 ON a1.ID = a2.ID AND a1.ACTIVITY < a2.ACTIVITY
        GROUP BY a1.ACTIVITY, a2.ACTIVITY
    )
    SELECT TOP 5 ACTIVITY1, ACTIVITY2, PAIR_COUNT
    FROM ActivityPairs
    ORDER BY PAIR_COUNT DESC;
    Example 93 - Calculate the average GPA trend over the years for each department.,the SQL command will be something like this
    WITH YearlyDeptGPA AS (
        SELECT 
            MAJOR,
            YEAR(ADMISSION_DATE) as ADMISSION_YEAR,
            AVG(GPA) as AVG_GPA
        FROM STUDENT
        GROUP BY MAJOR, YEAR(ADMISSION_DATE)
    )
    SELECT 
        MAJOR,
        ADMISSION_YEAR,
        AVG_GPA,
        AVG_GPA - LAG(AVG_GPA) OVER (PARTITION BY MAJOR ORDER BY ADMISSION_YEAR) as GPA_CHANGE
    FROM YearlyDeptGPA
    ORDER BY MAJOR, ADMISSION_YEAR;
    \nExample 94 - Identify students who have consistently improved their GPA each year.,the SQL command will be something like this
    WITH YearlyGPA AS (
        SELECT 
            ID,
            FIRST_NAME,
            LAST_NAME,
            YEAR(ADMISSION_DATE) as YEAR,
            GPA,
            ROW_NUMBER() OVER (PARTITION BY ID ORDER BY YEAR(ADMISSION_DATE)) as YEAR_NUM,
            COUNT(*) OVER (PARTITION BY ID) as TOTAL_YEARS
        FROM STUDENT
    ),
    GPAComparison AS (
        SELECT 
            ID,
            FIRST_NAME,
            LAST_NAME,
            YEAR,
            GPA,
            LAG(GPA) OVER (PARTITION BY ID ORDER BY YEAR) as PREV_GPA,
            YEAR_NUM,
            TOTAL_YEARS
        FROM YearlyGPA
    )
    SELECT DISTINCT ID, FIRST_NAME, LAST_NAME
    FROM GPAComparison
    GROUP BY ID, FIRST_NAME, LAST_NAME, TOTAL_YEARS
    HAVING SUM(CASE WHEN GPA > PREV_GPA OR PREV_GPA IS NULL THEN 1 ELSE 0 END) = TOTAL_YEARS;
    \nExample 95 - Find the department with the highest retention rate (percentage of students who haven't dropped out).,the SQL command will be something like this
    WITH DepartmentStats AS (
        SELECT 
            MAJOR,
            COUNT(*) as TOTAL_STUDENTS,
            SUM(CASE WHEN EXPECTED_GRADUATION >= GETDATE() THEN 1 ELSE 0 END) as ACTIVE_STUDENTS
        FROM STUDENT
        GROUP BY MAJOR
    )
    SELECT TOP 1
        MAJOR,
        TOTAL_STUDENTS,
        ACTIVE_STUDENTS,
        (CAST(ACTIVE_STUDENTS AS FLOAT) / TOTAL_STUDENTS) * 100 as RETENTION_RATE
    FROM DepartmentStats
    ORDER BY RETENTION_RATE DESC;
    \nExample 96 - Calculate the correlation coefficient between GPA and scholarship amount for each department.,the SQL command will be something like this
    WITH DepartmentStats AS (
        SELECT 
            MAJOR,
            AVG(GPA) as AVG_GPA,
            AVG(SCHOLARSHIP_AMOUNT) as AVG_SCHOLARSHIP,
            AVG(GPA * SCHOLARSHIP_AMOUNT) as AVG_PRODUCT,
            AVG(GPA * GPA) as AVG_GPA_SQUARED,
            AVG(SCHOLARSHIP_AMOUNT * SCHOLARSHIP_AMOUNT) as AVG_SCHOLARSHIP_SQUARED,
            COUNT(*) as STUDENT_COUNT
        FROM STUDENT
        GROUP BY MAJOR
    )
    SELECT 
        MAJOR,
        (STUDENT_COUNT * AVG_PRODUCT - AVG_GPA * AVG_SCHOLARSHIP) / 
        (SQRT((STUDENT_COUNT * AVG_GPA_SQUARED - AVG_GPA * AVG_GPA) * 
              (STUDENT_COUNT * AVG_SCHOLARSHIP_SQUARED - AVG_SCHOLARSHIP * AVG_SCHOLARSHIP))) as CORRELATION_COEFFICIENT
    FROM DepartmentStats
    ORDER BY CORRELATION_COEFFICIENT DESC;
    \nExample 97 - Identify students who have taken internships in all seasons (Spring, Summer, Fall, Winter).
    WITH SeasonalInternships AS (
        SELECT 
            ID,
            CASE 
                WHEN MONTH(INTERNSHIP_START_DATE) IN (3, 4, 5) THEN 'Spring'
                WHEN MONTH(INTERNSHIP_START_DATE) IN (6, 7, 8) THEN 'Summer'
                WHEN MONTH(INTERNSHIP_START_DATE) IN (9, 10, 11) THEN 'Fall'
                ELSE 'Winter'
            END as SEASON
        FROM STUDENT
        WHERE INTERNSHIP_START_DATE IS NOT NULL
    )
    SELECT s.FIRST_NAME, s.LAST_NAME
    FROM STUDENT s
    JOIN SeasonalInternships si ON s.ID = si.ID
    GROUP BY s.ID, s.FIRST_NAME, s.LAST_NAME
    HAVING COUNT(DISTINCT si.SEASON) = 4;
    \nExample 98 - Calculate the average GPA for students based on the number of extracurricular activities they participate in.,the SQL command will be something like this
    WITH ActivityCount AS (
        SELECT 
            ID,
            GPA,
            LEN(EXTRACURRICULAR_ACTIVITIES) - LEN(REPLACE(EXTRACURRICULAR_ACTIVITIES, ',', '')) + 1 as ACTIVITY_COUNT
        FROM STUDENT
    )
    SELECT 
        ACTIVITY_COUNT,
        AVG(GPA) as AVG_GPA,
        COUNT(*) as STUDENT_COUNT
    FROM ActivityCount
    GROUP BY ACTIVITY_COUNT
    ORDER BY ACTIVITY_COUNT;
    \nExample 99 - Find students who have the same first name as another student in their department, but a higher GPA:,the SQL command will be something like this
    SELECT 
        s1.FIRST_NAME,
        s1.LAST_NAME as HIGHER_GPA_STUDENT,
        s2.LAST_NAME as LOWER_GPA_STUDENT,
        s1.MAJOR,
        s1.GPA as HIGHER_GPA,
        s2.GPA as LOWER_GPA
    FROM STUDENT s1
    JOIN STUDENT s2 ON s1.FIRST_NAME = s2.FIRST_NAME 
                AND s1.MAJOR = s2.MAJOR 
                AND s1.GPA > s2.GPA
    ORDER BY s1.MAJOR, s1.FIRST_NAME, s1.GPA DESC;
    \nExample 100 - Identify departments where the average GPA of students with internships is significantly higher (more than 0.5 points) than those without.,the SQL command will be something like this
    WITH InternshipGPA AS (
        SELECT 
            MAJOR,
            AVG(CASE WHEN INTERNSHIP_COMPANY IS NOT NULL THEN GPA END) as AVG_GPA_WITH_INTERNSHIP,
            AVG(CASE WHEN INTERNSHIP_COMPANY IS NULL THEN GPA END) as AVG_GPA_WITHOUT_INTERNSHIP
        FROM STUDENT
        GROUP BY MAJOR
    )
    SELECT 
        MAJOR,
        AVG_GPA_WITH_INTERNSHIP,
        AVG_GPA_WITHOUT_INTERNSHIP,
        (AVG_GPA_WITH_INTERNSHIP - AVG_GPA_WITHOUT_INTERNSHIP) as GPA_DIFFERENCE
    FROM InternshipGPA
    WHERE (AVG_GPA_WITH_INTERNSHIP - AVG_GPA_WITHOUT_INTERNSHIP) > 0.5
    ORDER BY GPA_DIFFERENCE DESC;
    \nExample 101 - Calculate the percentage of students in each department who have earned more credits than the university-wide average.,the SQL command will be something like this
    WITH UniversityAvg AS (
        SELECT AVG(CREDITS_EARNED) as AVG_CREDITS
        FROM STUDENT
    ),
    DepartmentStats AS (
        SELECT 
            MAJOR,
            COUNT(*) as TOTAL_STUDENTS,
            SUM(CASE WHEN CREDITS_EARNED > (SELECT AVG_CREDITS FROM UniversityAvg) THEN 1 ELSE 0 END) as ABOVE_AVG_STUDENTS
        FROM STUDENT
        GROUP BY MAJOR
    )
    SELECT 
        MAJOR,
        TOTAL_STUDENTS,
        ABOVE_AVG_STUDENTS,
        (CAST(ABOVE_AVG_STUDENTS AS FLOAT) / TOTAL_STUDENTS) * 100 as PERCENTAGE_ABOVE_AVG
    FROM DepartmentStats
    ORDER BY PERCENTAGE_ABOVE_AVG DESC;
    \nExample 102 - Find students who have taken internships at companies that have hired interns from multiple departments.,the SQL command will be something like this
    WITH CompanyDepartments AS (
        SELECT 
            INTERNSHIP_COMPANY,
            COUNT(DISTINCT MAJOR) as DEPT_COUNT
        FROM STUDENT
        WHERE INTERNSHIP_COMPANY IS NOT NULL
        GROUP BY INTERNSHIP_COMPANY
        HAVING COUNT(DISTINCT MAJOR) > 1
    )
    SELECT 
        s.FIRST_NAME,
        s.LAST_NAME,
        s.MAJOR,
        s.INTERNSHIP_COMPANY,
        cd.DEPT_COUNT
    FROM STUDENT s
    JOIN CompanyDepartments cd ON s.INTERNSHIP_COMPANY = cd.INTERNSHIP_COMPANY
    ORDER BY cd.DEPT_COUNT DESC, s.INTERNSHIP_COMPANY, s.LAST_NAME, s.FIRST_NAME;
    \nExample 103 - Identify students who have maintained a GPA above the department average for each year of their studies.,the SQL command will be something like this
    WITH YearlyDeptAvg AS (
        SELECT 
            MAJOR,
            YEAR(ADMISSION_DATE) as YEAR,
            AVG(GPA) as AVG_DEPT_GPA
        FROM STUDENT
        GROUP BY MAJOR, YEAR(ADMISSION_DATE)
    ),
    StudentYearlyGPA AS (
        SELECT 
            ID,
            FIRST_NAME,
            LAST_NAME,
            MAJOR,
            YEAR(ADMISSION_DATE) as YEAR,
            GPA
        FROM STUDENT
    )
    SELECT DISTINCT
        s.ID,
    \nExample 104 - Find students who have taken internships in companies that have a higher average GPA than their department's average.,the SQL command will be something like this
    WITH DeptAvgGPA AS (
        SELECT MAJOR, AVG(GPA) as DEPT_AVG_GPA
        FROM STUDENT
        GROUP BY AV
    ),
    CompanyAvgGPA AS (
        SELECT INTERNSHIP_COMPANY, AVG(GPA) as COMPANY_AVG_GPA
        FROM STUDENT
        WHERE INTERNSHIP_COMPANY IS NOT NULL
        GROUP BY INTERNSHIP_COMPANY
    )
    SELECT 
        s.FIRST_NAME,
        s.LAST_NAME,
        s.V,
        s.INTERNSHIP_COMPANY,
        d.DEPT_AVG_GPA,
        c.COMPANY_AVG_GPA
    FROM STUDENT s
    JOIN DeptAvgGPA d ON s.MAJOR = d.MAJOR
    JOIN CompanyAvgGPA c ON s.INTERNSHIP_COMPANY = c.INTERNSHIP_COMPANY
    WHERE c.COMPANY_AVG_GPA > d.DEPT_AVG_GPA
    ORDER BY s.MAJOR, c.COMPANY_AVG_GPA DESC;  
    \nExample 105 - Calculate the "academic momentum" for each student, defined as the rate of change in GPA per credit earned.,the SQL command will be something like this
    SELECT 
        FIRST_NAME,
        LAST_NAME,
        MAJOR,
        GPA,
        CREDITS_EARNED,
        CASE 
            WHEN CREDITS_EARNED > 0 THEN (GPA - 2.0) / CREDITS_EARNED 
            ELSE 0 
        END as ACADEMIC_MOMENTUM
    FROM STUDENT
    ORDER BY ACADEMIC_MOMENTUM DESC;  
    \nExample 106 - Identify departments where the gender gap in average GPA is the largest.,the SQL command will be something like this
    WITH GenderGPA AS (
        SELECT 
            MAJOR,
            AVG(CASE WHEN GENDER = 'Male' THEN GPA END) as AVG_MALE_GPA,      
            AVG(CASE WHEN GENDER = 'Female' THEN GPA END) as AVG_FEMALE_GPA
        FROM STUDENT
        GROUP BY MAJOR
    )
    SELECT 
        MAJOR,
        AVG_MALE_GPA,
        AVG_FEMALE_GPA,
        ABS(AVG_MALE_GPA - AVG_FEMALE_GPA) as GPA_GAP
    FROM GenderGPA
    WHERE AVG_MALE_GPA IS NOT NULL AND AVG_FEMALE_GPA IS NOT NULL
    ORDER BY GPA_GAP DESC;
    \nExample 107 - Find students who have participated in internships at companies that have hired interns from all departments.,the SQL command will be something like this
    WITH CompanyDeptCount AS (
        SELECT 
            INTERNSHIP_COMPANY,
            COUNT(DISTINCT MAJOR) as DEPT_COUNT
        FROM STUDENT
        WHERE INTERNSHIP_COMPANY IS NOT NULL
        GROUP BY INTERNSHIP_COMPANY
    ),
    TotalDepts AS (
        SELECT COUNT(DISTINCT MAJOR) as TOTAL_DEPTS
        FROM STUDENT
    )
    SELECT 
        s.FIRST_NAME,
        s.LAST_NAME,
        s.MAJOR,
        s.INTERNSHIP_COMPANY
    FROM STUDENT s
    JOIN CompanyDeptCount c ON s.INTERNSHIP_COMPANY = c.INTERNSHIP_COMPANY
    CROSS JOIN TotalDepts t
    WHERE c.DEPT_COUNT = t.TOTAL_DEPTS
    ORDER BY s.INTERNSHIP_COMPANY, s.LAST_NAME, s.FIRST_NAME;
    \nExample 108 - Calculate the diversity index for each department based on the number of different countries represented.,the SQL command will be something like this
    WITH DeptCountries AS (
        SELECT 
            MAJOR,
            COUNT(DISTINCT COUNTRY) as COUNTRY_COUNT,
            COUNT(*) as TOTAL_STUDENTS
        FROM STUDENT
        GROUP BY MAJOR
    )
    SELECT 
        MAJOR,
        COUNTRY_COUNT,
        TOTAL_STUDENTS,
        (CAST(COUNTRY_COUNT AS FLOAT) / TOTAL_STUDENTS) as DIVERSITY_INDEX
    FROM DeptCountries
    ORDER BY DIVERSITY_INDEX DESC;
    \nExample 109 - Identify students who have earned more credits than 75% of students admitted in the same year.,the SQL command will be something like this
    WITH AdmissionYearStats AS (
        SELECT 
            YEAR(ADMISSION_DATE) as ADMISSION_YEAR,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY CREDITS_EARNED) OVER (PARTITION BY YEAR(ADMISSION_DATE)) as CREDITS_75TH_PERCENTILE
        FROM STUDENT
    )
    SELECT 
        s.FIRST_NAME,
        s.LAST_NAME,
        s.ADMISSION_DATE,
        s.CREDITS_EARNED,
        a.CREDITS_75TH_PERCENTILE
    FROM STUDENT s
    JOIN AdmissionYearStats a ON YEAR(s.ADMISSION_DATE) = a.ADMISSION_YEAR
    WHERE s.CREDITS_EARNED > a.CREDITS_75TH_PERCENTILE
    ORDER BY s.ADMISSION_DATE, s.CREDITS_EARNED DESC;
    \nExample 110 - Calculate the average time (in days) between internship end date and expected graduation date for each department.,the SQL command will be something like this
    SELECT 
        MAJOR,
        AVG(DATEDIFF(day, INTERNSHIP_END_DATE, EXPECTED_GRADUATION)) as AVG_DAYS_AFTER_INTERNSHIP
    FROM STUDENT
    WHERE INTERNSHIP_END_DATE IS NOT NULL AND EXPECTED_GRADUATION IS NOT NULL
    GROUP BY MAJOR
    ORDER BY AVG_DAYS_AFTER_INTERNSHIP;
    \nExample 111 - Find students who have the highest GPA among those with the same number of extracurricular activities.,the SQL command will be something like this
    WITH ActivityCount AS (
        SELECT 
            ID,
            FIRST_NAME,
            LAST_NAME,
            GPA,
            LEN(EXTRACURRICULAR_ACTIVITIES) - LEN(REPLACE(EXTRACURRICULAR_ACTIVITIES, ',', '')) + 1 as ACTIVITY_COUNT,
            ROW_NUMBER() OVER (PARTITION BY LEN(EXTRACURRICULAR_ACTIVITIES) - LEN(REPLACE(EXTRACURRICULAR_ACTIVITIES, ',', '')) + 1 ORDER BY GPA DESC) as RN
        FROM STUDENT
    )
    SELECT 
        FIRST_NAME,
        LAST_NAME,
        GPA,
        ACTIVITY_COUNT
    FROM ActivityCount
    WHERE RN = 1
    ORDER BY ACTIVITY_COUNT DESC, GPA DESC;
    \nExample 112 - How many students have internships lasting more than 3 months?,the SQL command will be something like this
    SELECT FIRST_NAME, LAST_NAME, INTERNSHIP_COMPANY,
        (JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY(INTERNSHIP_START_DATE)) AS Internship_Days
    FROM STUDENT
    WHERE (JULIANDAY(INTERNSHIP_END_DATE) - JULIANDAY(INTERNSHIP_START_DATE)) > 9
    );
    \nExample 113 - what are the columns in the student table?
    the SQL command will be something like this PRAGMA table_info(STUDENT);
    \nExample 114 - show me all the students majoring in computer sceince.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, GPA, MAJOR
    FROM STUDENT
    WHERE GPA > 3.0 AND MAJOR = 'Computer Science';  
    \nExample 115 - show me all the students majoring in Psychology.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, GPA, MAJOR
    FROM STUDENT
    WHERE GPA > 3.0 AND MAJOR = 'Psychology';
    \nExample 116 - show me all the students majoring in Mechanical Engineering.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, GPA, MAJOR
    FROM STUDENT
    WHERE GPA > 3.0 AND MAJOR = 'Mechanical Engineering';
    \nExample 117 - show me all the students majoring in Business Administration.,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, GPA, MAJOR
    FROM STUDENT
    WHERE GPA > 3.0 AND MAJOR = 'Business Administration';
    \nExample 117 - How many students got internship and name of each student?,
    the SQL command will be something like this SELECT COUNT(*) AS Total_Interns,
    GROUP_CONCAT(FIRST_NAME || ' ' || LAST_NAME, ', ') AS Intern_Names
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL;
    \nExample 118 - Name of each student who got internship this year and the company?,
    the SQL command will be something like this SELECT FIRST_NAME,
    LAST_NAME,
    INTERNSHIP_COMPANY
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL
    AND INTERNSHIP_START_DATE >= date('now', 'start of year')
    AND INTERNSHIP_START_DATE <= date('now', 'end of year')
    ORDER BY LAST_NAME, FIRST_NAME;
    \nExample 119 - Which are the companies that selected students as interns?,
    the SQL command will be something like this SELECT DISTINCT INTERNSHIP_COMPANY,
    COUNT(*) AS Number_of_Interns
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL
    GROUP BY INTERNSHIP_COMPANY
    ORDER BY Number_of_Interns DESC, INTERNSHIP_COMPANY;
    \nExample 120 - How many companies are there in the database?,
    the SQL command will be something like this SELECT COUNT(DISTINCT INTERNSHIP_COMPANY) AS Total_Companies
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL;
    \nExample 121 - What are the companies in the database and how many interns does each have?,
    the SQL command will be something like this SELECT INTERNSHIP_COMPANY,
    COUNT(*) AS Number_of_Interns
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL
    GROUP BY INTERNSHIP_COMPANY
    ORDER BY Number_of_Interns DESC, INTERNSHIP_COMPANY;
    \nExample 122 - How many companies are in the database and name each one of them?,
    the SQL command will be something like this SELECT COUNT(DISTINCT INTERNSHIP_COMPANY) AS Total_Companies,
    GROUP_CONCAT(DISTINCT INTERNSHIP_COMPANY, ', ') AS Company_Names
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NOT NULL;
    \nExample 123 - How many students are from Houston and what are their names?,
    the SQL command will be something like this SELECT COUNT(*) AS Total_Students_From_Houston,
    GROUP_CONCAT(FIRST_NAME || ' ' || LAST_NAME, ', ') AS Student_Names
    FROM STUDENT
    WHERE CITY = 'Houston';
    \nExample 134 - List all students from Houston with a total count,
    the SQL command will be something like this SELECT COUNT(*) OVER () AS Total_Students_From_Houston,
    FIRST_NAME || ' ' || LAST_NAME AS Student_Name
    FROM STUDENT
    WHERE CITY = 'Houston'
    ORDER BY LAST_NAME, FIRST_NAME;
    \nExample 123 - How many students are from Houston and what are their names?,
    the SQL command will be something like this SELECT COUNT(*) AS Total_Students_From_Houston,
    GROUP_CONCAT(FIRST_NAME || ' ' || LAST_NAME, ', ') AS Student_Names
    FROM STUDENT
    WHERE CITY = 'Houston';
    \nExample 124 - Which students have completed an internship at "Google" and are expected to graduate in the next two years?,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, MAJOR, INTERNSHIP_COMPANY, EXPECTED_GRADUATION
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY = 'Google'
    AND EXPECTED_GRADUATION BETWEEN DATE('now') AND DATE('now', '+2 years');
    \nFind all students who were admitted in 2020 and have earned more than 50 credits:,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, MAJOR, ADMISSION_DATE, CREDITS_EARNED
    FROM STUDENT
    WHERE strftime('%Y', ADMISSION_DATE) = '2020'
    AND CREDITS_EARNED > 50;
    \nExample 125 - List the names of students who have not provided an internship company but have a GPA greater than 3.2:,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, GPA
    FROM STUDENT
    WHERE INTERNSHIP_COMPANY IS NULL
    AND GPA > 3.2;
    \nExample 126 - Which students have an internship position titled "Data Analyst" and are earning a scholarship of more than 5000:,
    the SQL command will be something like this SELECT s.student_id, s.first_name, s.last_name, i.position, s.scholarship_amount
    FROM students s
    JOIN internships i ON s.student_id = i.student_id
    WHERE i.position = 'Data Analyst'
    AND s.scholarship_amount > 5000;
    \nExample 127 - which students have an internship position titled as data engineer.,
    the SQL command will be something like this 
    SELECT FIRST_NAME, LAST_NAME
    FROM STUDENT
    WHERE TRIM(LOWER(INTERNSHIP_POSITION)) = 'data engineer';
    \nExample 128 - Find the oldest student in the database and display their name, date of birth, and age:,the SQL command will be something like this 
    SELECT FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, 
            (julianday('now') - julianday(DATE_OF_BIRTH)) / 365.25 AS AGE
    FROM STUDENT
    ORDER BY DATE_OF_BIRTH
    LIMIT 1;
    \nExample 129 - Find all students who have never participated in any extracurricular activities:,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, EXTRACURRICULAR_ACTIVITIES
    FROM STUDENT
    WHERE EXTRACURRICULAR_ACTIVITIES IS NULL
    OR EXTRACURRICULAR_ACTIVITIES = '';
    \nExample 130 - Display the names of students whose phone number or email is missing:,
    the SQL command will be something like this SELECT FIRST_NAME, LAST_NAME, PHONE, EMAIL
    FROM STUDENT
    WHERE PHONE IS NULL
    OR EMAIL IS NULL;
    \nExample 131 -  Retrieve the list of students who are expected to graduate within 1 year and have not completed an internship:,
    the SQL command will be something like SELECT FIRST_NAME, LAST_NAME, EXPECTED_GRADUATION, INTERNSHIP_COMPANY
    FROM STUDENT
    WHERE EXPECTED_GRADUATION <= DATE('now', '+1 year')
    AND INTERNSHIP_COMPANY IS NULL;
    \nExample 132 -List all students from "Texas" who have been awarded a scholarship and have a GPA higher than 3.5:,
    the SQL command will be something like SELECT FIRST_NAME, LAST_NAME, COUNTRY, GPA, SCHOLARSHIP_AMOUNT
    FROM STUDENT
    WHERE COUNTRY = 'India'
    AND SCHOLARSHIP_AMOUNT > 0
    AND GPA > 3.5;
    \nExample 133 - name of the students starting with letter O and the major they are studying but remove the duplicates.,
    the SQL command will be something like SELECT DISTINCT FIRST_NAME, MAJOR
    FROM STUDENT
    WHERE FIRST_NAME LIKE 'O%';

     also the sql code should not have ``` in beginning or end and sql word in output answer, without any additional explanation.
    """
]
