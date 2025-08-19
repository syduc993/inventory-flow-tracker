import requests
import json
import logging

def fetch_imex_details(bill_id: int) -> list[dict] | None:
    url = "https://open.nhanh.vn/api/bill/imexrequirements"
    payload = {
        "version": "2.0",
        "appId": "74951",
        "businessId": "8901",
        "accessToken": "twf9P1xFZCUUgwt8zR0XgNeB6V5jsbq2KHb14bxovqK1ppCxyADwOK8FzQlCEeEGABRZINXoUCSzM50kjhwcrUSBWTY5nSvyhfnH2X2cI0pC7pNczSVxc1ratdDmxF85q7hUTUNCrUnpPTG5ZwLNO7bkMlEEJTCdPhgYaC",
        "data": json.dumps({"billId": int(bill_id)})
    }
    res = requests.post(url, data=payload)
    if res.status_code == 200:
        try:
            res_json = res.json()
            if res_json.get("code") == 1:
                data = res_json.get("data")
                if not data:
                    return None
                    
                imexs = data.get("imexs")
                if not imexs:
                    return None
                    
                result = []
                for item in imexs.values():
                    result.append({
                        "requiredQuantity": item.get("requiredQuantity", ""),
                        "damagedQuantity": item.get("damagedQuantity", ""),
                        "approvedQuantity": item.get("approvedQuantity", ""),
                        "realQuantity": item.get("realQuantity", ""),
                        "approvedByUser": item.get("approvedByUser", ""),
                        "requiredAt": item.get("requiredAt", ""),
                        "approvedAt": item.get("approvedAt", ""),
                        "confirmedAt": item.get("confirmedAt", ""),
                        "fromDepotId": item.get("fromDepotId", ""),
                        "fromDepotName": item.get("fromDepotName", ""),
                        "toDepotId": item.get("toDepotId", ""),
                        "toDepotName": item.get("toDepotName", ""),
                        "status": item.get("status", "")
                    })
                return result
        except Exception as e:
            logging.error(f"Lỗi khi parse JSON: {e}")
            return None
    return None

