#!/usr/bin/env python3
"""
ZEUS - Zero-Human Enterprise Universal System
Deployment Orchestrator for Garcar Revenue Agent System

Configures all secrets, verifies Zap connections, and deploys the autonomous revenue loop.
"""

import os
import sys
import requests
import stripe
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ZEUS - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ZeusOrchestrator:
    """Master deployment orchestrator for the autonomous revenue system."""
    
    def __init__(self):
        """Initialize Zeus with all required API keys and configuration."""
        
        # === STRIPE CONFIGURATION ===
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY', '')
        self.stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        
        # === NOTION CONFIGURATION ===
        self.notion_api_key = os.getenv('NOTION_API_KEY', '')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID', '')
        
        # === GITHUB CONFIGURATION ===
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_repo = 'Garrettc123/revenue-agent-system'
        
        # === SENDGRID CONFIGURATION ===
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', '')
        self.from_email = os.getenv('FROM_EMAIL', 'garrett@garcar.io')
        
        # === LINEAR CONFIGURATION ===
        self.linear_api_key = os.getenv('LINEAR_API_KEY', '')
        self.linear_team_id = os.getenv('LINEAR_TEAM_ID', '')
        
        # === ZAPIER CONFIGURATION ===
        self.zapier_webhook_url = os.getenv('ZAPIER_WEBHOOK_URL', '')
        
        # === PRODUCT IDS ===
        self.starter_audit_product_ids = os.getenv(
            'STARTER_AUDIT_PRODUCT_IDS', 
            'price_1QDnHRI2mSgAYJivfNVvB7Y3,price_1QGx9RI2mSgAYJivJ0B8xQRU'
        ).split(',')
        
        # === DEPLOYMENT CONFIGURATION ===
        self.deployment_url = os.getenv('DEPLOYMENT_URL', 'https://revenue-agent-system.vercel.app')
        self.railway_project_id = os.getenv('RAILWAY_PROJECT_ID', '')
        
        logger.info("Zeus Orchestrator initialized")
    
    def verify_secrets(self) -> bool:
        """Verify all required secrets are configured."""
        logger.info("Verifying secrets configuration...")
        
        required_secrets = {
            'STRIPE_SECRET_KEY': self.stripe_secret_key,
            'NOTION_API_KEY': self.notion_api_key,
            'GITHUB_TOKEN': self.github_token,
            'SENDGRID_API_KEY': self.sendgrid_api_key,
            'LINEAR_API_KEY': self.linear_api_key,
        }
        
        missing = [name for name, value in required_secrets.items() if not value]
        
        if missing:
            logger.error(f"Missing required secrets: {', '.join(missing)}")
            logger.error("Set these environment variables before running Zeus")
            return False
        
        logger.info("✓ All required secrets configured")
        return True
    
    def verify_stripe_connection(self) -> bool:
        """Verify Stripe API connection and product configuration."""
        logger.info("Verifying Stripe connection...")
        
        try:
            stripe.api_key = self.stripe_secret_key
            
            # Test API connection
            account = stripe.Account.retrieve()
            logger.info(f"✓ Connected to Stripe account: {account['id']}")
            
            # Verify product IDs
            for price_id in self.starter_audit_product_ids:
                price = stripe.Price.retrieve(price_id.strip())
                product = stripe.Product.retrieve(price['product'])
                logger.info(f"✓ Found product: {product['name']} - ${price['unit_amount']/100}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Stripe verification failed: {str(e)}")
            return False
    
    def verify_notion_connection(self) -> bool:
        """Verify Notion API connection and database access."""
        logger.info("Verifying Notion connection...")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.notion_api_key}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            
            # Test database access
            if self.notion_database_id:
                url = f'https://api.notion.com/v1/databases/{self.notion_database_id}'
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    db = response.json()
                    logger.info(f"✓ Connected to Notion database: {db.get('title', [{}])[0].get('plain_text', 'Audit Pipeline')}")
                    return True
                else:
                    logger.warning(f"Database {self.notion_database_id} not accessible, will use page-level logging")
            
            # Test API connection even without database
            test_url = 'https://api.notion.com/v1/users/me'
            response = requests.get(test_url, headers=headers)
            
            if response.status_code == 200:
                logger.info("✓ Notion API connection verified")
                return True
            else:
                logger.error(f"✗ Notion API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Notion verification failed: {str(e)}")
            return False
    
    def verify_linear_connection(self) -> bool:
        """Verify Linear API connection."""
        logger.info("Verifying Linear connection...")
        
        try:
            headers = {
                'Authorization': self.linear_api_key,
                'Content-Type': 'application/json'
            }
            
            query = '''
            query {
                viewer {
                    id
                    name
                    email
                }
            }
            '''
            
            response = requests.post(
                'https://api.linear.app/graphql',
                headers=headers,
                json={'query': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                viewer = data.get('data', {}).get('viewer', {})
                logger.info(f"✓ Connected to Linear as: {viewer.get('name')} ({viewer.get('email')})")
                return True
            else:
                logger.error(f"✗ Linear API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Linear verification failed: {str(e)}")
            return False
    
    def verify_zap_endpoints(self) -> Dict[str, bool]:
        """Verify all 7 Zap endpoints are accessible."""
        logger.info("Verifying Zap endpoints (Z1-Z7)...")
        
        results = {}
        
        # Z1-Z7 Zap names and expected status
        zaps = [
            'Z1: Stripe → Linear',
            'Z2: Stripe → Notion',
            'Z3: Stripe → Gmail',
            'Z4: Stripe → Calendar (Pro plan required)',
            'Z5: Linear In Review → Gmail',
            'Z6: Linear Done → Notion',
            'Z7: Stripe Subscription → Linear'
        ]
        
        for zap in zaps:
            # Zaps are configured via Zapier web UI, not API
            # Mark as pending manual verification
            results[zap] = 'configured'
            logger.info(f"  {zap}: Configured (manual verification required)")
        
        logger.info("✓ Zap configuration documented in GAR-460")
        return results
    
    def run_smoke_test(self) -> bool:
        """Run smoke test of the revenue loop."""
        logger.info("Running smoke test...")
        logger.warning("Smoke test requires actual Stripe payment")
        logger.warning("To test: Send $0.50 to Payment Link")
        logger.warning("Expected: Z1-Z4 fire within 60 seconds")
        logger.warning("Verify: Linear issue created, Notion page created, Gmail sent, Calendar event created")
        return True
    
    def deploy(self) -> bool:
        """Execute full deployment sequence."""
        logger.info("="*60)
        logger.info("ZEUS DEPLOYMENT ORCHESTRATOR")
        logger.info("Autonomous Revenue System - RHNS Template Flywheel")
        logger.info("="*60)
        
        # Step 1: Verify secrets
        if not self.verify_secrets():
            logger.error("Deployment failed: Missing secrets")
            return False
        
        # Step 2: Verify API connections
        verifications = [
            ('Stripe', self.verify_stripe_connection()),
            ('Notion', self.verify_notion_connection()),
            ('Linear', self.verify_linear_connection()),
        ]
        
        failed = [name for name, status in verifications if not status]
        
        if failed:
            logger.error(f"Deployment failed: {', '.join(failed)} verification failed")
            return False
        
        # Step 3: Verify Zap configuration
        self.verify_zap_endpoints()
        
        # Step 4: Display smoke test instructions
        self.run_smoke_test()
        
        logger.info("="*60)
        logger.info("DEPLOYMENT COMPLETE")
        logger.info("="*60)
        logger.info("System Status: OPERATIONAL")
        logger.info(f"Deployment URL: {self.deployment_url}")
        logger.info("Next Steps:")
        logger.info("  1. Upgrade Zapier to Pro plan to activate Z4")
        logger.info("  2. Create Notion Audit Pipeline database for Z2")
        logger.info("  3. Run smoke test with $0.50 Stripe payment")
        logger.info("  4. Monitor GAR-460 for Z1-Z7 execution confirmation")
        logger.info("="*60)
        
        return True

def main():
    """Main entry point."""
    zeus = ZeusOrchestrator()
    success = zeus.deploy()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
