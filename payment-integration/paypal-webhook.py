#!/usr/bin/env python3
"""
PayPal Webhook Handler for Autonomous Payment Processing
Receives payment notifications and auto-provisions customer access
"""

import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
import logging

app = FastAPI(title="PayPal Payment Processor")
logger = logging.getLogger(__name__)

# Payment configuration
PAYPAL_ACCOUNT = os.getenv('PAYPAL_ACCOUNT', 'gwc2780@gmail.com')

# Pricing tiers
PRICING = {
    'mesh-network': {'price': 9.00, 'name': 'Zero-Human Mesh Network'},
    'ai-governance': {'price': 299.00, 'name': 'AI Governance Platform'},
    'data-api': {'price': 49.00, 'name': 'Data Monetization API'},
    'cicd-templates': {'price': 799.00, 'name': 'Enterprise CI/CD Templates'},
    'trading-bot': {'price': 1999.00, 'name': 'Autonomous Trading Bot'},
}


@app.post('/webhook/paypal')
async def paypal_webhook(request: Request):
    """Handle PayPal webhook events"""
    try:
        # Parse webhook payload
        payload = await request.json()
        event_type = payload.get('event_type')
        
        logger.info(f"📧 Received PayPal event: {event_type}")
        
        if event_type == 'PAYMENT.SALE.COMPLETED':
            return await handle_payment_completed(payload)
        
        elif event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            return await handle_subscription_activated(payload)
        
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            return await handle_subscription_cancelled(payload)
        
        return {'status': 'ignored', 'event_type': event_type}
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_payment_completed(payload: dict):
    """Process completed payment"""
    resource = payload.get('resource', {})
    amount = float(resource.get('amount', {}).get('total', 0))
    currency = resource.get('amount', {}).get('currency', 'USD')
    payer_email = resource.get('payer', {}).get('email_address', '')
    
    logger.info(f"💰 Payment: ${amount} {currency} from {payer_email}")
    
    # Determine product based on amount
    product_key = determine_product_from_amount(amount)
    
    if product_key:
        # Auto-provision customer access
        await provision_customer_access(
            email=payer_email,
            product=product_key,
            amount=amount
        )
    
    return {
        'status': 'success',
        'payment_processed': True,
        'amount': amount,
        'provisioned': product_key is not None
    }


async def handle_subscription_activated(payload: dict):
    """Process subscription activation"""
    resource = payload.get('resource', {})
    subscriber_email = resource.get('subscriber', {}).get('email_address', '')
    plan_id = resource.get('plan_id', '')
    
    logger.info(f"🔄 Subscription activated: {subscriber_email}")
    
    # Auto-provision recurring access
    await provision_customer_access(
        email=subscriber_email,
        product='subscription',
        amount=0,
        recurring=True
    )
    
    return {'status': 'success', 'subscription_activated': True}


async def handle_subscription_cancelled(payload: dict):
    """Process subscription cancellation"""
    resource = payload.get('resource', {})
    subscriber_email = resource.get('subscriber', {}).get('email_address', '')
    
    logger.info(f"⛔ Subscription cancelled: {subscriber_email}")
    
    # Revoke access (implement your logic)
    await revoke_customer_access(email=subscriber_email)
    
    return {'status': 'success', 'subscription_cancelled': True}


def determine_product_from_amount(amount: float) -> str:
    """Determine product key from payment amount"""
    for key, details in PRICING.items():
        if abs(amount - details['price']) < 0.01:  # Within 1 cent
            return key
    return None


async def provision_customer_access(email: str, product: str, amount: float, recurring: bool = False):
    """Automatically provision customer access"""
    logger.info(f"✅ Provisioning {product} for {email}")
    
    # TODO: Implement your provisioning logic:
    # 1. Create user account
    # 2. Generate API keys
    # 3. Send welcome email with access credentials
    # 4. Add to customer database
    # 5. Enable product features
    
    timestamp = datetime.now().isoformat()
    
    # Log to database/file
    provision_record = {
        'timestamp': timestamp,
        'email': email,
        'product': product,
        'amount': amount,
        'recurring': recurring,
        'status': 'provisioned'
    }
    
    print(f"📝 Provisioned: {json.dumps(provision_record, indent=2)}")
    
    # Send confirmation email (implement with SendGrid/Mailgun)
    # await send_welcome_email(email, product)


async def revoke_customer_access(email: str):
    """Revoke customer access"""
    logger.info(f"❌ Revoking access for {email}")
    
    # TODO: Implement revocation logic:
    # 1. Disable API keys
    # 2. Remove from active users
    # 3. Send cancellation confirmation


@app.get('/health')
def health():
    return {
        'status': 'operational',
        'service': 'paypal-webhook',
        'account': PAYPAL_ACCOUNT
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)
