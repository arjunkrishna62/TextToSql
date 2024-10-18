# Natural Language to Database
#####  This project is a Natural Language to SQL Query Converter that allows users to input queries in natural language and converts them into SQL queries, executing them on an SQLite database. The results are displayed in a web-based interface using Streamlit, with an option to visualize the data and download results as a CSV file.

### Features

•	Natural Language Query Processing: Converts user-provided natural language inputs into SQL          queries.

•	Database Interaction: Executes generated SQL queries on an SQLite database and retrieves results.

•	Visualization: Displays query results in a tabular format and offers data visualization using       Matplotlib.

•	Generative AI Integration: Uses Google’s Gemini AI (via google-generativeai) to assist in natural   language understanding and SQL generation.

•	Export Options: Provides an option to download query results as a CSV file.

### Installation

 #### 1. clone the repository:
 git clone https://github.com/yourusername/arjunkrishna62.git

#### 2. Set up a Virtual Environment:
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Recomended(use conda)

#### 3. Install dependencies:

pip install -r requirements.txt

 Required Libraries:

	•	python-dotenv: Manage environment variables from a .env file.
	•	streamlit: A simple web framework for displaying and interacting with the app.
	•	pandas: For data manipulation and processing SQL query results.
	•	matplotlib: For data visualization of SQL query results.
	•	google-generativeai: Integrates Google’s Gemini AI for natural language to SQL conversion.

#### 4. Set up Environment Variables:

GOOGLE_API_KEY=your_google_api_key_here

To find the appi key :-

Go to - makerssuit.google.com/app/apike

On the Web page click - "create API key in niw project "

Once it created copy and paste it in .env file.

### Usage

#### 1.	Run the Streamlit app:
Start the app by running the following command in your terminal:
streamlit run application.py

#### 2.	Input a natural language query:
Use the input box on the Streamlit interface to enter a natural language query. Example:
Show me all students who have a GPA above 3.5

### 3.	Execute SQL and visualize results:
•	The app will convert the query into SQL, execute it on the SQLite database, and display the results.

•	You can visualize the results using the Matplotlib charts provided in the app.

•	An option is provided to download the data as a CSV file.

### Project Structure

``` /NewProject
│
├── application.py           # Main application file that runs the Streamlit app
├── sql.py                   # SQL handling and query execution logic
├── requirements.txt          # Python dependencies for the project
├── .env                      # Environment file for storing sensitive keys (not committed)
├── data/                     # Directory containing the SQLite database
├── README.md                 # Project documentation (this file) ```





