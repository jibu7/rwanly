#!/usr/bin/env python3
"""
Database Cleanup Script
This script cleans all business data from the database to prevent duplicates
when re-loading sample data. It preserves the database structure.
"""

import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models.core import *


def clean_all_data(db: Session):
    """Clean all business data from database in proper order to respect foreign keys."""
    print("🧹 Starting database cleanup...")
    
    # List of tables to clean in order (respecting foreign key constraints)
    # Most dependent tables first, then their dependencies
    cleanup_order = [
        # Order Entry - Most dependent
        'grv_lines',
        'goods_received_vouchers',
        'purchase_order_lines',
        'sales_order_lines',
        'purchase_orders',
        'sales_orders',
        'oe_document_types',
        
        # Allocations and Transactions
        'ar_allocations',
        'ar_transactions',
        'ap_allocations', 
        'ap_transactions',
        'inventory_transactions',
        'gl_transactions',
        
        # Transaction Types
        'ar_transaction_types',
        'ap_transaction_types',
        'inventory_transaction_types',
        
        # Master Data
        'inventory_items',
        'customers',
        'suppliers',
        'ageing_periods',
        'gl_accounts',
        'accounting_periods',
        
        # User management (preserve structure but clean data)
        'user_roles',
        'roles',
        'users',
        
        # Companies (this will cascade delete everything)
        'companies'
    ]
    
    try:
        # Disable foreign key checks temporarily (PostgreSQL specific)
        db.execute(text("SET session_replication_role = 'replica';"))
        
        for table in cleanup_order:
            try:
                result = db.execute(text(f"DELETE FROM {table}"))
                count = result.rowcount
                print(f"  ✓ Cleaned {table}: {count} records deleted")
            except Exception as e:
                print(f"  ⚠️  Warning cleaning {table}: {str(e)}")
        
        # Re-enable foreign key checks
        db.execute(text("SET session_replication_role = 'origin';"))
        
        # Reset sequences to start from 1
        print("\n🔄 Resetting sequences...")
        sequence_reset_queries = [
            "ALTER SEQUENCE companies_id_seq RESTART WITH 1",
            "ALTER SEQUENCE users_id_seq RESTART WITH 1", 
            "ALTER SEQUENCE roles_id_seq RESTART WITH 1",
            "ALTER SEQUENCE accounting_periods_id_seq RESTART WITH 1",
            "ALTER SEQUENCE gl_accounts_id_seq RESTART WITH 1",
            "ALTER SEQUENCE gl_transactions_id_seq RESTART WITH 1",
            "ALTER SEQUENCE customers_id_seq RESTART WITH 1",
            "ALTER SEQUENCE suppliers_id_seq RESTART WITH 1",
            "ALTER SEQUENCE ar_transaction_types_id_seq RESTART WITH 1",
            "ALTER SEQUENCE ap_transaction_types_id_seq RESTART WITH 1",
            "ALTER SEQUENCE ar_transactions_id_seq RESTART WITH 1",
            "ALTER SEQUENCE ap_transactions_id_seq RESTART WITH 1",
            "ALTER SEQUENCE inventory_items_id_seq RESTART WITH 1",
            "ALTER SEQUENCE inventory_transaction_types_id_seq RESTART WITH 1",
            "ALTER SEQUENCE inventory_transactions_id_seq RESTART WITH 1",
            "ALTER SEQUENCE oe_document_types_id_seq RESTART WITH 1",
            "ALTER SEQUENCE sales_orders_id_seq RESTART WITH 1",
            "ALTER SEQUENCE purchase_orders_id_seq RESTART WITH 1",
            "ALTER SEQUENCE goods_received_vouchers_id_seq RESTART WITH 1"
        ]
        
        for query in sequence_reset_queries:
            try:
                db.execute(text(query))
                print(f"  ✓ Reset sequence: {query.split()[2]}")
            except Exception as e:
                print(f"  ⚠️  Warning resetting sequence: {str(e)}")
        
        db.commit()
        print("\n✅ Database cleanup completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during cleanup: {str(e)}")
        raise


def vacuum_database():
    """Run VACUUM to reclaim space after cleanup."""
    try:
        print("\n🧽 Running VACUUM to reclaim space...")
        # Create a new connection for VACUUM (cannot run in transaction)
        vacuum_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
        with vacuum_engine.connect() as conn:
            conn.execute(text("VACUUM ANALYZE"))
        print("✅ VACUUM completed successfully!")
    except Exception as e:
        print(f"⚠️  Warning during VACUUM: {str(e)}")


def main():
    """Main cleanup function."""
    print("=" * 60)
    print("🗑️  DATABASE CLEANUP SCRIPT")
    print("=" * 60)
    print("This script will delete ALL business data from the database.")
    print("The database structure will be preserved.")
    print()
    
    # Safety check
    confirm = input("⚠️  Are you sure you want to proceed? Type 'YES' to continue: ")
    if confirm != 'YES':
        print("❌ Cleanup cancelled.")
        return
    
    # Additional confirmation for production
    if os.getenv('ENVIRONMENT', 'development').lower() == 'production':
        prod_confirm = input("🚨 PRODUCTION ENVIRONMENT DETECTED! Type 'DELETE_PRODUCTION_DATA' to continue: ")
        if prod_confirm != 'DELETE_PRODUCTION_DATA':
            print("❌ Production cleanup cancelled.")
            return
    
    db = SessionLocal()
    try:
        clean_all_data(db)
        vacuum_database()
        
        print("\n" + "=" * 60)
        print("✅ CLEANUP COMPLETED SUCCESSFULLY!")
        print("The database is now ready for fresh sample data.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ CLEANUP FAILED: {str(e)}")
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    exit(main())
