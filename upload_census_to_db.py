import pandas as pd
from sqlalchemy import create_engine

def upload_census_data():
    print("Connecting to PostgreSQL database 'census_db'...")
    # Establish connection
    engine = create_engine(
        "postgresql+psycopg2://postgres:ash123@localhost:5432/census_db"
    )

    print("Reading local CSV files...")
    # Load raw CSV datasets
    df1 = pd.read_csv("India_Census_2001.csv")
    df2 = pd.read_csv("India_Census_2011.csv")

    print("Uploading India_Census_2001.csv to PostgreSQL as 'india_census_2001'...")
    # Upload 2001 dataset
    df1.to_sql(
        "india_census_2001",
        engine,
        if_exists="replace",
        index=False
    )

    print("Uploading India_Census_2011.csv to PostgreSQL as 'india_census_2011'...")
    # Upload 2011 dataset
    df2.to_sql(
        "india_census_2011",
        engine,
        if_exists="replace",
        index=False
    )

    print("All census data uploaded successfully!")

if __name__ == "__main__":
    upload_census_data()
