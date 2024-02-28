from pymongo import MongoClient

username = 'rosemaryellery'
password = '27YOjZirWfNwcCc1'

client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.l7w57ga.mongodb.net/?retryWrites=True&w=majority&appName=Cluster0')

db = client.get_database('hero_data')
records = db.user_records

# create new document:
new_consult = {
    "user_id": 2,
    "consult_id": "123",
    "consult_time": "2024-01-03T11:37:41.250976",
    "consult_data":{
        "pss": {
            "answers": [2, 4, 1, 1, 1, 2, 3, 0, 2]
        },
        "wct": {
            "answers": [False, False, False, False, False, True, False, True, False, False, False, True, False, False, False, False, False, True, False, False, False, True, False, True, False, True, True, False, True, True], "change_ids": [5, 12, 18, 23, 28]
        },
        "vat": {
            "answers": [True, True, True, True, True, True, True, True, True, True, True, True, False, True, True, True, False, True, True, True],
            "times": [3.249995643272996e-06, 1.0855352920043515, 0.993170249988907, 0.9657484159979504, 1.0510747090011137, 1.1216245000105118, 0.8606732909975108, 0.9954385419987375, 1.072387666994473, 1.13113916599832, 1.0880492090072948, 0.9347829159960384, 1.0505073749955045, 0.9540435000089929, 0.9279510839987779, 1.0650419159937883, 1.0506032920093276, 0.9512055829982273, 0.9305694999929983, 1.0252792500104988]
        }
    }   
}

records.insert_one(new_consult)