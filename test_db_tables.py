from src.database.connection import get_db
from sqlalchemy import inspect

def check_tables():
    print("\n=== Checking Database Tables ===")
    try:
        # Get database connection
        db = next(get_db())
        
        # Get inspector
        inspector = inspect(db.bind)
        
        # Get all table names
        tables = inspector.get_table_names()
        
        print("\nExisting tables:")
        for table in tables:
            print(f"\nTable: {table}")
            # Get columns for each table
            columns = inspector.get_columns(table)
            print("Columns:")
            for column in columns:
                print(f"  - {column['name']} ({column['type']})")
        
        db.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_tables() 