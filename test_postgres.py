from src.database.connection import get_db
from src.database.models import Customer, Interaction, Document

def test_postgres():
    print("\n=== Testing PostgreSQL Connection ===")
    try:
        # Create a database session
        db = next(get_db())
        
        # Get counts
        customer_count = db.query(Customer).count()
        interaction_count = db.query(Interaction).count()
        document_count = db.query(Document).count()
        
        print("\nDatabase Status:")
        print(f"Customers: {customer_count}")
        print(f"Interactions: {interaction_count}")
        print(f"Documents: {document_count}")
        
        if interaction_count > 0:
            print("\nLatest Interactions:")
            latest = db.query(Interaction).order_by(Interaction.created_at.desc()).limit(3).all()
            for interaction in latest:
                print(f"\nFrom: {interaction.customer.phone_number}")
                print(f"Message: {interaction.message}")
                print(f"Response: {interaction.response}")
                print(f"Time: {interaction.created_at}")
        
        db.close()
        print("\nPostgreSQL connection test completed successfully!")
        
    except Exception as e:
        print(f"PostgreSQL Error: {str(e)}")

if __name__ == "__main__":
    test_postgres() 