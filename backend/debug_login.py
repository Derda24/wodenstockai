#!/usr/bin/env python3

from main import get_admin_users, hash_password

def debug_login():
    print("=== Debug Login ===")
    
    # Get admin users
    users = get_admin_users()
    print(f"Total admin users: {len(users)}")
    
    for i, user in enumerate(users):
        print(f"User {i+1}: {user.username}")
        print(f"  Hash: {user.password_hash}")
    
    # Test password hash
    test_password = "woden2025"
    test_hash = hash_password(test_password)
    print(f"\nTest password: {test_password}")
    print(f"Test hash: {test_hash}")
    
    # Check if derda2412 exists
    derda_user = next((u for u in users if u.username == "derda2412"), None)
    if derda_user:
        print(f"\nderda2412 user found:")
        print(f"  Stored hash: {derda_user.password_hash}")
        print(f"  Test hash:   {test_hash}")
        print(f"  Match: {derda_user.password_hash == test_hash}")
    else:
        print("\nderda2412 user NOT found!")
    
    # Test verification
    from main import verify_user
    result = verify_user("derda2412", "woden2025")
    print(f"\nverify_user('derda2412', 'woden2025'): {result}")

if __name__ == "__main__":
    debug_login()
