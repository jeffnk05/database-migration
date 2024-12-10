from arango import ArangoClient

client = ArangoClient(hosts='http://arangodb:8529')

db = client.db('dvdrental', username='root', password='rootpassword')

# 4 a
def count_movies():
    # Execute the query
    query = 'RETURN LENGTH(film)'
    cursor = db.aql.execute(query)
    # Iterate through the result cursor
    print(f"Befehl: {query}")
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
    query = """
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
    cursor = db.aql.execute(query)
    print(f"Befehl: {query}")
    for doc in cursor:
        print(doc)

# 4 d
def earnings_per_employee():
    query = """
    FOR s IN staff
        FOR p IN payment
            FILTER p.staff == s._id
            COLLECT staff_id = s._id, staff_name = s.name AGGREGATE earnings = SUM(p.amount)
        RETURN { staff_id, staff_name, earnings }
    """
    cursor = db.aql.execute(query)

    print(f"Befehl: {query}")
    for doc in cursor:
        print(doc)

# 4 e
def get_rentals_per_customer():
    query = """
            FOR r IN rental
                COLLECT customer_id = r.customer WITH COUNT INTO rental_count
                SORT rental_count DESC
                LIMIT 10
                RETURN {
                    customer_id: customer_id,
                    rental_count: rental_count
                }
        """
    cursor = db.aql.execute(query)

    print(f"Befehl: {query}")
    for doc in cursor:
        print(doc)

 # 4 f
def sales_per_customer_per_store():
    query = """
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
    cursor = db.aql.execute(query)

    print(f"Befehl: {query}")
    for doc in cursor:
        print(doc)

# 4 g Die 10 meistgesehenen Filme unter Angabe des Titels, absteigend sortiert
def most_watched_movies():
    query = """
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
    cursor = db.aql.execute(query)

    print(f"Befehl: {query}")
    for doc in cursor:
        print(doc)

def most_watched_movies_per_category():
    query = """
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
    cursor = db.aql.execute(query)

    print(f"Befehl: {query}")
    for doc in cursor:
        print(doc)
    

def get_customer_view():
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

    print(f"Befehl: {query}")
    for document in cursor:
        print(document)


print("Gesamtanzahl der verfügbaren Filme")
count_movies()

print("")
print("Anzahl der unterschiedlichen Filme je Standort")
get_unique_movies_per_store()

print("")
print("Die Vor- und Nachnamen der 10 Schauspieler mit den meisten Filmen, absteigend sortiert.")
movies_per_actor()

print("")
print("Die Erlöse je Mitarbeiter")
earnings_per_employee()

print("")
print("Die IDs der 10 Kunden mit den meisten Entleihungen")
get_rentals_per_customer

print("")
print("Die Vor- und Nachnamen sowie die Niederlassung der 10 Kunden, die das meiste Geld ausgegeben haben")
sales_per_customer_per_store()

print("")
print("Die 10 meistgesehenen Filme unter Angabe des Titels, absteigendsortiert")
most_watched_movies()

print("")
print("Die Vor- und Nachnamen sowie die Niederlassung der 10 Kunden, die das meiste Geld ausgegeben haben")
most_watched_movies_per_category()

print("")
print("Customer list")
get_customer_view()