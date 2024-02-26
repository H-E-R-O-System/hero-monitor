import pygame as pg
import pandas as pd
from consult import Consultation
import os
import datetime

# os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pg.init()

sim_count = 3

all_user_data = pd.read_csv("data/user_data.csv")
all_user_data = all_user_data.set_index("Username")

for username in all_user_data.index:
    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(weeks=x) for x in range(sim_count)]
    for idx in range(sim_count):

        consult = Consultation(
            pi=False, authenticate=True, seamless=True, scale=0.7, username=username,
            password=all_user_data.loc[username, "Password"], date=date_list[idx]
        )

        consult.loop()

        if consult.output is not None:
            consult_output = pd.DataFrame(consult.output, index=[0])
            if consult.user:
                if not os.path.isdir(f"data/consult_records/user_{consult.user.id}"):
                    os.mkdir(f"data/consult_records/user_{consult.user.id}")

                save_path = f"data/consult_records/user_{consult.user.id}/consult_{consult.id}.tsv"
            else:
                # only the case when no authenticate user is set to false
                save_path = f"data/consult_records/guest/consult_{consult.id}.tsv"

            consult_output.to_csv(save_path, sep="\t",index=False)