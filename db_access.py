from pymongo import MongoClient

class DBClient:
    def __init__(self):
        username = 'rosemaryellery'
        password = '27YOjZirWfNwcCc1'
        client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.l7w57ga.mongodb.net/?retryWrites=True&w=majority&appName=Cluster0')
        self.db = client.get_database('hero_data').user_records
    
    def clear_all(self):
        self.db.delete_many({})
        print('All data successfully cleared from MongoDB.')
    
    def upload_consult(self, new_consult):
        self.db.insert_one(new_consult)
        print('New consultation data uploaded to MongoDB.')
