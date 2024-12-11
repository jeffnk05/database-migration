import secrets
import string
from datetime import datetime

from arango import ArangoClient

client = ArangoClient(hosts='http://arangodb:8529')

db = client.db('dvdrental', username='root', password='rootpassword')

def generate_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))  # for a 20-character password
    return password

# 5 a 
def update_staff_password():
    staff = db.collection('staff')

    cursor = staff.all()

    for document in cursor:
        print(f'User: {document['username']}, old password: {document['password']}')

        # replace password in staff document 
        document['password'] = generate_password()

        # commit change
        staff.update(document)
        print(f'User: {document['username']}, new password: {document['password']}')   

def create_new_address():
    cursor = db.aql.execute(
    'RETURN LENGTH(address)'
    )
    address_id = next(cursor, None) + 1 # Create address id by incrementing count by 1
    
    address_doc = {
        "_key": str(address_id),
        "address": "1796 Santiago de Compostela Way",
        "city": "city/295",
        "address2": "",
        "postal_code": "18743",
        "phone": "860452626434",
        "last_update": datetime.now().isoformat()
    }
    address = db.collection('address')
    address.update(address_doc)

    print("Neues Dokument erstellt: ", address.get(str(address_id)))
    return address.get(str(address_id))['_id']

def add_store_and_move_inventory():
    address_id = create_new_address

    # create new store document
    new_store = {
        "_key": "3",
        "address": str(address_id),
        "manager_staff_id": "1"
        }
    db.collection("store").insert(new_store)
    print('Methode zum Erstellen eines neuen Standorts: db.collection("store").insert(new_store)')

    # get store id
    new_store_id = db.collection("store").get('3')['_id']

    # Inventar zum neuen Standort verlegen
    update_inventory_store_key(new_store_id)

    # update store ids of staff (Nebenbedingung)
    update_staff_store(new_store_id)

# Aktualisiert die 'store'-ID in allen Dokumenten der Inventory-Collection
def update_inventory_store_key(new_store_id):
    # Die AQL-Abfrage zum Aktualisieren der 'store'-IDs in allen 'inventory'-Dokumenten
    query = '''
    FOR inv IN inventory
        UPDATE inv WITH { store: @new_store_id } IN inventory
    '''
    print(f'Befehl zum Inventar verlegen: {query}')
    db.aql.execute(query, bind_vars={"new_store_id": new_store_id})
    print(f"Alle Inventory-Dokumente wurden aktualisiert und die Store-Id wurde auf '{new_store_id}' gesetzt.")

def update_staff_store(store_id):
    query = '''
    FOR s IN staff
        UPDATE s WITH { store: @new_store_id } IN staff
    '''
    print(f'Befehl zum verlegen der Mitarbeter: {query}')
    db.aql.execute(query, bind_vars={"new_store_id": store_id})
    print(f"Alle Staff-Dokumente wurden aktualisiert und die Store-Id wurde auf '{store_id}' gesetzt.")

print("Vergebt allen Mitarbeitern ein neues, sicheres Passwort")
update_staff_password()

print(" Erzeugt einen neuen Standort (mit einer fiktiven Adresse) und verlegt das Inventar der beiden bisherigen Standorte dorthin")
add_store_and_move_inventory()
