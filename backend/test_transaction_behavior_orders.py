"""
Transaction & Document Processing Behavior Tests - Order Entry Documents

This module tests the specific business behaviors for Order Entry Documents as described 
in the CRUD_Testing_Checklist.md:

5. Order Entry Documents:
   - Create Sales Orders and verify they appear in listing
   - Create Purchase Orders and verify they appear in listing  
   - Create GRV (Goods Receipt Voucher) and verify inventory updates
   - Create Supplier Invoices and verify conversions
   - Test document conversions (SO->Invoice, PO->GRV->Supplier Invoice)
   - Verify document status updates throughout the process
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, date

from app.main import app
from app.database.base import get_db
from app.models.sales import SalesOrder, SalesOrderLine
from app.models.purchasing import PurchaseOrder, PurchaseOrderLine, GoodsReceiptVoucher, GRVLine
from app.models.accounts_payable import APTransaction
from app.models.accounts_receivable import ARTransaction
from app.models.inventory import Item
from app.models.general_ledger import GLAccount
from app.models.core import Customer, Supplier
from app.models.auth import User
from app.crud.sales import create_sales_order, get_sales_orders, convert_so_to_invoice
from app.crud.purchasing import create_purchase_order, get_purchase_orders, create_grv, convert_grv_to_invoice
from app.crud.inventory import get_item_by_code
from app.schemas.sales import SalesOrderCreate, SalesOrderLineCreate
from app.schemas.purchasing import PurchaseOrderCreate, PurchaseOrderLineCreate, GRVCreate, GRVLineCreate
from app.core.security import create_access_token

client = TestClient(app)


class TestOrderEntryDocumentsBehavior:
    """Test class for Order Entry Documents transaction behavior"""

    @pytest.fixture(autouse=True)
    def setup_order_test_data(self, db: Session, test_user):
        """Set up test data for order entry document tests"""
        self.db = db
        self.test_user = test_user
        
        # Create test customer
        self.test_customer = Customer(
            code="CUST001",
            name="Test Customer Ltd",
            contact_person="John Doe",
            email="customer@test.com",
            phone="123-456-7890",
            address="123 Customer St",
            credit_limit=Decimal("10000.00"),
            is_active=True
        )
        
        # Create test supplier
        self.test_supplier = Supplier(
            code="SUPP001",
            name="Test Supplier Inc",
            contact_person="Jane Smith",
            email="supplier@test.com",
            phone="098-765-4321",
            address="456 Supplier Ave",
            credit_limit=Decimal("50000.00"),
            is_active=True
        )
        
        db.add_all([self.test_customer, self.test_supplier])
        db.commit()
        
        # Create test inventory items
        self.test_item1 = Item(
            code="ITEM001",
            name="Test Product 1",
            description="First test product",
            unit_of_measure="EA",
            current_cost=Decimal("25.00"),
            selling_price=Decimal("40.00"),
            quantity_on_hand=Decimal("100.00"),
            reorder_level=Decimal("10.00"),
            is_active=True
        )
        
        self.test_item2 = Item(
            code="ITEM002",
            name="Test Product 2",
            description="Second test product",
            unit_of_measure="EA",
            current_cost=Decimal("15.00"),
            selling_price=Decimal("25.00"),
            quantity_on_hand=Decimal("50.00"),
            reorder_level=Decimal("5.00"),
            is_active=True
        )
        
        db.add_all([self.test_item1, self.test_item2])
        db.commit()
        db.refresh(self.test_customer)
        db.refresh(self.test_supplier)
        db.refresh(self.test_item1)
        db.refresh(self.test_item2)

    def test_sales_order_creation_and_listing(self, db: Session):
        """Test Sales Order creation and verify it appears in listing"""
        # Create sales order
        so_lines = [
            SalesOrderLineCreate(
                item_id=self.test_item1.id,
                quantity=Decimal("5.00"),
                unit_price=self.test_item1.selling_price,
                discount_percent=Decimal("0.00")
            ),
            SalesOrderLineCreate(
                item_id=self.test_item2.id,
                quantity=Decimal("3.00"),
                unit_price=self.test_item2.selling_price,
                discount_percent=Decimal("5.00")
            )
        ]
        
        so_data = SalesOrderCreate(
            customer_id=self.test_customer.id,
            order_date=date.today(),
            reference="SO-TEST-001",
            notes="Test sales order",
            lines=so_lines
        )
        
        # Process the sales order
        sales_order = create_sales_order(db, so_data, self.test_user.id)
        
        # Verification 1: Sales order created successfully
        assert sales_order is not None
        assert sales_order.reference == "SO-TEST-001"
        assert sales_order.status == "Open"
        assert len(sales_order.lines) == 2
        
        # Verification 2: Sales order appears in listing
        sales_orders = get_sales_orders(db)
        so_references = [so.reference for so in sales_orders]
        assert "SO-TEST-001" in so_references
        
        # Verification 3: Order total calculated correctly
        expected_total = (Decimal("5.00") * Decimal("40.00")) + (Decimal("3.00") * Decimal("25.00") * Decimal("0.95"))
        assert abs(sales_order.total_amount - expected_total) < Decimal("0.01")
        
        return sales_order

    def test_purchase_order_creation_and_listing(self, db: Session):
        """Test Purchase Order creation and verify it appears in listing"""
        # Create purchase order
        po_lines = [
            PurchaseOrderLineCreate(
                item_id=self.test_item1.id,
                quantity=Decimal("20.00"),
                unit_cost=self.test_item1.current_cost,
                discount_percent=Decimal("0.00")
            ),
            PurchaseOrderLineCreate(
                item_id=self.test_item2.id,
                quantity=Decimal("15.00"),
                unit_cost=self.test_item2.current_cost,
                discount_percent=Decimal("2.50")
            )
        ]
        
        po_data = PurchaseOrderCreate(
            supplier_id=self.test_supplier.id,
            order_date=date.today(),
            reference="PO-TEST-001",
            notes="Test purchase order",
            lines=po_lines
        )
        
        # Process the purchase order
        purchase_order = create_purchase_order(db, po_data, self.test_user.id)
        
        # Verification 1: Purchase order created successfully
        assert purchase_order is not None
        assert purchase_order.reference == "PO-TEST-001"
        assert purchase_order.status == "Open"
        assert len(purchase_order.lines) == 2
        
        # Verification 2: Purchase order appears in listing
        purchase_orders = get_purchase_orders(db)
        po_references = [po.reference for po in purchase_orders]
        assert "PO-TEST-001" in po_references
        
        # Verification 3: Order total calculated correctly
        expected_total = (Decimal("20.00") * Decimal("25.00")) + (Decimal("15.00") * Decimal("15.00") * Decimal("0.975"))
        assert abs(purchase_order.total_amount - expected_total) < Decimal("0.01")
        
        return purchase_order

    def test_grv_creation_and_inventory_updates(self, db: Session):
        """Test GRV creation and verify inventory updates"""
        # First create a purchase order
        purchase_order = self.test_purchase_order_creation_and_listing(db)
        
        # Record initial inventory quantities
        initial_qty_item1 = self.test_item1.quantity_on_hand
        initial_qty_item2 = self.test_item2.quantity_on_hand
        
        # Create GRV
        grv_lines = [
            GRVLineCreate(
                purchase_order_line_id=purchase_order.lines[0].id,
                item_id=self.test_item1.id,
                quantity_received=Decimal("18.00"),  # Partial receipt
                unit_cost=self.test_item1.current_cost
            ),
            GRVLineCreate(
                purchase_order_line_id=purchase_order.lines[1].id,
                item_id=self.test_item2.id,
                quantity_received=Decimal("15.00"),  # Full receipt
                unit_cost=self.test_item2.current_cost
            )
        ]
        
        grv_data = GRVCreate(
            purchase_order_id=purchase_order.id,
            supplier_id=self.test_supplier.id,
            receipt_date=date.today(),
            reference="GRV-TEST-001",
            notes="Test goods receipt",
            lines=grv_lines
        )
        
        # Process the GRV
        grv = create_grv(db, grv_data, self.test_user.id)
        
        # Verification 1: GRV created successfully
        assert grv is not None
        assert grv.reference == "GRV-TEST-001"
        assert grv.status == "Received"
        assert len(grv.lines) == 2
        
        # Verification 2: Inventory quantities updated
        db.refresh(self.test_item1)
        db.refresh(self.test_item2)
        
        assert self.test_item1.quantity_on_hand == initial_qty_item1 + Decimal("18.00")
        assert self.test_item2.quantity_on_hand == initial_qty_item2 + Decimal("15.00")
        
        # Verification 3: Purchase order status updated
        db.refresh(purchase_order)
        assert purchase_order.status == "Partially Received"  # Since item1 was partial
        
        return grv

    def test_supplier_invoice_creation_from_grv(self, db: Session):
        """Test Supplier Invoice creation and verify conversions"""
        # First create a GRV
        grv = self.test_grv_creation_and_inventory_updates(db)
        
        # Convert GRV to Supplier Invoice
        supplier_invoice = convert_grv_to_invoice(db, grv.id, self.test_user.id)
        
        # Verification 1: Supplier invoice created successfully
        assert supplier_invoice is not None
        assert supplier_invoice.transaction_type == "Invoice"
        assert supplier_invoice.supplier_id == self.test_supplier.id
        
        # Verification 2: Invoice amount matches GRV
        expected_amount = (Decimal("18.00") * Decimal("25.00")) + (Decimal("15.00") * Decimal("15.00"))
        assert abs(supplier_invoice.amount - expected_amount) < Decimal("0.01")
        
        # Verification 3: GRV status updated
        db.refresh(grv)
        assert grv.status == "Invoiced"
        
        return supplier_invoice

    def test_sales_order_to_invoice_conversion(self, db: Session):
        """Test Sales Order to Invoice conversion"""
        # First create a sales order
        sales_order = self.test_sales_order_creation_and_listing(db)
        
        # Convert SO to Invoice
        ar_invoice = convert_so_to_invoice(db, sales_order.id, self.test_user.id)
        
        # Verification 1: AR Invoice created successfully
        assert ar_invoice is not None
        assert ar_invoice.transaction_type == "Invoice"
        assert ar_invoice.customer_id == self.test_customer.id
        
        # Verification 2: Invoice amount matches SO
        assert abs(ar_invoice.amount - sales_order.total_amount) < Decimal("0.01")
        
        # Verification 3: Sales order status updated
        db.refresh(sales_order)
        assert sales_order.status == "Invoiced"
        
        # Verification 4: Customer balance updated
        customer_balance = sum(
            trans.amount for trans in self.test_customer.ar_transactions
            if trans.transaction_type == "Invoice"
        )
        assert customer_balance >= ar_invoice.amount
        
        return ar_invoice

    def test_complete_purchase_to_pay_cycle(self, db: Session):
        """Test complete Purchase-to-Pay document cycle"""
        # Step 1: Create Purchase Order
        purchase_order = self.test_purchase_order_creation_and_listing(db)
        assert purchase_order.status == "Open"
        
        # Step 2: Create GRV
        grv = self.test_grv_creation_and_inventory_updates(db)
        assert grv.status == "Received"
        
        # Verify PO status updated
        db.refresh(purchase_order)
        assert purchase_order.status in ["Partially Received", "Fully Received"]
        
        # Step 3: Create Supplier Invoice
        supplier_invoice = self.test_supplier_invoice_creation_from_grv(db)
        assert supplier_invoice.transaction_type == "Invoice"
        
        # Verify GRV status updated
        db.refresh(grv)
        assert grv.status == "Invoiced"
        
        # Step 4: Verify supplier balance updated
        supplier_balance = sum(
            trans.amount for trans in self.test_supplier.ap_transactions
            if trans.transaction_type == "Invoice"
        )
        assert supplier_balance >= supplier_invoice.amount

    def test_complete_order_to_cash_cycle(self, db: Session):
        """Test complete Order-to-Cash document cycle"""
        # Step 1: Create Sales Order
        sales_order = self.test_sales_order_creation_and_listing(db)
        assert sales_order.status == "Open"
        
        # Step 2: Convert to Invoice
        ar_invoice = self.test_sales_order_to_invoice_conversion(db)
        assert ar_invoice.transaction_type == "Invoice"
        
        # Verify SO status updated
        db.refresh(sales_order)
        assert sales_order.status == "Invoiced"
        
        # Step 3: Verify customer balance updated
        customer_balance = sum(
            trans.amount for trans in self.test_customer.ar_transactions
            if trans.transaction_type == "Invoice"
        )
        assert customer_balance >= ar_invoice.amount

    def test_document_status_tracking(self, db: Session):
        """Test document status updates throughout processes"""
        # Create and track Purchase Order lifecycle
        po = self.test_purchase_order_creation_and_listing(db)
        status_history = [po.status]
        
        # Create GRV (partial)
        grv_lines = [
            GRVLineCreate(
                purchase_order_line_id=po.lines[0].id,
                item_id=self.test_item1.id,
                quantity_received=Decimal("10.00"),  # Partial receipt
                unit_cost=self.test_item1.current_cost
            )
        ]
        
        grv_data = GRVCreate(
            purchase_order_id=po.id,
            supplier_id=self.test_supplier.id,
            receipt_date=date.today(),
            reference="GRV-STATUS-001",
            notes="Status tracking test",
            lines=grv_lines
        )
        
        grv = create_grv(db, grv_data, self.test_user.id)
        db.refresh(po)
        status_history.append(po.status)
        
        # Convert to invoice
        supplier_invoice = convert_grv_to_invoice(db, grv.id, self.test_user.id)
        db.refresh(grv)
        status_history.append(grv.status)
        
        # Verify status progression
        assert "Open" in status_history
        assert "Partially Received" in status_history or "Fully Received" in status_history
        assert "Invoiced" in status_history


class TestOrderEntryDocumentsAPI:
    """Test class for Order Entry Documents API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_api_test_data(self, db: Session, test_user):
        """Set up test data for API tests"""
        self.db = db
        self.test_user = test_user
        
        # Create access token
        self.access_token = create_access_token(data={"sub": test_user.email})
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Create test customer for API tests
        self.api_customer = Customer(
            code="API-CUST",
            name="API Test Customer",
            contact_person="API Contact",
            email="api-customer@test.com",
            phone="111-222-3333",
            address="API Customer Address",
            credit_limit=Decimal("5000.00"),
            is_active=True
        )
        
        # Create test supplier for API tests
        self.api_supplier = Supplier(
            code="API-SUPP",
            name="API Test Supplier",
            contact_person="API Supplier Contact",
            email="api-supplier@test.com",
            phone="444-555-6666",
            address="API Supplier Address",
            credit_limit=Decimal("25000.00"),
            is_active=True
        )
        
        # Create test item for API tests
        self.api_item = Item(
            code="API-ITEM",
            name="API Test Item",
            description="Item for API testing",
            unit_of_measure="EA",
            current_cost=Decimal("20.00"),
            selling_price=Decimal("35.00"),
            quantity_on_hand=Decimal("75.00"),
            reorder_level=Decimal("8.00"),
            is_active=True
        )
        
        db.add_all([self.api_customer, self.api_supplier, self.api_item])
        db.commit()
        db.refresh(self.api_customer)
        db.refresh(self.api_supplier)
        db.refresh(self.api_item)

    def test_api_sales_order_workflow(self):
        """Test complete API workflow for sales orders"""
        # Create sales order via API
        so_data = {
            "customer_id": self.api_customer.id,
            "order_date": str(date.today()),
            "reference": "API-SO-001",
            "notes": "API sales order test",
            "lines": [
                {
                    "item_id": self.api_item.id,
                    "quantity": "4.00",
                    "unit_price": str(self.api_item.selling_price),
                    "discount_percent": "0.00"
                }
            ]
        }
        
        response = client.post(
            "/api/sales/orders/",
            json=so_data,
            headers=self.headers
        )
        
        # Verify API response
        assert response.status_code == 201
        so_response = response.json()
        assert so_response["reference"] == "API-SO-001"
        assert so_response["status"] == "Open"
        
        # Verify appears in listing
        list_response = client.get(
            "/api/sales/orders/",
            headers=self.headers
        )
        assert list_response.status_code == 200
        orders = list_response.json()
        order_refs = [order["reference"] for order in orders]
        assert "API-SO-001" in order_refs
        
        return so_response["id"]

    def test_api_purchase_order_workflow(self):
        """Test complete API workflow for purchase orders"""
        # Create purchase order via API
        po_data = {
            "supplier_id": self.api_supplier.id,
            "order_date": str(date.today()),
            "reference": "API-PO-001",
            "notes": "API purchase order test",
            "lines": [
                {
                    "item_id": self.api_item.id,
                    "quantity": "10.00",
                    "unit_cost": str(self.api_item.current_cost),
                    "discount_percent": "0.00"
                }
            ]
        }
        
        response = client.post(
            "/api/purchasing/orders/",
            json=po_data,
            headers=self.headers
        )
        
        # Verify API response
        assert response.status_code == 201
        po_response = response.json()
        assert po_response["reference"] == "API-PO-001"
        assert po_response["status"] == "Open"
        
        # Verify appears in listing
        list_response = client.get(
            "/api/purchasing/orders/",
            headers=self.headers
        )
        assert list_response.status_code == 200
        orders = list_response.json()
        order_refs = [order["reference"] for order in orders]
        assert "API-PO-001" in order_refs
        
        return po_response["id"]

    def test_api_document_conversion_workflow(self):
        """Test API workflow for document conversions"""
        # Create sales order
        so_id = self.test_api_sales_order_workflow()
        
        # Convert to invoice via API
        response = client.post(
            f"/api/sales/orders/{so_id}/convert-to-invoice/",
            headers=self.headers
        )
        
        assert response.status_code == 201
        invoice_response = response.json()
        assert invoice_response["transaction_type"] == "Invoice"
        assert invoice_response["customer_id"] == self.api_customer.id
        
        # Verify SO status updated
        so_response = client.get(
            f"/api/sales/orders/{so_id}",
            headers=self.headers
        )
        assert so_response.status_code == 200
        updated_so = so_response.json()
        assert updated_so["status"] == "Invoiced"

    def test_api_unauthorized_access_prevention(self):
        """Test API prevents unauthorized access to order documents"""
        # Test without authorization header
        so_data = {
            "customer_id": self.api_customer.id,
            "order_date": str(date.today()),
            "reference": "UNAUTH-SO",
            "notes": "Unauthorized test",
            "lines": []
        }
        
        response = client.post(
            "/api/sales/orders/",
            json=so_data
        )
        
        assert response.status_code == 401  # Unauthorized
