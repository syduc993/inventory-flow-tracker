# main.py - Entry Point (Đã tối ưu)
import uvicorn
import os
from src.core.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
