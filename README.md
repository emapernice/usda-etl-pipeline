# USDA Crop Insights — ETL & Analytics with Python and MySQL

This project builds a complete **ETL pipeline** to extract, transform, and load agricultural data from the **USDA Quick Stats API** into a **MySQL database**, enabling data-driven insights into crop price trends across U.S. states.

---

## Project Overview

- **Goal:** Automate the collection and analysis of U.S. agricultural statistics (e.g., Soybeans, Corn prices).
- **Data Source:** USDA NASS Quick Stats API
- **Tech Stack:** Python · Pandas · SQLAlchemy · MySQL · Matplotlib
- **Focus:** Real-world ETL automation and exploratory data analysis (EDA)

---

## Project Structure


usda-etl-pipeline/
│
├── config/
│ ├── .env # Environment variables (not tracked in git)
│ ├── db_config.json.example 
│ └── api_keys.json.example 
│
├── data/
│ ├── raw/ # Raw JSON files from the USDA API
│ └── processed/ # Cleaned CSV files ready for load
│
├── sql/
│   └── schema.sql 
│
├── src/
│ ├── extract.py 
│ ├── transform.py 
│ ├── load.py 
│ ├── run_etl.py 
│ └── api/
│   ├── main.py   
│   ├── db.py            
│   └── routes/
│       └── prices.py   
│
├── requirements.txt
├── .gitignore
└── README.md


⚙️ Setup Instructions

1 - Clone this repository
git clone https://github.com/yourusername/usda-crop-insights.git
cd usda-crop-insights

2 - Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows

3 - Install dependencies
pip install -r requirements.txt

4 - Set up environment variables
Create a .env file inside config/ with:
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_DATABASE=usda_data
USDA_API_KEY=your_usda_api_key

5 - Run the ETL pipeline
python src/run_etl.py


📊 Example Outputs

After running the ETL, the MySQL table usda_observations stores clean agricultural data that can be analyzed for trends such as:

Average crop prices by state and year
Year-over-year price changes
Regional performance comparisons
Example SQL query:

SELECT year, commodity_desc, AVG(price) AS avg_price
FROM usda_observations
WHERE commodity_desc = 'SOYBEANS'
GROUP BY year, commodity_desc
ORDER BY year;

## API Layer (FastAPI)

After the ETL pipeline stores cleaned USDA data into the MySQL database,
this FastAPI service allows querying the processed results.

📈 Future Improvements

Integrate data visualization dashboards (Streamlit or Plotly Dash)
Expand commodity coverage (e.g., Wheat, Cotton)
Schedule automatic updates via Linux CRON jobs

👨‍💻 Author

Emanuel Pernice
Data Analyst & Python Developer
📧 [perniceemanuel@gmail.com]