"""
IMS Immutable Blockchain Audit Trail Engine (SHA-256 Cryptographic Hash Chain)
Provides tamper-proof maintenance records for nuclear power and aerospace compliance standards.
"""

import os
import sys
import json
import hashlib
import time
from typing import List, Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import RESULTS_DIR

class BearingAuditBlock:
    """Represents a single block in the cryptographic maintenance ledger."""
    def __init__(self, index: int, timestamp: float, data: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_str = f"{self.index}{self.timestamp}{json.dumps(self.data, sort_keys=True)}{self.previous_hash}"
        return hashlib.sha256(block_str.encode("utf-8")).hexdigest()

class BlockchainAuditLedger:
    """
    Manages the cryptographic append-only ledger for bearing health records.
    """

    def __init__(self):
        self.chain: List[BearingAuditBlock] = [self._create_genesis_block()]
        self.ledger_file = os.path.join(RESULTS_DIR, "blockchain_audit_ledger.json")

    def _create_genesis_block(self) -> BearingAuditBlock:
        return BearingAuditBlock(0, time.time(), {"genesis": "IMS Bearing Audit Blockchain Genesis Block"}, "0"*64)

    def get_latest_block(self) -> BearingAuditBlock:
        return self.chain[-1]

    def add_audit_record(self, asset_id: str, health_index: float, status: str, action: str) -> BearingAuditBlock:
        """Appends a new verified health record block to the hash chain."""
        prev_block = self.get_latest_block()
        data = {
            "asset_id": asset_id,
            "health_index": round(health_index, 4),
            "status": status,
            "action_taken": action
        }
        new_block = BearingAuditBlock(len(self.chain), time.time(), data, prev_block.hash)
        self.chain.append(new_block)

        self._save_ledger()
        print(f"[SUCCESS] Block #{new_block.index} added to Blockchain Hash: {new_block.hash[:16]}...")
        return new_block

    def is_chain_valid(self) -> bool:
        """Verifies cryptographic hash integrity of the entire chain."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.hash != curr.calculate_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
        return True

    def _save_ledger(self):
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        serializable = [
            {"index": b.index, "timestamp": b.timestamp, "data": b.data, "previous_hash": b.previous_hash, "hash": b.hash}
            for b in self.chain
        ]
        with open(self.ledger_file, "w") as f:
            json.dump(serializable, f, indent=2)

if __name__ == "__main__":
    ledger = BlockchainAuditLedger()
    ledger.add_audit_record("PUMP-01-BRG1", 0.95, "HEALTHY", "Normal inspection")
    ledger.add_audit_record("PUMP-01-BRG1", 0.42, "WARNING", "Vibration surge recorded")
    print(f"Blockchain Ledger Valid: {ledger.is_chain_valid()}")
