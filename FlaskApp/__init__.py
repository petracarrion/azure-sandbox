from datetime import date, datetime
import os
from uuid import uuid4

from azure.cosmos import ContainerProxy, DatabaseProxy
from flask import Flask

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey

app = Flask(__name__)

COSMOS_HOST = os.environ.get('COSMOS_HOST', '${{ secrets.COSMOS_HOST }}')
COSMOS_KEY = os.environ.get('COSMOS_KEY', '${{ secrets.COSMOS_KEY }}')
DATABASE_ID = 'consume'
CONTAINER_ID = 'reading'

client = cosmos_client.CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_KEY})

db: DatabaseProxy = client.create_database_if_not_exists(id=DATABASE_ID)


def init_container(reset=False):
    if reset:
        db.delete_container(container)
    return db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey(path='/id', kind='Hash'))


container: ContainerProxy = init_container()


def create_reading(reading_value):
    reading = {
        'id': str(uuid4()),
        'reading_timestamp': datetime.now().timestamp(),
        'reading_value': reading_value
    }
    container.create_item(body=reading)


@app.route("/create", methods=['POST'])
def create_item():
    create_reading(1000)
    return "Created"


@app.route("/reset", methods=['POST'])
def reset_items():
    init_container(reset=True)
    create_reading(0)
    return "Reset"


@app.route("/list")
def list_items():
    all_items = list(container.read_all_items())
    all_items = [{
        'reading_timestamp': datetime.fromtimestamp(item['reading_timestamp']),
        'reading_value': item['reading_value']
    } for item in all_items]
    return all_items


@app.route("/")
def index():
    result = '''
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Value</th>
        </tr>
    '''
    all_items = list_items()
    next_value = all_items[-1]['reading_value'] + 1
    for item in all_items:
        result += f'''
        <tr>
            <td>{item['reading_timestamp']}</td>
            <td>{item['reading_value']}</td>
        </tr>
        '''
    result += '</table>'
    result += f'''
    <form action="/create" method="POST">
        <input name="reading_value" type="number" min="{next_value}" value="{next_value}"/>
        <input value="Add" type="submit" />
    </form>
    '''
    result += f'''
    <form action="/reset" method="POST">
        <input value="Reset All" type="submit" />
    </form>
    '''
    return result


if __name__ == "__main__":
    app.run(debug=True)
