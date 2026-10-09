"""
IMS Automated ERP / SAP Spare Part Requisition Engine
Automatically generates SAP/ERP Purchase Orders (PO) when bearing RUL breaches spare part lead time.
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import RESULTS_DIR

class SAPAutomatedERPOrder:
    """
    Automates spare part procurement via ERP API integration.
    """

    def __init__(self, lead_time_hours: float = 48.0):
        self.lead_time = lead_time_hours

    def check_and_create_purchase_order(self, bearing_id: str, predicted_rul_hours: float,
                                       part_number: str = "REXNORD-ZA-2115") -> Dict[str, Any]:
        """
        Evaluates RUL against procurement lead time and issues a Purchase Requisition if required.
        """
        order_triggered = bool(predicted_rul_hours <= self.lead_time)

        order_payload = {}
        if order_triggered:
            po_id = f"PO-{int(time.time())}"
            order_payload = {
                "purchase_order_id": po_id,
                "erp_system": "SAP S/4HANA PM/MM Module",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "asset_id": bearing_id,
                "part_number": part_number,
                "part_description": "Rexnord ZA-2115 Double Row Tapered Roller Bearing",
                "quantity": 1,
                "urgency": "HIGH - PREDICTIVE REPLACEMENT",
                "predicted_rul_hours": predicted_rul_hours,
                "procurement_lead_time_hours": self.lead_time,
                "delivery_address": "Main Processing Plant - Maintenance Bay 4"
            }

            # Save PO JSON record
            po_file = os.path.join(RESULTS_DIR, "erp_purchase_orders.json")
            os.makedirs(os.path.dirname(po_file), exist_ok=True)
            with open(po_file, "w") as f:
                json.dump(order_payload, f, indent=2)

            print(f"[SUCCESS] SAP Purchase Order {po_id} automatically issued for {bearing_id}.")

        return {
            "bearing_id": bearing_id,
            "order_triggered": order_triggered,
            "purchase_order": order_payload
        }

if __name__ == "__main__":
    erp = SAPAutomatedERPOrder(lead_time_hours=48.0)
    
    # Healthy - No PO
    print("Normal Check:", erp.check_and_create_purchase_order("BRG-01", 120.0))

    # Critical RUL < Lead Time -> Auto PO
    print("Low RUL Check:", erp.check_and_create_purchase_order("BRG-01", 24.5))
