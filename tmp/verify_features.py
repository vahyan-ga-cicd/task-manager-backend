import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.admin.admin_service import get_all_users, create_user_by_admin, get_users_short_list
from app.services.task_service import assign_task, get_tasks, get_all_tasks_public

def test_features():
    print("Starting verification of Task Management features...")
    
    # 1. Check all users
    users = get_all_users()
    admin_user = next((u for u in users if u['role'] == 'admin'), None)
    if not admin_user:
        print("Error: No admin user found for testing.")
        return
    print(f"Admin user found: {admin_user['username']} ({admin_user['user_id']})")
    
    # 2. Create a new user via Admin
    test_email = "employee_test@example.com"
    # Clean up if exists (though for test script we just use a unique name)
    try:
        new_user = create_user_by_admin("TestEmployee", test_email, "pass123", role="user")
        user_id = new_user['user']['user_id']
        print(f"Successfully created user: {user_id}")
    except Exception as e:
        print(f"User creation failed (might already exist): {e}")
        # Try to find it
        user_id = next((u['user_id'] for u in users if u['email'] == test_email), None)
        if not user_id:
            print("Could not find or create test user.")
            return

    # 3. Assign a task to the new user
    print(f"Assigning task to user {user_id}...")
    task = assign_task(
        assigned_to_id=user_id,
        assigned_by_id=admin_user['user_id'],
        title="Verification Task",
        description="Verify this task appears in employee dashboard",
        deadline="2026-12-31"
    )
    print(f"Task assigned: {task['task_id']}")
    
    # 4. Verify user can see their task
    user_tasks = get_tasks(user_id)
    found = any(t['task_id'] == task['task_id'] for t in user_tasks['data'])
    if found:
        print("Success: Task found in user's task list.")
    else:
        print("Error: Task NOT found in user's task list.")
        
    # 5. Verify public list shows the task
    public_tasks = get_all_tasks_public()
    found_public = any(t['task_id'] == task['task_id'] for t in public_tasks)
    if found_public:
        print("Success: Task found in public task list.")
    else:
        print("Error: Task NOT found in public task list.")
        
    # 6. Verify users short list for dropdown
    short_list = get_users_short_list()
    if any(u['user_id'] == user_id for u in short_list):
        print("Success: New user found in admin dropdown list.")
    else:
        print("Error: New user NOT found in admin dropdown list.")

if __name__ == "__main__":
    test_features()
