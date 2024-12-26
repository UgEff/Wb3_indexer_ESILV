import time
from web3 import Web3
import json
from typing import Optional
from datetime import datetime
from .db import save_event, init_db
from dotenv import load_dotenv
import os

load_dotenv()

class EventListener:
    def __init__(self, node_url, start_block=None):
        # Initialisation de la connexion Web3
        self.web3 = Web3(Web3.HTTPProvider(node_url))
        self.start_block = start_block
        # Adresse du contrat EntryPoint
        self.entry_point_address = Web3.to_checksum_address(os.getenv('ENTRYPOINT_ADDRESS'))
        # Signature de l'événement
        self.user_op_topic = os.getenv('USER_OP_TOPIC')
        
        # Configuration de l'ABI pour l'événement UserOperationEvent
        self.event_abi = {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "userOpHash", "type": "bytes32"},
                {"indexed": True, "name": "sender", "type": "address"},
                {"indexed": True, "name": "paymaster", "type": "address"},
                {"indexed": False, "name": "nonce", "type": "uint256"},
                {"indexed": False, "name": "success", "type": "bool"},
                {"indexed": False, "name": "actualGasCost", "type": "uint256"},
                {"indexed": False, "name": "actualGasUsed", "type": "uint256"}
            ],
            "name": "UserOperationEvent",
            "type": "event"
        }
        
        # Initialiser la base de données
        init_db()

    def start(self):
        print("\n=== Starting Event Listener ===")
        
        if not self.web3.is_connected():
            raise Exception("Echec de la connexion au noeud Ethereum")
        print("✓ Connecté au noeud Ethereum")
        
        contract = self.web3.eth.contract(
            address=self.entry_point_address,
            abi=[self.event_abi]
        )
        print(f"✓ Contract init a l'adresse : {self.entry_point_address}")
        
        current_block = self.start_block
        latest_block = self.web3.eth.block_number
        print(f"\nInitial state:")
        print(f"- Start block: {current_block:,}")
        print(f"- Latest block: {latest_block:,}")
        print(f"- Blocks scan: {latest_block - current_block:,}")
        
        #statistiques de scanning
        stats = {
            "blocks_scanned": 0,  # Nombre total de blocs analysés
            "events_found": 0,    # Nombre total d'événements trouvés
            "errors": 0           # Nombre d'erreurs rencontrées
        }
        
        while True:
            try:
                # Récupération du dernier bloc
                latest_block = self.web3.eth.block_number
                if current_block < latest_block:
                    # Limitation à 1000 blocs pour éviter les timeouts
                    end_block = min(current_block + 1000, latest_block)
                    print(f"\n🔍 Scanning blocks {current_block:,} to {end_block:,}")
                    
                    try:
                        # Configuration du filtre pour les événements
                        event_filter = {
                            'address': self.entry_point_address,
                            'fromBlock': current_block,
                            'toBlock': end_block,
                            'topics': [self.user_op_topic]
                        }
                        
                        logs = self.web3.eth.get_logs(event_filter)
                        stats["blocks_scanned"] += (end_block - current_block + 1)
                        stats["events_found"] += len(logs)
                        
                        print(f"\nFound {len(logs)} UserOperationEvent(s)")
                        
                        for log in logs:
                            try:
                                event = contract.events.UserOperationEvent().process_log(log)
                                event_data = self._format_event(event)
                                self._save_event(event_data)
                                print(f"✓ Processed event from block {log['blockNumber']:,}")
                            except Exception as e:
                                stats["errors"] += 1
                                print(f"✗ Error processing event: {e}")
                        
                    except Exception as e:
                        print(f"Error getting logs: {e}")
                        stats["errors"] += 1
                        time.sleep(5)
                        continue
                    
                    print("\nIndexing stats:")
                    print(f"- Blocks scanned: {stats['blocks_scanned']:,}")
                    print(f"- Events found: {stats['events_found']:,}")
                    print(f"- Errors: {stats['errors']}")
                    
                    current_block = end_block + 1
                    time.sleep(2)
                else:
                    print(f"\n⏳ Waiting for new blocks...")
                    print(f"Current position: {current_block:,}")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"\n⚠️ Error: {e}")
                stats["errors"] += 1
                time.sleep(10)

    def _format_event(self, event):
        """Formate un événement pour le stockage
        
        Args:
            event: L'événement Web3 brut
            
        Returns:
            dict: Les données de l'événement formatées pour le stockage
        """
        return {
            "userOpHash": event.args.userOpHash.hex(),
            "sender": event.args.sender,
            "paymaster": event.args.paymaster,
            "nonce": str(event.args.nonce),
            "success": event.args.success,
            "actualGasCost": str(event.args.actualGasCost),
            "actualGasUsed": str(event.args.actualGasUsed),
            "blockNumber": event.blockNumber,
            "timestamp": datetime.now().isoformat()
        }

    def _save_event(self, event_data):
        """Sauvegarde un événement"""
        save_event(event_data)