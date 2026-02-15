/**
 * Revenue System - Stripe Integration
 * Handles SaaS subscriptions, pay-as-you-go API billing, and premium features
 */

const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const router = express.Router();

// Pricing Tiers
const SUBSCRIPTION_TIERS = {
  starter: {
    name: 'Starter',
    price: 29,
    features: [
      'GitHub webhook integration',
      'Basic Linear sync',
      'Notion automation',
      '100 AI analyses/month',
      'Email support'
    ],
    stripePriceId: process.env.STRIPE_STARTER_PRICE_ID
  },
  professional: {
    name: 'Professional',
    price: 99,
    features: [
      'All Starter features',
      'Advanced GitHub CI/CD',
      'Full Linear integration',
      'Perplexity research',
      '1,000 AI analyses/month',
      'Marketing automation',
      'Priority support'
    ],
    stripePriceId: process.env.STRIPE_PROFESSIONAL_PRICE_ID
  },
  enterprise: {
    name: 'Enterprise',
    price: 499,
    features: [
      'All Professional features',
      'Unlimited AI analyses',
      'Custom integrations',
      'Dedicated support',
      'Advanced analytics',
      'White-label options',
      'Custom workflows'
    ],
    stripePriceId: process.env.STRIPE_ENTERPRISE_PRICE_ID
  }
};

// API Usage Pricing (per 1000 calls)
const API_PRICING = {
  github_webhook: 0.01,
  linear_sync: 0.02,
  ai_analysis: 0.10,
  content_generation: 0.15,
  perplexity_research: 0.20
};

// Create Subscription
router.post('/subscribe', async (req, res) => {
  try {
    const { email, tier, userId } = req.body;

    if (!SUBSCRIPTION_TIERS[tier]) {
      return res.status(400).json({ error: 'Invalid tier' });
    }

    // Create or get customer
    const customers = await stripe.customers.list({ email, limit: 1 });
    let customer = customers.data[0];

    if (!customer) {
      customer = await stripe.customers.create({
        email,
        metadata: { userId }
      });
    }

    // Create subscription
    const subscription = await stripe.subscriptions.create({
      customer: customer.id,
      items: [{
        price: SUBSCRIPTION_TIERS[tier].stripePriceId
      }],
      payment_behavior: 'default_incomplete',
      expand: ['latest_invoice.payment_intent']
    });

    res.json({
      subscription_id: subscription.id,
      client_secret: subscription.latest_invoice.payment_intent.client_secret,
      tier,
      price: SUBSCRIPTION_TIERS[tier].price
    });
  } catch (error) {
    console.error('[Stripe] Subscription error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Track API Usage
router.post('/track-usage', async (req, res) => {
  try {
    const { userId, apiType, count } = req.body;
    const price = API_PRICING[apiType] || 0.05;
    const chargeAmount = Math.round(count * price * 100); // Convert to cents

    console.log(`[API Usage] User: ${userId}, Type: ${apiType}, Count: ${count}, Charge: $${chargeAmount/100}`);

    // Store usage record
    res.json({
      recorded: true,
      apiType,
      count,
      estimatedCharge: chargeAmount / 100
    });
  } catch (error) {
    console.error('[API Usage] Error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get Pricing
router.get('/pricing', (req, res) => {
  res.json({
    subscriptions: SUBSCRIPTION_TIERS,
    apiUsage: API_PRICING,
    timestamp: new Date().toISOString()
  });
});

// Billing Portal
router.post('/billing-portal', async (req, res) => {
  try {
    const { customerId } = req.body;

    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: process.env.BILLING_RETURN_URL
    });

    res.json({ url: session.url });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Webhook Handler for Stripe Events
router.post('/webhook', async (req, res) => {
  try {
    const sig = req.headers['stripe-signature'];
    let event;

    try {
      event = stripe.webhooks.constructEvent(
        req.body,
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );
    } catch (err) {
      console.error('[Stripe Webhook] Signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    console.log(`[Stripe Webhook] Event received: ${event.type}`);

    // Handle different event types
    switch (event.type) {
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object;
        console.log(`[Stripe] Payment succeeded: ${paymentIntent.id}, Amount: $${paymentIntent.amount / 100}`);
        // Trigger auto payout logic here if applicable
        break;

      case 'invoice.payment_succeeded':
        const invoice = event.data.object;
        console.log(`[Stripe] Invoice paid: ${invoice.id}, Amount: $${invoice.amount_paid / 100}`);
        break;

      case 'customer.subscription.created':
      case 'customer.subscription.updated':
        const subscription = event.data.object;
        console.log(`[Stripe] Subscription ${event.type}: ${subscription.id}`);
        break;

      case 'payout.paid':
        const payout = event.data.object;
        console.log(`[Stripe] Payout completed: ${payout.id}, Amount: $${payout.amount / 100}`);
        break;

      case 'payout.failed':
        const failedPayout = event.data.object;
        console.error(`[Stripe] Payout failed: ${failedPayout.id}, Reason: ${failedPayout.failure_message}`);
        break;

      default:
        console.log(`[Stripe] Unhandled event type: ${event.type}`);
    }

    res.json({ received: true });
  } catch (error) {
    console.error('[Stripe Webhook] Error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Create Stripe Connect Account for Payouts
router.post('/create-connect-account', async (req, res) => {
  try {
    const { email, userId } = req.body;

    const account = await stripe.accounts.create({
      type: 'express',
      country: 'US',
      email: email,
      capabilities: {
        transfers: { requested: true }
      },
      metadata: { userId }
    });

    console.log(`[Stripe Connect] Account created: ${account.id} for ${email}`);

    res.json({
      accountId: account.id,
      email,
      status: 'created',
      needsOnboarding: true
    });
  } catch (error) {
    console.error('[Stripe Connect] Error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Initiate Payout via Stripe
router.post('/initiate-payout', async (req, res) => {
  try {
    const { amount, currency, connectedAccountId, description } = req.body;

    // NOTE: This is a general $1 minimum. Tier-based minimums should be enforced at the application layer before calling this endpoint
    if (!amount || amount < 1) {
      return res.status(400).json({ error: 'Minimum payout amount is $1.00' });
    }

    // TODO: In production, specify the connected account using Stripe-Account header or use transfers
    // Example: stripe.payouts.create({ amount, currency }, { stripeAccount: connectedAccountId })
    // Or use: stripe.transfers.create({ amount, currency, destination: connectedAccountId })
    
    // Create a payout to the connected account
    const payout = await stripe.payouts.create({
      amount: Math.round(amount * 100), // Convert to cents
      currency: currency || 'usd',
      description: description || 'Affiliate commission payout',
      metadata: {
        connectedAccountId,
        initiatedAt: new Date().toISOString()
      }
    });

    console.log(`[Stripe Payout] Initiated: ${payout.id}, Amount: $${amount}`);

    res.json({
      payoutId: payout.id,
      amount,
      currency: payout.currency,
      status: payout.status,
      arrivalDate: new Date(payout.arrival_date * 1000).toISOString(),
      created: new Date(payout.created * 1000).toISOString()
    });
  } catch (error) {
    console.error('[Stripe Payout] Error:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
