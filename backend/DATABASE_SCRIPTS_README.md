# Database Management Scripts

This directory contains scripts for managing your ERP database with comprehensive business data.

## 🎯 Quick Start

Run the master setup script for an interactive menu:
```bash
python setup_database.py
```

## 📋 Available Scripts

### 1. `setup_database.py` - Master Controller
Interactive script that provides menu options for all database operations.

**Features:**
- Clean database only
- Load business data only  
- Complete clean and reload (recommended)
- User-friendly menu interface

### 2. `cleanup_database.py` - Database Cleaner
Safely removes all business data while preserving database structure.

**Features:**
- Respects foreign key constraints
- Resets auto-increment sequences
- Safety confirmations
- Production environment protection
- VACUUM operation for space reclamation

**Usage:**
```bash
python cleanup_database.py
```

### 3. `load_business_data.py` - Business Data Loader
Loads comprehensive business data for a functional ERP system.

**Data Loaded:**
- **Company**: Tech Solutions Inc. with complete profile
- **Chart of Accounts**: 33 accounts covering all business areas
- **Users**: Admin user with full permissions
- **Accounting Periods**: 12 months for current year
- **Customers**: 5 sample customers with credit limits
- **Suppliers**: 5 sample suppliers with payment terms
- **Inventory Items**: 12 items (hardware, software, services)
- **Transaction Types**: AR, AP, and Inventory types
- **Document Types**: Sales Orders, Purchase Orders, GRV
- **Sample Transactions**: Invoices, bills, inventory movements

**Usage:**
```bash
python load_business_data.py
```

## 🏢 Sample Business Data Overview

### Company Profile
- **Name**: Tech Solutions Inc.
- **Industry**: Technology solutions and services
- **Location**: Tech City, CA, USA
- **Currency**: USD
- **Tax Rate**: 8.5%

### Chart of Accounts (33 accounts)
- **Assets**: Cash, AR, Inventory, Equipment
- **Liabilities**: AP, Accruals, Loans
- **Equity**: Owner's equity, Retained earnings
- **Revenue**: Sales, Services, Other income
- **Expenses**: COGS, Operating expenses, Financial costs

### Master Data
- **5 Customers**: ABC Corp, XYZ Industries, Global Tech Solutions, Metro Services, Innovation Labs
- **5 Suppliers**: Tech Components Inc., Office Supplies Co., Hardware Solutions, Software Vendors, Equipment Rental
- **12 Inventory Items**: Laptops, desktops, monitors, peripherals, software, services

### Sample Transactions
- Customer invoices with tax calculations
- Supplier bills with payment terms
- Inventory purchases and sales
- Proper GL posting and period allocation

## 🔒 Safety Features

### Data Protection
- **Confirmation prompts** prevent accidental deletion
- **Production environment protection** requires special confirmation
- **Foreign key respect** ensures clean deletion order
- **Transaction rollback** on any errors

### Database Integrity
- **Sequence resets** ensure clean ID numbering
- **VACUUM operation** reclaims space after cleanup
- **Proper commit/rollback** handling
- **Relationship validation** during data creation

## 🚀 Usage Scenarios

### Development Setup
```bash
# Clean slate for development
python setup_database.py
# Choose option 3: Clean and reload all data
```

### Testing Environment
```bash
# Reset between test runs
python cleanup_database.py
python load_business_data.py
```

### Production Migration
```bash
# Load business data to new production system
python load_business_data.py
```

## 📊 Expected Results

After running the complete setup, your ERP system will have:

- ✅ Full chart of accounts with proper classifications
- ✅ Sample customers with outstanding invoices
- ✅ Sample suppliers with pending bills  
- ✅ Inventory items with stock on hand
- ✅ Transaction types for all modules
- ✅ Document types for order processing
- ✅ Admin user for system access
- ✅ Current accounting period open
- ✅ Sample GL transactions posted

## 🔧 Troubleshooting

### Common Issues

**Permission Errors:**
```bash
chmod +x *.py
```

**Database Connection:**
Check your `.env` file for correct DATABASE_URL

**Dependency Errors:**
```bash
pip install -r requirements.txt
```

**Foreign Key Violations:**
Run cleanup script first before loading new data

### Script Execution Order
1. Always run cleanup before loading new data
2. Don't run partial loads (always use complete dataset)
3. Check for existing data before running loaders

## 📈 Extending the Data

The business data loader is designed to be easily extensible:

1. **Add more accounts** in `create_chart_of_accounts()`
2. **Add customers/suppliers** in respective creation methods
3. **Add inventory items** in `create_inventory_items()`
4. **Add sample transactions** in `create_sample_transactions()`

Each section is modular and can be enhanced based on your business needs.

---

## 💡 Pro Tips

- Use option 3 (clean and reload) for development
- Keep backups before running cleanup in production
- Customize the sample data to match your business
- Run scripts during low-usage periods
- Monitor disk space during VACUUM operations
