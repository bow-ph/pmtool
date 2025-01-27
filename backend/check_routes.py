from app.main import app
from fastapi.middleware.cors import CORSMiddleware

def check_routes():
    print("Available Routes:")
    for route in app.routes:
        print(f'{route.methods} {route.path}')

def check_cors():
    print("\nCORS Configuration:")
    for middleware in app.user_middleware:
        if isinstance(middleware, CORSMiddleware):
            print(f"CORS Middleware found")
            print(f"Allow origins: {middleware.options.get('allow_origins', [])}")
            print(f"Allow methods: {middleware.options.get('allow_methods', [])}")
            print(f"Allow headers: {middleware.options.get('allow_headers', [])}")
            return
    print("No CORS middleware configured")

if __name__ == "__main__":
    check_routes()
    check_cors()
