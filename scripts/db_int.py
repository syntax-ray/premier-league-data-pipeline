from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import pandas as pd
from utils.logging_config import get_logger


logger = get_logger(__name__)

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
        logger.info('Connecting to database %s on port %s as user %s on host %s',self.database, self.port, self.user, self.host)
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
                ,round varchar                             
            )
        '''

        try:
            with engine.begin() as conn:
                conn.execute(text(league_table))
                conn.execute(text(team_table))
                conn.execute(text(match_table))
                pass
        except Exception as e:
            logger.error("Failed to create pipeline tables due to: %s", e)
            raise

    def drop_pipeline_tables(self):
        engine = create_engine(self.conn_str)
        league_table = 'drop table if exists league cascade'
        team_table = 'drop table if exists team cascade'
        match_table = 'drop table if exists match cascade'
        try:
            with engine.begin() as conn:
                conn.execute(text(league_table)) 
                conn.execute(text(team_table))
                conn.execute(text(match_table))
            logger.info("Successfully dropped all pipeline tables.")
        except Exception as e:
            logger.error("Failed to drop pipeline tables due to: %s", e)
            raise
    
    def truncate_pipeline_tables(self):
        engine = create_engine(self.conn_str)
        league_table = 'truncate table league restart identity cascade'
        try:
            with engine.begin() as conn:
                conn.execute(text(league_table))
            logger.info("Successfully truncated all pipeline tables.")
        except Exception as e:
            logger.error("Failed to truncate pipeline tables due to: %s", e)
            raise


    def save_dataframe_to_table(self,df: pd.DataFrame, table_name: str, if_exists):
        engine = create_engine(self.conn_str)
        try:
            df.to_sql(name=table_name, con=engine, index=False, if_exists=if_exists)
            rows = df.shape[0]
            logger.info('Saved %s records to %s postgres table', rows, table_name)
        except Exception as e:
            logger.error('Could not save table due to %s', e)
            raise

    def fetch_league(self):
        engine = create_engine(self.conn_str)
        try:
            league_ids = pd.read_sql("select league_id, name, country from league", con=engine)
            logger.info('Successfully fetched league IDs')
            return league_ids
        except Exception as e:
            logger.error('Could not fetch league ids due to %s', e)
            raise

    def fetch_team_ids(self):
        engine = create_engine(self.conn_str)
        try:
            team_ids = pd.read_sql("select id from team", con=engine)
            return set(team_ids['id'].to_list()) if not team_ids.empty else {}
        except Exception as e:
            logger.error('Could not fetch team ids due to %s', e)
            raise

    def fetch_match_ids(self):
        engine = create_engine(self.conn_str)
        try:
            match_ids = pd.read_sql("select id from match", con=engine)
            return set(match_ids['id'].to_list()) if not match_ids.empty else {}
        except Exception as e:
            logger.error('Could not fetch match ids due to %s', e)
            raise

    def fetch_league_ids(self):
        """
        Fetch the league IDs to process.

        Currently restricted to the top five European leagues.
        1. Premier League - England 
        2. Ligue 1 - France 
        3. Bundesliga - Germany 
        4. Serie A - Italy 
        5. La Liga - Spain

        return type - dict. League id -> description
        """
       

        league_data = self.fetch_league()

        league_ids = {}

        top_leagues = ( ("Premier League", "England"), ("Ligue 1", "France"), ("Bundesliga", "Germany"), ("Serie A", "Italy"), ("La Liga", "Spain") )

        for top_league in top_leagues:
            league_name, country = top_league

            league = (league_data.loc[
                (league_data["name"] == league_name)
                & (league_data["country"] == country)
            ])

            if league.empty:
                logger.error("Could not fetch %s - %s league data from the database", country, league_data)
                raise RuntimeError("Could not fetch %s - %s league data from the database", country, league_data)
            else:
                league_ids[f'{int(league.iloc[0]["league_id"])}'] = f'{country}-{league_name}' 

        return league_ids


if __name__ == '__main__':
    db = DB()
    # db.create_pipeline_tables()
    db.drop_pipeline_tables()
