# rwanly Core ERP - Backend

This is the FastAPI backend for the rwanly Core ERP system.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

3. **Database Setup**
   ```bash
   # Make sure PostgreSQL is running
   # Create database and user:
   createdb rwanly_db
   createuser rwanly_user
   
   # Initialize database tables and sample data
   python init_db.py
   ```

4. **Run Database Migrations (if needed)**
   ```bash
   alembic upgrade head
   ```

5. **Start the Server**
   ```bash
   # Development
   uvicorn main:app --reload
   
   # Production
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Default Credentials

After running `init_db.py`:
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default password in production!

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Security and permissions
│   ├── crud/          # Database operations
│   ├── database/      # Database configuration
│   ├── models/        # SQLAlchemy models
│   └── schemas/       # Pydantic schemas
├── alembic/           # Database migrations
├── main.py           # FastAPI application
├── init_db.py        # Database initialization
└── requirements.txt  # Python dependencies
```

## Features Implemented

### Core System
- ✅ User Management (REQ-SYS-UM-*)
- ✅ Role-Based Access Control (REQ-SYS-RBAC-*)
- ✅ Company Setup (REQ-SYS-COMP-*)
- ✅ JWT Authentication
- ✅ Permission-based API protection

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

#### Users
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `POST /api/users/{id}/assign-role` - Assign role to user

#### Companies
- `GET /api/companies` - List companies
- `POST /api/companies` - Create company
- `GET /api/companies/{id}` - Get company
- `PUT /api/companies/{id}` - Update company

#### Roles
- `GET /api/roles` - List roles
- `POST /api/roles` - Create role
- `GET /api/roles/{id}` - Get role
- `PUT /api/roles/{id}` - Update role
- `DELETE /api/roles/{id}` - Delete role
- `GET /api/roles/permissions/all` - List all permissions

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Modules

1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Create CRUD operations in `app/crud/`
4. Create API routes in `app/api/`
5. Add permissions in `app/core/permissions.py`
6. Update the main router in `app/api/__init__.py`

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Role-based access control on all endpoints
- Company-level data isolation
- Input validation with Pydantic

## Next Steps

1. Add Accounting Periods module
2. Implement General Ledger module
3. Add Accounts Receivable module
4. Add Accounts Payable module
5. Implement Inventory module
6. Create Order Entry module
