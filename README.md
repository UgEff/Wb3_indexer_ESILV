# UserOperation Monitoring Event

Application de monitoring des UserOperation sur Ethereum permettant de suivre et d'analyser les transactions ERC-4337 (Account Abstraction).

## Description

Cette application indexe et explore les événements `UserOperationEvent` d'un contrat ERC-4337.

**Informations du contrat :**
- Adresse : `0x0000000071727de22e5e9d8baf0edac6f37da032`
- Topic : `0x49628fd1471006c1482da88028e9ce4dbb080b815c9b0344d39e5a8e6ec1419f`

## Architecture
```bash
    .
    ├── app/
    │   ├── listener.py    # Indexeur d'événements
    │   ├── api.py         # API REST Flask
    │   ├── db.py         # Gestion base de données
    ├── templates/
    │   └── index.html    # Interface utilisateur
    ├── .env              # Variables d'environnement
    ├── .env.example      # Example de configuration
    ├── .gitignore       # Fichiers ignorés par git
    ├── README.md
    ├── requirements.txt
    ├── main.py
    └── events.db
```

## Installation

1. Cloner le repository :
```bash
git clone <repository_url>
cd app
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
```bash
cp .env.example .env
```
Puis modifiez le fichier `.env` avec vos paramètres :
```
# Ethereum Node
ETHEREUM_NODE_URL=votre_url_infura
START_BLOCK=21000000

# API Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# Contract Configuration
ENTRYPOINT_ADDRESS=0x0000000071727de22e5e9d8baf0edac6f37da032
USER_OP_TOPIC=0x49628fd1471006c1482da88028e9ce4dbb080b815c9b0344d39e5a8e6ec1419f
```

5. Lancer l'application :
```bash
python main.py
```

6. Accéder à l'interface web :
```
http://localhost:5000
```

## API REST

### GET /events
Récupère les événements avec filtres optionnels.

**Paramètres :**
- `userOpHash` : Hash de l'opération
- `sender` : Adresse de l'expéditeur
- `paymaster` : Adresse du paymaster
- `success` : Statut de l'opération (true/false)
- `blockNumber` : Numéro de bloc spécifique
- `fromBlock` : Bloc de début pour une plage
- `toBlock` : Bloc de fin pour une plage

**Exemple :**
```
GET /events?sender=0x123...&success=true
```

## Base de Données

Structure de la table `user_operations` :

```sql
CREATE TABLE user_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userOpHash TEXT UNIQUE,
    sender TEXT,
    paymaster TEXT,
    nonce TEXT,
    success INTEGER,
    actualGasCost TEXT,
    actualGasUsed TEXT,
    blockNumber INTEGER,
    timestamp TEXT
)
```

## Technologies Utilisées

### Backend
- Python 3.8+
- Web3.py pour l'interaction Ethereum
- Flask pour l'API REST
- SQLite pour le stockage
- python-dotenv pour la gestion des variables d'environnement

## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.




