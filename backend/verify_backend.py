from app.schemas.invoice import InvoiceResponse
import requests
import psutil
import socket

def check_schema():
    try:
        print("Checking InvoiceResponse schema...")
        schema = InvoiceResponse.model_json_schema()
        print("Schema loaded successfully")
        return True
    except Exception as e:
        print(f"Schema error: {str(e)}")
        return False

def check_service():
    try:
        print("\nChecking uvicorn service...")
        uvicorn_running = False
        for proc in psutil.process_iter(['name', 'cmdline']):
            if 'uvicorn' in str(proc.info['name']):
                print(f"Found uvicorn process: {proc.pid}")
                uvicorn_running = True
                break
        if not uvicorn_running:
            print("No uvicorn process found")
            return False
        return True
    except Exception as e:
        print(f"Service check error: {str(e)}")
        return False

def check_port():
    try:
        print("\nChecking port 8000...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        if result == 0:
            print("Port 8000 is open")
            return True
        print("Port 8000 is not accessible")
        return False
    except Exception as e:
        print(f"Port check error: {str(e)}")
        return False

def check_api():
    try:
        print("\nChecking API health...")
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            print("API is healthy")
            return True
        print(f"API health check failed: {response.status_code}")
        return False
    except Exception as e:
        print(f"API check error: {str(e)}")
        return False

if __name__ == '__main__':
    schema_ok = check_schema()
    service_ok = check_service()
    port_ok = check_port()
    api_ok = check_api()
    
    if all([schema_ok, service_ok, port_ok, api_ok]):
        print("\nAll checks passed successfully")
        exit(0)
    else:
        print("\nSome checks failed")
        exit(1)
