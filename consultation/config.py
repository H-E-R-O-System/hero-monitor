from pymongo import MongoClient

username = 'rosemaryellery'
password = '27YOjZirWfNwcCc1'

client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.l7w57ga.mongodb.net/?retryWrites=True&w=majority&appName=Cluster0')