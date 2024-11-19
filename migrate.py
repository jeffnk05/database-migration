import base64
import datetime
import traceback
import decimal
import time

from arango import ArangoClient
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor

def connect_postgres():
    conn = None
    while not conn:
        try:
            conn = psycopg2.connect(
                                dbname = "dvdrental", 
                                user = "postgres", 
                                host= 'postgresdb',
                                password = "1234",
                                port = '5432'
                                )
            return conn
        except OperationalError as e:
            print(f"Fehler beim Herstellen der Verbindung zu Postgres: {e}")
            time.sleep(5)
    return conn


def connect_arangodb():
    try:
        # Initialize the ArangoDB client.
        client = ArangoClient(hosts='http://arangodb:8529')

        # Connect to "_system" database as root user.
        # This returns an API wrapper for "_system" database.
        sys_db = client.db('_system', username='root', password='rootpassword')

        # Create a new database named "dvdrental" if it does not exist.
        if not sys_db.has_database('dvdrental'):
            sys_db.create_database('dvdrental')

        # Connect to "dvdrental" database as root user.
        # This returns an API wrapper for "dvdrental" database.
        db = client.db('dvdrental', username='root', password='rootpassword')

        return db
    except Exception as e:
        print(f"Fehler beim Herstellen der Verbindung zu ArangoDB: {e}")

def create_collection(db, name):
    if db.has_collection(name):
        pass 
    else:
        db.create_collection(
            name, 
            user_keys=True,
            key_generator='traditional'
        )

def create_edge_collection(db, name):
    if db.has_collection(name):
        pass 
    else:
        db.create_collection(
            name,
            user_keys=True,
            key_generator='traditional', 
            edge=True
        )

def migrate_table(cursor, db, table_name, collection_name, id_field, fields):
  
    # Fetch records from PostgreSQL table
    cursor.execute(f'SELECT * FROM {table_name};')
    records = cursor.fetchall()
    
    create_collection(db, collection_name)

    # Insert each record into ArangoDB collection
    for record in records:
        document = {'_key': str(record[id_field])}
        for field in fields:
            if field.endswith('_id'):
                related_collection = field[:-3]  
                document[related_collection] = f"{related_collection}/{record[field]}"
            elif isinstance(record[field], memoryview):  # check if value is a BYTEA
                document[field] = base64.b64encode(record[field].tobytes()).decode('utf-8')
            elif isinstance(record[field], decimal.Decimal): # check if value is a decimal number
                document[field] = float(record[field])
            elif isinstance(record[field], datetime.date):  # check if value is a `date`-object
                document[field] = record[field].isoformat()
            elif isinstance(record[field], datetime.datetime):  # check if value is `timestamp`-object
                document[field] = record[field].isoformat()
            else:
                document[field] = record[field]
        db.collection(collection_name).insert(document)
    print(f'All {table_name} records successfully inserted into {collection_name}') 

def migrate_mapping_table(cursor, db, table_name, collection_name, field, from_field, to_field):
    # Fetch records from PostgreSQL table
    cursor.execute(f'SELECT * FROM {table_name};')
    records = cursor.fetchall()
    
    create_edge_collection(db, collection_name)

    for record in records:
        document = dict()

        from_key = f"{from_field[:-3]}/{record[from_field]}"
        document["_from"] = from_key

        to_key = f"{to_field[:-3]}/{record[to_field]}"
        document["_to"] = to_key
        if isinstance(record[field], datetime.datetime):  # check if value is `timestamp`-object
                document[field] = record[field].isoformat()
        db.collection(collection_name).insert(document)
    print(f'All {table_name} records successfully transferred to {collection_name}')

def migrate_manager_to_store(cursor, db):
    cursor.execute('SELECT store_id, manager_staff_id FROM store')
    records = cursor.fetchall()

    for record in records:
        store_doc = db.collection('store').get(str(record["store_id"]))

        if store_doc:
            update_data = {
                "_key": str(record["store_id"]), 
                "manager_staff_id": str(record["manager_staff_id"]  )
            }
            db.collection('store').update(update_data)
            print(f"Store-Dokument {record['store_id']} erfolgreich aktualisiert.")
        else:
            print(f"Store-Dokument mit _key {record['store_id']} nicht gefunden.")
 

def main():
    try:
        pg_conn = connect_postgres()
        arangodb_db = connect_arangodb()

        tables_to_migrate = [
            {"table_name": "actor", "collection_name": "actor", "id_field": "actor_id", "fields": ["first_name", "last_name", "last_update"]},
            {"table_name": "country", "collection_name": "country", "id_field": "country_id", "fields": ["country", "last_update"]},
            {"table_name": "category", "collection_name": "category", "id_field": "category_id", "fields": ["name", "last_update"]},
            {"table_name": "language", "collection_name": "language", "id_field": "language_id", "fields": ["name", "last_update"]},
            {"table_name": "city", "collection_name": "city", "id_field": "city_id", "fields": ["city", "country_id", "last_update"]},
            {"table_name": "film", "collection_name": "film", "id_field": "film_id", "fields": ['title', 'description', 'release_year', 
             'language_id','rental_duration', 'rental_rate', 'length', 'replacement_cost','rating', 'special_features', 'fulltext', "last_update"]},
            {"table_name": "address", "collection_name": "address", "id_field": "address_id", 
             "fields": ["address", "city_id", "address2", "postal_code", "phone", "last_update"]},
            {"table_name": "store", "collection_name": "store", "id_field": "store_id", "fields": ["address_id", "last_update"]},
            {"table_name": "staff", "collection_name": "staff", "id_field": "staff_id", 
             "fields": ["first_name", "last_name", "address_id", "email", "store_id", "active", "username", "password", "picture", "last_update"]},
            {"table_name": "inventory", "collection_name": "inventory", "id_field": "inventory_id", 
             "fields": ["film_id", "store_id", "last_update"]},
            {"table_name": "customer", "collection_name": "customer", "id_field": "customer_id", 
             "fields": ["store_id", "first_name", "last_name", "email", "address_id", "activebool", "create_date", "active", "last_update"]},
            {"table_name": "rental", "collection_name": "rental", "id_field": "rental_id",
             "fields": ["rental_date", "inventory_id", "customer_id", "return_date", "staff_id", "last_update"]},
            {"table_name": "payment", "collection_name": "payment", "id_field": "payment_id", 
             "fields": ["customer_id", "staff_id", "rental_id", "amount", "payment_date"]},
        ]

        mapping_tables_to_migrate = [
            {"table_name": "film_category", "collection_name": "film_category", "field": "last_update", "from_field": "film_id", "to_field": "category_id"},
            {"table_name": "film_actor", "collection_name": "film_actor", "field": "last_update", "from_field": "actor_id", "to_field": "film_id"}
        ]

        for table in tables_to_migrate:
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                migrate_table(cursor=cursor, 
                db=arangodb_db, 
                table_name=table['table_name'], 
                collection_name=table['collection_name'], 
                id_field=table['id_field'], 
                fields=table['fields'],
                )

        for mtable in mapping_tables_to_migrate:
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                migrate_mapping_table(
                    cursor=cursor,
                    db=arangodb_db,
                    table_name=mtable["table_name"],
                    collection_name=mtable["collection_name"],
                    field=mtable["field"],
                    from_field=mtable["from_field"],
                    to_field=mtable["to_field"]
                )

        with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            migrate_manager_to_store(cursor=cursor, db=arangodb_db)

    except Exception as e:
        print(f"Fehler während der Migration: {e}")
        traceback.print_exc()

    finally:
        if pg_conn:
            pg_conn.close()
        print("Verbindung zu PostgreSQL geschlossen.")

if __name__ == "__main__":
    main()