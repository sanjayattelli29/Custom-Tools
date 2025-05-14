import os
import sys

def check_file_for_null_bytes(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if b'\x00' in content:
                return True
            return False
    except Exception as e:
        print(f"Error checking {file_path}: {str(e)}")
        return False

def main():
    backend_dir = os.path.join(os.getcwd(), 'backend')
    
    print(f"Checking for null bytes in Python files under {backend_dir}")
    
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if check_file_for_null_bytes(file_path):
                    print(f"Found null bytes in: {file_path}")

if __name__ == "__main__":
    main()
