from sqlalchemy.orm import Session
from . import models as models, schemas as schemas, security as security

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_credits(db: Session, user_id: int, credits: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.credits = credits
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user_stripe_customer_id(db: Session, user_id: int, stripe_customer_id: str):
    """
    Associa um ID de cliente do Stripe a um utilizador na nossa base de dados.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.stripe_customer_id = stripe_customer_id
        db.commit()
        db.refresh(db_user)
    return db_user

def add_user_credits_and_plan(db: Session, stripe_customer_id: str, credits_to_add: int, plan_name: str):
    """
    Encontra um utilizador pelo seu ID do Stripe, adiciona créditos e atualiza o seu plano.
    Isto é chamado pelo webhook quando um pagamento é confirmado.
    """
    db_user = db.query(models.User).filter(models.User.stripe_customer_id == stripe_customer_id).first()
    if db_user:
        db_user.credits = (db_user.credits or 0) + credits_to_add
        db_user.plan = plan_name
        db.commit()
        db.refresh(db_user)
    return db_user