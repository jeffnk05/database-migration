Ausführungsbefehle:

docker-compose down
docker-compose up --build

Zusätzliche Informationen:
CREATE: In der migrate.py wird die Migration durchgeführt.
READ: In der read.py werden die Leseoperationen durchgeführt.
UPDATE: In der update.py werden die Update-Operationen durchgeführt.
DELETE: In der delete.py werden die Löschoperationen durchgeführt.

Die CRUD Ergebnisse der CRUD Optionen werden sofern sie einen Output liefern im Logfile des script-Containers ausgegeben.
Teilweise wurden für Befehle die Methoden der pyArango Bibliothek ausgeführt, diese geben wir nicht aus, da wir den Code nur kopieren würden.

Aufgabenaufteilung:

Aufgabe 1: Endrit & Jeff 
Aufgabe 2: Jeff
Aufgbae 3: Endrit: Aufbau der Datenbankverbindungen, Jeff: Umsetzung der Migrationslogik 
Aufgabe 4: Jeff & Endrit (Pair Programming)
Aufgabe 5: Jeff
Aufgabe 6: Endrit