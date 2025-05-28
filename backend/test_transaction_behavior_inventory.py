"""
Transaction & Document Processing Behavior Tests - Inventory Module

This module tests the specific business behaviors for Inventory Adjustment as described 
in the CRUD_Testing_Checklist.md:

4. Inventory Adjustment:
   - Process "Adjustment Increase" and "Adjustment Decrease"
   - Verify Quantity On Hand updates correctly
   - Verify inventory adjustments appear in listing
   - Verify GL impact (Inventory Asset Account and Cost of Sales/Adjustment Account)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, date

from app.main import app
from app.database.base import get_db
from app.models.inventory import Item, InventoryAdjustment
from app.models.general_ledger import GLAccount, GLTransaction, GLEntry
from app.models.auth import User, Role, Permission, RolePermission, UserRole
from app.crud.inventory import get_item_by_code, create_inventory_adjustment, get_inventory_adjustments
from app.crud.general_ledger import get_gl_account_balance
from app.schemas.inventory import InventoryAdjustmentCreate
from app.core.security import create_access_token

client = TestClient(app)


class TestInventoryAdjustmentBehavior:
    """Test class for Inventory Adjustment transaction behavior"""

    @pytest.fixture(autouse=True)
    def setup_inventory_test_data(self, db: Session, test_user):
        """Set up test data for inventory adjustment tests"""
        self.db = db
        self.test_user = test_user
        
        # Create test GL accounts for inventory
        self.inventory_asset_account = GLAccount(
            code="1300",
            name="Inventory Asset",
            account_type="Asset",
            is_active=True
        )
        self.cost_adjustment_account = GLAccount(
            code="5100",
            name="Cost of Sales - Adjustments",
            account_type="Expense",
            is_active=True
        )
        
        db.add_all([self.inventory_asset_account, self.cost_adjustment_account])
        db.commit()
        
        # Create test inventory item
        self.test_item = Item(
            code="TEST001",
            name="Test Inventory Item",
            description="Test item for inventory adjustment tests",
            unit_of_measure="EA",
            current_cost=Decimal("10.00"),
            quantity_on_hand=Decimal("100.00"),
            reorder_level=Decimal("10.00"),
            is_active=True
        )
        
        db.add(self.test_item)
        db.commit()
        db.refresh(self.test_item)
        
        # Store initial balances for verification
        self.initial_quantity = self.test_item.quantity_on_hand
        self.initial_inventory_balance = get_gl_account_balance(
            db, self.inventory_asset_account.id
        ) or Decimal("0.00")

    def test_inventory_adjustment_increase(self, db: Session):
        """Test inventory adjustment increase behavior"""
        # Record the initial quantity
        initial_qty = self.test_item.quantity_on_hand
        adjustment_qty = Decimal("25.00")
        expected_new_qty = initial_qty + adjustment_qty
        
        # Create adjustment increase
        adjustment_data = InventoryAdjustmentCreate(
            item_id=self.test_item.id,
            adjustment_type="Increase",
            quantity=adjustment_qty,
            unit_cost=self.test_item.current_cost,
            reason="Test adjustment increase",
            reference="TEST-ADJ-001"
        )
        
        # Process the adjustment
        adjustment = create_inventory_adjustment(db, adjustment_data, self.test_user.id)
        
        # Verification 1: Adjustment created successfully
        assert adjustment is not None
        assert adjustment.quantity == adjustment_qty
        assert adjustment.adjustment_type == "Increase"
        
        # Verification 2: Item quantity updated correctly
        db.refresh(self.test_item)
        assert self.test_item.quantity_on_hand == expected_new_qty
        
        # Verification 3: Adjustment appears in listing
        adjustments = get_inventory_adjustments(db)
        adjustment_codes = [adj.reference for adj in adjustments]
        assert "TEST-ADJ-001" in adjustment_codes
        
        # Verification 4: GL impact - Inventory Asset Account increase
        new_inventory_balance = get_gl_account_balance(
            db, self.inventory_asset_account.id
        ) or Decimal("0.00")
        expected_gl_impact = adjustment_qty * self.test_item.current_cost
        assert new_inventory_balance == self.initial_inventory_balance + expected_gl_impact
        
        return adjustment

    def test_inventory_adjustment_decrease(self, db: Session):
        """Test inventory adjustment decrease behavior"""
        # First ensure we have enough stock by doing an increase
        self.test_inventory_adjustment_increase(db)
        
        # Record current quantity after increase
        current_qty = self.test_item.quantity_on_hand
        adjustment_qty = Decimal("15.00")
        expected_new_qty = current_qty - adjustment_qty
        
        # Create adjustment decrease
        adjustment_data = InventoryAdjustmentCreate(
            item_id=self.test_item.id,
            adjustment_type="Decrease",
            quantity=adjustment_qty,
            unit_cost=self.test_item.current_cost,
            reason="Test adjustment decrease",
            reference="TEST-ADJ-002"
        )
        
        # Process the adjustment
        adjustment = create_inventory_adjustment(db, adjustment_data, self.test_user.id)
        
        # Verification 1: Adjustment created successfully
        assert adjustment is not None
        assert adjustment.quantity == adjustment_qty
        assert adjustment.adjustment_type == "Decrease"
        
        # Verification 2: Item quantity updated correctly
        db.refresh(self.test_item)
        assert self.test_item.quantity_on_hand == expected_new_qty
        
        # Verification 3: Adjustment appears in listing
        adjustments = get_inventory_adjustments(db)
        adjustment_codes = [adj.reference for adj in adjustments]
        assert "TEST-ADJ-002" in adjustment_codes
        
        # Verification 4: GL impact - Inventory Asset Account decrease
        current_inventory_balance = get_gl_account_balance(
            db, self.inventory_asset_account.id
        ) or Decimal("0.00")
        expected_gl_decrease = adjustment_qty * self.test_item.current_cost
        
        # Should reflect both the increase and decrease adjustments
        net_adjustment = Decimal("25.00") - Decimal("15.00")  # +25 -15 = +10
        expected_final_balance = self.initial_inventory_balance + (net_adjustment * self.test_item.current_cost)
        assert current_inventory_balance == expected_final_balance

    def test_multiple_adjustments_consistency(self, db: Session):
        """Test that multiple adjustments maintain quantity consistency"""
        initial_qty = self.test_item.quantity_on_hand
        
        # Series of adjustments
        adjustments = [
            ("Increase", Decimal("20.00"), "ADJ-001"),
            ("Decrease", Decimal("5.00"), "ADJ-002"),
            ("Increase", Decimal("10.00"), "ADJ-003"),
            ("Decrease", Decimal("8.00"), "ADJ-004")
        ]
        
        expected_qty = initial_qty
        for adj_type, qty, ref in adjustments:
            adjustment_data = InventoryAdjustmentCreate(
                item_id=self.test_item.id,
                adjustment_type=adj_type,
                quantity=qty,
                unit_cost=self.test_item.current_cost,
                reason=f"Test {adj_type.lower()}",
                reference=ref
            )
            
            create_inventory_adjustment(db, adjustment_data, self.test_user.id)
            
            # Update expected quantity
            if adj_type == "Increase":
                expected_qty += qty
            else:
                expected_qty -= qty
            
            # Verify quantity after each adjustment
            db.refresh(self.test_item)
            assert self.test_item.quantity_on_hand == expected_qty

    def test_negative_quantity_prevention(self, db: Session):
        """Test that system prevents negative inventory quantities"""
        current_qty = self.test_item.quantity_on_hand
        excessive_decrease = current_qty + Decimal("10.00")  # More than available
        
        adjustment_data = InventoryAdjustmentCreate(
            item_id=self.test_item.id,
            adjustment_type="Decrease",
            quantity=excessive_decrease,
            unit_cost=self.test_item.current_cost,
            reason="Test negative prevention",
            reference="TEST-NEG-001"
        )
        
        # This should raise an exception or return error
        with pytest.raises(Exception):
            create_inventory_adjustment(db, adjustment_data, self.test_user.id)
        
        # Verify quantity unchanged
        db.refresh(self.test_item)
        assert self.test_item.quantity_on_hand == current_qty

    def test_zero_quantity_adjustment_prevention(self, db: Session):
        """Test that system prevents zero quantity adjustments"""
        adjustment_data = InventoryAdjustmentCreate(
            item_id=self.test_item.id,
            adjustment_type="Increase",
            quantity=Decimal("0.00"),
            unit_cost=self.test_item.current_cost,
            reason="Test zero prevention",
            reference="TEST-ZERO-001"
        )
        
        # This should raise an exception or return error
        with pytest.raises(Exception):
            create_inventory_adjustment(db, adjustment_data, self.test_user.id)


class TestInventoryAdjustmentAPI:
    """Test class for Inventory Adjustment API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_api_test_data(self, db: Session, test_user):
        """Set up test data for API tests"""
        self.db = db
        self.test_user = test_user
        
        # Create access token
        self.access_token = create_access_token(data={"sub": test_user.email})
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Create test item for API tests
        self.api_test_item = Item(
            code="API001",
            name="API Test Item",
            description="Item for API testing",
            unit_of_measure="EA",
            current_cost=Decimal("15.00"),
            quantity_on_hand=Decimal("50.00"),
            reorder_level=Decimal("5.00"),
            is_active=True
        )
        
        db.add(self.api_test_item)
        db.commit()
        db.refresh(self.api_test_item)

    def test_api_inventory_adjustment_increase_workflow(self):
        """Test complete API workflow for inventory adjustment increase"""
        initial_qty = self.api_test_item.quantity_on_hand
        adjustment_qty = "20.00"
        
        # API call to create adjustment
        adjustment_data = {
            "item_id": self.api_test_item.id,
            "adjustment_type": "Increase",
            "quantity": adjustment_qty,
            "unit_cost": str(self.api_test_item.current_cost),
            "reason": "API test increase",
            "reference": "API-ADJ-001"
        }
        
        response = client.post(
            "/api/inventory/adjustments/",
            json=adjustment_data,
            headers=self.headers
        )
        
        # Verify API response
        assert response.status_code == 201
        adjustment_response = response.json()
        assert adjustment_response["quantity"] == adjustment_qty
        assert adjustment_response["adjustment_type"] == "Increase"
        
        # Verify item quantity updated via API
        item_response = client.get(
            f"/api/inventory/items/{self.api_test_item.id}",
            headers=self.headers
        )
        assert item_response.status_code == 200
        updated_item = item_response.json()
        expected_qty = float(initial_qty) + float(adjustment_qty)
        assert float(updated_item["quantity_on_hand"]) == expected_qty

    def test_api_inventory_adjustment_decrease_workflow(self):
        """Test complete API workflow for inventory adjustment decrease"""
        # First do an increase to ensure sufficient stock
        self.test_api_inventory_adjustment_increase_workflow()
        
        # Get current quantity
        item_response = client.get(
            f"/api/inventory/items/{self.api_test_item.id}",
            headers=self.headers
        )
        current_qty = float(item_response.json()["quantity_on_hand"])
        adjustment_qty = "10.00"
        
        # API call to create decrease adjustment
        adjustment_data = {
            "item_id": self.api_test_item.id,
            "adjustment_type": "Decrease",
            "quantity": adjustment_qty,
            "unit_cost": str(self.api_test_item.current_cost),
            "reason": "API test decrease",
            "reference": "API-ADJ-002"
        }
        
        response = client.post(
            "/api/inventory/adjustments/",
            json=adjustment_data,
            headers=self.headers
        )
        
        # Verify API response
        assert response.status_code == 201
        adjustment_response = response.json()
        assert adjustment_response["quantity"] == adjustment_qty
        assert adjustment_response["adjustment_type"] == "Decrease"
        
        # Verify item quantity updated via API
        item_response = client.get(
            f"/api/inventory/items/{self.api_test_item.id}",
            headers=self.headers
        )
        assert item_response.status_code == 200
        updated_item = item_response.json()
        expected_qty = current_qty - float(adjustment_qty)
        assert float(updated_item["quantity_on_hand"]) == expected_qty

    def test_api_inventory_adjustments_listing(self):
        """Test API endpoint for inventory adjustments listing"""
        # Create some adjustments first
        self.test_api_inventory_adjustment_increase_workflow()
        self.test_api_inventory_adjustment_decrease_workflow()
        
        # Get adjustments listing via API
        response = client.get(
            "/api/inventory/adjustments/",
            headers=self.headers
        )
        
        assert response.status_code == 200
        adjustments = response.json()
        
        # Verify our test adjustments are in the listing
        adjustment_refs = [adj["reference"] for adj in adjustments]
        assert "API-ADJ-001" in adjustment_refs
        assert "API-ADJ-002" in adjustment_refs

    def test_api_invalid_adjustment_prevention(self):
        """Test API prevention of invalid adjustments"""
        # Test negative quantity
        invalid_data = {
            "item_id": self.api_test_item.id,
            "adjustment_type": "Increase",
            "quantity": "-5.00",
            "unit_cost": str(self.api_test_item.current_cost),
            "reason": "Invalid negative test",
            "reference": "INVALID-001"
        }
        
        response = client.post(
            "/api/inventory/adjustments/",
            json=invalid_data,
            headers=self.headers
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test zero quantity
        invalid_data["quantity"] = "0.00"
        response = client.post(
            "/api/inventory/adjustments/",
            json=invalid_data,
            headers=self.headers
        )
        
        assert response.status_code == 422  # Validation error

    def test_api_unauthorized_access_prevention(self):
        """Test API prevents unauthorized access to inventory adjustments"""
        adjustment_data = {
            "item_id": self.api_test_item.id,
            "adjustment_type": "Increase",
            "quantity": "10.00",
            "unit_cost": str(self.api_test_item.current_cost),
            "reason": "Unauthorized test",
            "reference": "UNAUTH-001"
        }
        
        # Call without authorization header
        response = client.post(
            "/api/inventory/adjustments/",
            json=adjustment_data
        )
        
        assert response.status_code == 401  # Unauthorized
