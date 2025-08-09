# lumen_voice/routers/billing.py

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_user
from ..config import settings
from ..database import get_db

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)

class PriceRequest(schemas.BaseModel):
    price_id: str

@router.post("/create-checkout-session")
def create_checkout_session(
    price_request: PriceRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    customer_id = current_user.stripe_customer_id
    if not customer_id:
        # Cria um novo cliente no Stripe se for a primeira vez
        customer = stripe.Customer.create(email=current_user.email, name=str(current_user.id))
        customer_id = customer.id
        # Atualiza o nosso utilizador com o ID do Stripe
        crud.update_user_stripe_customer_id(db, user_id=current_user.id, stripe_customer_id=customer_id)

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_request.price_id, 'quantity': 1}],
            mode='subscription',
            success_url='http://localhost:3000/payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:3000/payment/cancel',
        )
        return {"sessionId": checkout_session.id, "url": checkout_session.url}
    except Exception as e:
        print("================ ERRO DO STRIPE ================")
        print(e)
        print("==============================================")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Lida com o evento
    if event['type'] == 'invoice.paid':
        invoice = event['data']['object']
        customer_id = invoice['customer']
        price_id = invoice['lines']['data'][0]['price']['id']
        
        plan_credits = 0
        plan_name = "free"
        if price_id == settings.PRICE_ID_HOBBY:
            plan_credits = 200
            plan_name = "hobby"
        elif price_id == settings.PRICE_ID_PRO:
            plan_credits = 600
            plan_name = "pro"

        if plan_credits > 0:
            crud.add_user_credits_and_plan(db, stripe_customer_id=customer_id, credits_to_add=plan_credits, plan_name=plan_name)

    return {"status": "success"}

@router.post("/create-portal-session", summary="Create a customer portal session")
def create_portal_session(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    stripe_customer_id = current_user.stripe_customer_id
    if not stripe_customer_id:
        raise HTTPException(status_code=400, detail="Utilizador não é um cliente Stripe.")

    # A URL para onde o utilizador será redirecionado após sair do portal
    return_url = "http://localhost:3000/" # Futuramente, será a nossa página /account

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=return_url,
        )
        return {"url": portal_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))