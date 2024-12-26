from threading import Thread
from app.listener import EventListener
from app.api import start_api
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    print("Starting application...")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    listener = EventListener(
        os.getenv('ETHEREUM_NODE_URL'),
        start_block=int(os.getenv('START_BLOCK'))
    )
    
    listener_thread = Thread(target=listener.start)
    listener_thread.daemon = True
    listener_thread.start()
    
    start_api()
