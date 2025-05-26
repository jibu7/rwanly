from app.database.database import SessionLocal
from app.models.core import Company, GLAccount
from sqlalchemy.orm import Session

def setup_ap_gl_accounts(db: Session, company_id: int):
    # AP Control Account
    ap_control = db.query(GLAccount).filter(
        GLAccount.company_id == company_id,
        GLAccount.account_type == "Liabilities",
        GLAccount.account_code.like("21%")
    ).first()
    if not ap_control:
        ap_control = GLAccount(
            company_id=company_id,
            account_code="2100",
            account_name="Accounts Payable Control",
            account_type="Liabilities",
            account_subtype="Current Liabilities",
            is_active=True,
            is_control_account=True,
            normal_balance="CREDIT",
            description="AP Control Account"
        )
        db.add(ap_control)
        print("Created AP Control Account (2100)")
    # Expense Account
    expense = db.query(GLAccount).filter(
        GLAccount.company_id == company_id,
        GLAccount.account_type == "Expenses",
        GLAccount.account_code.like("50%")
    ).first()
    if not expense:
        expense = GLAccount(
            company_id=company_id,
            account_code="5000",
            account_name="General Expenses",
            account_type="Expenses",
            account_subtype="Operating Expenses",
            is_active=True,
            is_control_account=False,
            normal_balance="DEBIT",
            description="General Expense Account"
        )
        db.add(expense)
        print("Created Expense Account (5000)")
    db.commit()

def main():
    db = SessionLocal()
    company = db.query(Company).first()
    if not company:
        print("No company found.")
        return
    setup_ap_gl_accounts(db, company.id)
    db.close()

if __name__ == "__main__":
    main()
