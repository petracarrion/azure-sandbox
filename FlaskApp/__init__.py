from datetime import date, datetime
import os
from uuid import uuid4

from azure.cosmos import ContainerProxy
from flask import Flask

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

app = Flask(__name__)

COSMOS_HOST = os.environ.get('COSMOS_HOST', '${{ secrets.COSMOS_HOST }}')
COSMOS_KEY = os.environ.get('COSMOS_KEY', '${{ secrets.COSMOS_KEY }}')
DATABASE_ID = 'consume'
CONTAINER_ID = 'reading'

client = cosmos_client.CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_KEY} )

db = client.create_database_if_not_exists(id=DATABASE_ID)
container: ContainerProxy = db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey(path='/id', kind='Hash'))


def create_reading(reading_date, reading_value):
    reading = {
        'id': str(uuid4()),
        'reading_date': reading_date,
        'reading_value': reading_value
    }
    container.create_item(body=reading)


@app.route("/")
def index():
    return (
        "Try /hello/Petra for parameterized Flask route.\n"
        f"Try /module for module import guidance"
    )


@app.route("/create")
def create_item():
    create_reading(datetime.now().timestamp(), 1000)
    return "Created"


@app.route("/list")
def list_items():
    all_items = list(container.read_all_items(max_item_count=100))
    return all_items


@app.route("/hello/<name>", methods=['GET'])
def hello(name: str):
    return f"hello {name}"


if __name__ == "__main__":
    app.run()
