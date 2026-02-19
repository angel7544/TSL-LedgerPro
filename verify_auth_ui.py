
import sys
import os
from PySide6.QtWidgets import QApplication
from auth.ui import LoginWindow

# Mock database and session if needed, but UI should load regardless
# We might need to mock execute_read_query if it's called in __init__
import database.db

def mock_read_query(query, params=()):
    print(f"Mock Query: {query}")
    if "SELECT COUNT(*) FROM users" in query:
        return [(0,)] # Simulate no users to show signup link
    if "SELECT id FROM users" in query:
        return [(1,)] # Simulate user found
    return []

database.db.execute_read_query = mock_read_query

def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    print("Login Window displayed successfully.")
    # In a real test we might not want to block, but for manual verification or just checking for crash:
    # sys.exit(app.exec()) 
    
    # Just check if it initialized
    if window.isVisible():
        print("Window is visible.")
    
    app.quit()

if __name__ == "__main__":
    main()
