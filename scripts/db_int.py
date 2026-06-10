from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import pandas as pd

class DB:

    def __init__(self):
            load_dotenv()
            self.user = os.environ.get('POSTGRES_USER')
            self.password = os.environ.get('POSTGRES_PASSWORD')
            self.host = os.environ.get('POSTGRES_HOST')
            self.port = os.environ.get('POSTGRES_PORT')
            self.database = os.environ.get('POSTGRES_DB')
            self.conn_str = f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
            self.create_pipeline_tables()

    def check_postgres_connection(self):
        print(f'Connecting to database {self.database} on port {self.port} as user {self.user} on host {self.host}')
        try:
            engine = create_engine(self.conn_str)
            connection = engine.connect()
            connection.close()
            return True, "Connection to the database was successful"
        except Exception as e:
            return False, f"Could not connect to the database due to {e}"
        
    def create_pipeline_tables(self):
        '''
            This function automates creation of postgres table used in the pipeline.
        '''

        engine = create_engine(self.conn_str)
        league_table = """
        CREATE TABLE IF NOT EXISTS league (
            id INT PRIMARY KEY,
            league_id BIGINT UNIQUE NOT NULL,
            name VARCHAR NOT NULL,
            type VARCHAR,
            country VARCHAR
        );
        """
    
        team_table = '''
            CREATE TABLE IF NOT EXISTS team (
            id INT PRIMARY KEY,
            name VARCHAR NOT NULL,
            country VARCHAR,
            national BOOLEAN
        );
        '''

        match_table = '''
            create table if not exists match (
                id bigint primary key
                ,date timestamp not null
                ,home_id int references team(id) not null   
                ,away_id int references team(id) not null
                ,season int not null 
                ,home_score int 
                ,away_score int                             
            )
        '''

        try:
            with engine.begin() as conn:
                conn.execute(text(league_table))
                conn.execute(text(team_table))
                conn.execute(text(match_table))
                pass
        except Exception as e:
            print(f"Failed to create pipeline tables due to: {e}")

    def drop_pipeline_tables(self):
        engine = create_engine(self.conn_str)
        league_table = 'drop table if exists league cascade'
        try:
            with engine.begin() as conn:
                conn.execute(text(league_table)) 
            print("Successfully dropped all pipeline tables.")
        except Exception as e:
            print(f"Failed to drop pipeline tables due to: {e}")
    
    def truncate_pipeline_tables(self):
        engine = create_engine(self.conn_str)
        league_table = 'truncate table league restart identity cascade'
        try:
            with engine.begin() as conn:
                conn.execute(text(league_table))
            print("Successfully truncated all pipeline tables.")
        except Exception as e:
            print(f"Failed to truncate pipeline tables due to: {e}")


    def save_dataframe_to_table(self,df: pd.DataFrame, table_name: str, if_exists):
        engine = create_engine(self.conn_str)
        try:
            df.to_sql(name=table_name, con=engine, index=False, if_exists=if_exists)
            print(f'Saved data to {table_name} postgres table')
        except Exception as e:
            print(f'Could not save table due to {e}')

    def fetch_league_ids(self):
        engine = create_engine(self.conn_str)
        try:
            league_ids = pd.read_sql("select league_id, name, country from league", con=engine)
            print(f'Successfully fetched league IDs')
            return league_ids
        except Exception as e:
            print(f'Could not fetch league ids due to {e}')


if __name__ == '__main__':
    db = DB()
    db.create_pipeline_tables()
