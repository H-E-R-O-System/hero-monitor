import pygame as pg
import pandas as pd
from consult import Consultation
import datetime
from db_access import DBClient

db = DBClient()
db.clear_all()

# os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pg.init()

sim_count = 20

all_user_data = pd.read_csv("data/user_data.csv")
all_user_data = all_user_data.set_index("Username")

for username in all_user_data.index:
    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(weeks=x) for x in range(sim_count)]
    for idx in range(sim_count):

        consult = Consultation(
            pi=False, authenticate=True, seamless=True, scale=0.7, username=username,
            password=all_user_data.loc[username, "Password"], consult_date=date_list[idx],
            wct_turns=30, pss_questions=10,
            auto_run=True, db_client=db, local=False
        )

        consult.loop()
