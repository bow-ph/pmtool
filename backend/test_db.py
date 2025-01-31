from app.core.database import engine

print('Testing connection...')
try:
    engine.connect()
    print('Connection successful!')
except Exception as e:
    print(f'Connection failed: {e}')
