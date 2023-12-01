# Numele Proiectului

Descrierea proiectului.

## Configurare

### Cerințe de sistem

- Python 3.10.12
- Docker și Docker Compose

### Instalare

1. Clonează acest repository:

   ```shell
   git clone https://github.com/utilizator/nume-proiect.git
   ```

2. Intră în directorul proiectului:

   ```shell
   cd nume-proiect
   ```

3. Creează și activează un mediu virtual:

   ```shell
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Instalează dependințele proiectului folosind Poetry:

   ```shell
   poetry install
   ```

5. Copiază fișierul de configurare `.env.example` și renumește-l în `.env`. Editează fișierul `.env` pentru a configura variabilele de mediu necesare.

6. Rulează migrările bazei de date folosind Alembic:

   ```shell
   alembic upgrade head
   ```

## Utilizare

1. Pornirea proiectului local folosind Docker Compose:

   ```shell
   docker-compose up -d
   ```

2. Accesează aplicația în browser la adresa `http://localhost:8000`.

## Contribuție

Contribuțiile sunt binevenite! Pentru a contribui la acest proiect, urmează pașii de mai jos:

1. Fork acestui repository
2. Creează o ramură nouă (`git checkout -b feature/nume-functie`)
3. Comite-ți modificările (`git commit -am 'Adaugă funcție nouă'`)
4. Împinge-ți ramura (`git push origin feature/nume-functie`)
5. Deschide un Pull Request

## Licență

Acest proiect este licențiat sub [Nume Licență]. Pentru mai multe detalii, consultă fișierul [LICENSE](LICENSE).

## Migrations (alembic)
new migration:

add in version 
from fastapi_users_db_sqlalchemy import generics

and table users
modify id: 
sa.Column('id', generics.GUID(), nullable=False),
