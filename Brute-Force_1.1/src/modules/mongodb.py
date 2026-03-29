# src/modules/mongodb.py

import pymongo

def login_mongodb(ip, usuario, password, puerto=27017, timeout=6):
    try:
        client = pymongo.MongoClient(f"mongodb://{usuario}:{password}@{ip}:{puerto}/", serverSelectionTimeoutMS=timeout*1000)
        client.admin.command('ismaster')
        return True
    except Exception:
        return False
