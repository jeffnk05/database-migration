from arango import ArangoClient

client = ArangoClient(hosts='http://arangodb:8529')

db = client.db('dvdrental', username='root', password='rootpassword')

# 4 a
def count_movies():
    # Execute the query
    cursor = db.aql.execute(
    'RETURN LENGTH(film)'
    )
    # Iterate through the result cursor
    result = next(cursor, None)
    print(result)

# 4 b
def get_unique_movies_per_store():
    query = """
            FOR i IN inventory
                COLLECT store_id = i.store
                AGGREGATE movie_count = COUNT(UNIQUE(i.film_id))
                RETURN {
                    store_id: store_id,
                    movie_count_per_store: movie_count
                }
        """
    cursor = db.aql.execute(query)

    print(f"Befehl: {query}")
    print("Ergebnis")
    for doc in cursor:
        print(doc)
    
# 4 c
def movies_per_actor():
    cursor = db.aql.execute(
        """
            FOR a IN actor
            LET film_count = LENGTH(
                FOR fa IN film_actor
                    FILTER fa._from == a._id
                    RETURN fa
            )
            SORT film_count DESC
            LIMIT 10
            RETURN { first_name: a.first_name, last_name: a.last_name, film_count }
        """
    )
    for doc in cursor:
        print(doc)

# 4 d
def earnings_per_employee():
    cursor = db.aql.execute(
    """
    FOR s IN staff
        FOR p IN payment
            FILTER p.staff == s._id
            COLLECT staff_id = s._id, staff_name = s.name AGGREGATE earnings = SUM(p.amount)
        RETURN { staff_id, staff_name, earnings }
    """
    )

    for doc in cursor:
        print(doc)

# 4 e
def get_rentals_per_customer():
    cursor = db.aql.execute(
        """
            FOR r IN rental
                COLLECT customer_id = r.customer WITH COUNT INTO rental_count
                SORT rental_count DESC
                LIMIT 10
                RETURN {
                    customer_id: customer_id,
                    rental_count: rental_count
                }
        """
    )
    for doc in cursor:
        print(doc)

 # 4 f
def sales_per_customer_per_store():
    cursor = db.aql.execute(
        """
            FOR c IN customer
                LET payments = (
                    FOR p IN payment
                    FILTER p.customer == c._id
                    COLLECT AGGREGATE total = SUM(p.amount)
                    RETURN total
                )[0]
                LET store = FIRST(
                    FOR s IN store
                    FILTER c.store == s._id
                    RETURN s
                )
                SORT payments DESC
                LIMIT 10
                RETURN { 
                    first_name: c.first_name, 
                    last_name: c.last_name, 
                    store_id: store._id, 
                    total_spent: payments 
                }
        """
    )
    for doc in cursor:
        print(doc)

# 4 g Die 10 meistgesehenen Filme unter Angabe des Titels, absteigend sortiert
def most_watched_movies():
    cursor = db.aql.execute(
        """
            FOR f IN film
                LET rental_count = LENGTH(
                    FOR i IN inventory
                        FILTER i.film == f._id
                        FOR r IN rental
                        FILTER r.inventory == i._id
                        RETURN 1
                )
                SORT rental_count DESC
                LIMIT 10
                RETURN {
                    title: f.title,
                    total_rentals: rental_count
            }
        """
    )

    for doc in cursor:
        print(doc)

def most_watched_movies_per_category():
    cursor = db.aql.execute(
        """
        FOR c IN category
            LET watch_count = LENGTH(
                FOR fc IN film_category
                FILTER c._id == fc._to
                FOR f IN film
                    FILTER f._id == fc._from
                    FOR i IN inventory
                    FILTER i.film == f._id
                    FOR r IN rental
                        FILTER r.inventory == i._id
                        RETURN r
            )
            SORT watch_count DESC
            LIMIT 3
            RETURN { 
                watch_count: watch_count,
                category: c.name
            }
    """
    )
    for doc in cursor:
        print(doc)
    

def get_customer_view():
    # ArangoSearch View erstellen
    db.create_arangosearch_view(
        name='Customer_Info',
        properties={
            "links": {
                "customer": {
                    "analyzers": ["identity"],
                    "includeAllFields": True,
                    "fields": {
                        "first_name": {},
                        "last_name": {},
                        "address_id": {},
                        "store": {},
                        "activebool": {}
                    }
                },
                "address": {
                    "analyzers": ["identity"],
                    "includeAllFields": True,
                    "fields": {
                        "address": {},
                        "postal_code": {},
                        "phone": {},
                        "city": {}
                    }
                },
                "city": {
                    "analyzers": ["identity"],
                    "includeAllFields": True,
                    "fields": {
                        "city": {},
                        "country": {}
                    }
                },
                "country": {
                    "analyzers": ["identity"],
                    "includeAllFields": True,
                    "fields": {
                        "country": {}
                    }
                }
            }
        }
    )

    query = """
    FOR cust IN customer
        LET addr = DOCUMENT(cust.address)
        LET city = DOCUMENT(addr.city)
        LET country = DOCUMENT(city.country)
        RETURN {
            customer_id: cust._key,
            name: CONCAT(cust.first_name, " ", cust.last_name),
            address: addr.address,
            "zip code": addr.postal_code,
            phone: addr.phone,
            city: city.city,
            country: country.country,
            notes: cust.activebool == true ? "active" : "",
            store_id: cust.store
        }
    """
    
    cursor = db.aql.execute(query)
    for document in cursor:
        print(document)



# count_movies()

# get_unique_movies_per_store()

# movies_per_actor()

# earnings_per_employee()

# print("Rentals per customer")
# get_rentals_per_customer

# sales_per_customer_per_store()

# print("")
# print("Die 10 meistgesehenen Filme unter Angabe des Titels, absteigendsortiert")
# most_watched_movies()

# print("Die Vor- und Nachnamen sowie die Niederlassung der 10 Kunden, die das meiste Geld ausgegeben haben")
# most_watched_movies_per_category()

print("Customer list")
get_customer_view()