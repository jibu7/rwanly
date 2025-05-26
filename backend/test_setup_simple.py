#!/usr/bin/env python3
"""
Simple AR setup script for debugging
"""

import sys
import os
import traceback

# Add the project root to the Python path
sys.path.append(os.getcwd())

def main():
    try:
        print("Starting AR setup...")
        
        from app.database import engine
        from sqlalchemy.orm import Session
        from app.models.core import Company
        
        print("Creating database session...")
        db = Session(engine)
        
        print("Querying companies...")
        companies = db.query(Company).filter(Company.is_active == True).all()
        print(f"Found {len(companies)} companies")
        
        for company in companies:
            print(f"Company: {company.name} (ID: {company.id})")
        
        db.close()
        print("Setup completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
