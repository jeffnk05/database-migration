from arango import ArangoClient

client = ArangoClient(hosts='http://arangodb:8529')

db = client.db('dvdrental', username='root', password='rootpassword')

"""
    Löscht die folgende Daten:
    a. Alle Filme, die weniger als 60 Minuten Spielzeit haben
    b. Alle damit zusammenhängenden Entleihungen
"""
def delete_film_and_rentals():
    # Delete payments associated with the rentals
    delete_payments_query = """
            FOR f IN film
                FILTER f.length < 60
                FOR i IN inventory
                    FILTER i.film == f._id
                    FOR r IN rental
                        FILTER r.inventory == i._id
                        FOR p IN payment
                            FILTER p.rental == r._id
                            REMOVE p IN payment
        """
    print("Lösche payments für alle rentals von Filmen unter 60 Minuten")
    db.aql.execute(delete_payments_query)
    print("Payments gelöscht.")

    # Delete rentals 
    delete_rentals_query = """
            FOR f IN film
                FILTER f.length < 60
                FOR i IN inventory
                    FILTER i.film == f._id
                    FOR r IN rental
                        FILTER r.inventory == i._id
                        REMOVE r IN rental
        """
    print("Lösche rentals für Filme unter 60 Minuten")
    db.aql.execute(delete_rentals_query)
    print("Rentals gelöscht.")

    # Delete films from inventory
    delete_inventory_query = """
            FOR f IN film
                FILTER f.length < 60
                FOR i IN inventory
                    FILTER i.film == f._id
                    REMOVE i IN inventory
        """
    print("Lösche inventory-Einträge für Filme unter 60 Minuten")
    db.aql.execute(delete_inventory_query)
    print("Inventory-Einträge gelöscht.")

    # Delete films from film_actor and film_category
    del_film_cat_query = """
            FOR f IN film
                FILTER f.length < 60
                FOR fc IN film_category
                    FILTER fc.film == f._id
                    REMOVE fc IN film_category
        """
    del_film_act_query = """
            FOR f IN film
                FILTER f.length < 60
                FOR fa IN film_actor
                    FILTER fa.film == f._id
                    REMOVE fa IN film_actor
        """
    print("Lösche film_category- und film_actor-Einträge für Filme unter 60 Minuten")
    db.aql.execute(del_film_cat_query)
    db.aql.execute(del_film_act_query)
    print("film_category und film_actor Einträge gelöscht.")

    # Delete all movies
    del_film_query = """
            FOR f IN film
                FILTER f.length < 60
                REMOVE f IN film
        """
    print("Lösche alle Filme unter 60 Minuten")
    db.aql.execute(del_film_query)
    print("Filme gelöscht.")

delete_film_and_rentals()