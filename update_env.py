import secrets
import os

def generate_secrets():
    return {
        'JWT_SECRET': secrets.token_hex(32),
        'SESSION_SECRET': secrets.token_hex(32)
    }

def update_env_file(env_path):
    try:
        # Generate new secrets
        new_secrets = generate_secrets()
        
        # Read existing .env file
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update or append secrets
        updated_lines = []
        existing_keys = set()
        
        for line in lines:
            key = line.split('=')[0].strip() if '=' in line else None
            if key in new_secrets:
                updated_lines.append(f"{key}={new_secrets[key]}\n")
                existing_keys.add(key)
            else:
                updated_lines.append(line)
        
        # Add any missing secrets
        for key, value in new_secrets.items():
            if key not in existing_keys:
                updated_lines.append(f"{key}={value}\n")
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
            
        print("Environment file updated successfully")
        return True
    except Exception as e:
        print(f"Error updating environment file: {str(e)}")
        return False

if __name__ == '__main__':
    env_path = '/var/www/docuplanai/backend/.env'
    if update_env_file(env_path):
        print("Successfully updated environment variables")
    else:
        print("Failed to update environment variables")
        exit(1)
