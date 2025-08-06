import requests
import json

def fetch_imex_details(bill_id: int) -> list[dict] | None:
    """
    Gọi API lấy chi tiết danh sách imex cho bill_id.
    Trả về list dict, mỗi dict có các trường:
        requiredQuantity, damagedQuantity, approvedQuantity, realQuantity
    Hoặc None nếu lỗi.
    """
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
                imexs = res_json.get("data", {}).get("imexs", {})
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
                        "toDepotId": item.get("toDepotId", ""),
                    })
                return result
        except Exception:
            return None
    return None
