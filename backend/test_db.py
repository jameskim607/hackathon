# backend/test_db.py
from sqlalchemy import create_engine, text

# Test database connection
try:
    # Update with your MySQL credentials
    engine = create_engine("mysql+pymysql://root:password@localhost/african_lms")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print(f"Result: {result.scalar()}")
except Exception as e:
    print(f"Database connection failed: {e}")