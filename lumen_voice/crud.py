from sqlalchemy.orm import Session
from . import models, schemas, security

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ▼▼▼ ESTA É A VERSÃO ATUALIZADA COM A DEPURAÇÃO ▼▼▼
def update_user_credits(db: Session, user_id: int, credits: int):
    print(f"--- CRUD: A tentar atualizar créditos para o user ID {user_id} ---")
    print(f"--- CRUD: Novo saldo a ser salvo: {credits} ---")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if db_user:
        print(f"--- CRUD: Utilizador encontrado. Saldo antigo no DB: {db_user.credits} ---")
        db_user.credits = credits
        try:
            db.commit()
            db.refresh(db_user)
            print(f"--- CRUD: COMMIT BEM-SUCEDIDO! Saldo atualizado no DB para: {db_user.credits} ---")
        except Exception as e:
            print(f"!!!!!! CRUD: ERRO DURANTE O COMMIT: {e} !!!!!!")
            db.rollback() # Importante: reverte a transação em caso de erro
    else:
        print(f"--- CRUD: Utilizador com ID {user_id} não encontrado. ---")
        
    return db_user
# ▲▲▲ FIM DA VERSÃO ATUALIZADA ▲▲▲

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
    print(f"\n--- WEBHOOK CRUD: A procurar utilizador com Stripe ID: {stripe_customer_id} ---")
    
    db_user = db.query(models.User).filter(models.User.stripe_customer_id == stripe_customer_id).first()
    
    if db_user:
        print(f"--- WEBHOOK CRUD: Utilizador encontrado: {db_user.email}. Saldo antigo: {db_user.credits} ---")
        print(f"--- WEBHOOK CRUD: A adicionar {credits_to_add} créditos e a definir o plano para '{plan_name}' ---")
        
        db_user.credits = (db_user.credits or 0) + credits_to_add
        db_user.plan = plan_name
        try:
            db.commit()
            db.refresh(db_user)
            print(f"--- WEBHOOK CRUD: COMMIT BEM-SUCEDIDO! Novo saldo: {db_user.credits}, Novo plano: {db_user.plan} ---")
        except Exception as e:
            print(f"!!!!!! WEBHOOK CRUD: ERRO DURANTE O COMMIT: {e} !!!!!!")
            db.rollback()
    else:
        print(f"!!!!!! WEBHOOK CRUD: Utilizador com Stripe ID {stripe_customer_id} NÃO ENCONTRADO no banco de dados. !!!!!!")
        
    return db_user

def update_user_password(db: Session, user_id: int, new_hashed_password: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.hashed_password = new_hashed_password
        db.commit()
        db.refresh(db_user)
    return db_user