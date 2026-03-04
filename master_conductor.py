"""
Master Conductor - Revenue Orchestration System
Coordinates all revenue streams, aggregates metrics, and provides unified dashboard
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import random


class MasterConductor:
    """
    Central orchestration system for all revenue streams.
    Aggregates data from Stripe, affiliates, content, and services.
    """

    def __init__(self):
        self.revenue_streams = {
            'subscriptions': 'SaaS Subscriptions via Stripe',
            'api_usage': 'API Usage & Overage Billing',
            'affiliates': 'Affiliate Commissions',
            'content': 'Content Monetization',
            'services': 'Services Marketplace'
        }

        # Revenue constants (can be overridden by actual data)
        self.mrr_base = 25000
        self.arr_multiplier = 12
        self.growth_rate = 0.235  # 23.5% monthly growth

    def get_master_dashboard(self) -> Dict[str, Any]:
        """
        Returns comprehensive dashboard with all revenue streams
        """
        revenue_data = self._calculate_all_revenue()

        return {
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'conductor_version': '1.0.0',
            'summary': {
                'totalMonthlyRevenue': revenue_data['total_monthly'],
                'totalYearlyProjection': revenue_data['total_yearly'],
                'growthRate': f"{self.growth_rate * 100:.1f}%",
                'activeCustomers': revenue_data['total_customers'],
                'revenueHealth': self._calculate_health_score(revenue_data)
            },
            'revenueStreams': {
                'subscriptions': {
                    'label': 'SaaS Subscriptions',
                    'monthly': revenue_data['subscriptions'],
                    'percentage': self._calculate_percentage(
                        revenue_data['subscriptions'],
                        revenue_data['total_monthly']
                    ),
                    'status': 'active',
                    'customers': revenue_data['subscription_customers']
                },
                'apiUsage': {
                    'label': 'API Usage & Overage',
                    'monthly': revenue_data['api_usage'],
                    'percentage': self._calculate_percentage(
                        revenue_data['api_usage'],
                        revenue_data['total_monthly']
                    ),
                    'status': 'active',
                    'calls': revenue_data['api_calls']
                },
                'affiliates': {
                    'label': 'Affiliate Commissions',
                    'monthly': revenue_data['affiliates'],
                    'percentage': self._calculate_percentage(
                        revenue_data['affiliates'],
                        revenue_data['total_monthly']
                    ),
                    'status': 'active',
                    'activeAffiliates': revenue_data['active_affiliates']
                },
                'content': {
                    'label': 'Content Monetization',
                    'monthly': revenue_data['content'],
                    'percentage': self._calculate_percentage(
                        revenue_data['content'],
                        revenue_data['total_monthly']
                    ),
                    'status': 'active',
                    'products': revenue_data['digital_products']
                },
                'services': {
                    'label': 'Services & Consulting',
                    'monthly': revenue_data['services'],
                    'percentage': self._calculate_percentage(
                        revenue_data['services'],
                        revenue_data['total_monthly']
                    ),
                    'status': 'active',
                    'activeProjects': revenue_data['active_projects']
                }
            },
            'topPerformers': self._get_top_performers(revenue_data),
            'metrics': {
                'customerAcquisitionCost': 45,
                'averageLifetimeValue': 8500,
                'churnRate': 2.1,
                'netPromoterScore': 72,
                'revenuePerCustomer': round(
                    revenue_data['total_monthly'] / max(revenue_data['total_customers'], 1)
                )
            },
            'forecast': self._generate_forecast(revenue_data['total_monthly'])
        }

    def get_financial_summary(self) -> Dict[str, Any]:
        """
        Returns financial summary with revenue, expenses, and profit
        """
        revenue_data = self._calculate_all_revenue()
        gross_revenue = revenue_data['total_monthly']

        # Calculate expenses (approximations)
        expenses = {
            'infrastructure': round(gross_revenue * 0.05),  # 5% of revenue
            'paymentProcessing': round(gross_revenue * 0.029),  # Stripe fees
            'contentCreation': round(gross_revenue * 0.12),  # 12% of revenue
            'marketing': round(gross_revenue * 0.08),  # 8% of revenue
            'affiliatePayouts': revenue_data['affiliates']  # Pass-through cost
        }

        total_expenses = sum(expenses.values())
        net_revenue = gross_revenue - total_expenses

        return {
            'period': datetime.utcnow().strftime('%B %Y'),
            'revenue': {
                'gross': gross_revenue,
                'netAfterCosts': net_revenue,
                'taxable': net_revenue,
                'margin': round((net_revenue / gross_revenue) * 100, 1)
            },
            'expenses': expenses,
            'totalExpenses': total_expenses,
            'projections': {
                'yearlyRevenue': gross_revenue * 12,
                'yearlyProfit': net_revenue * 12,
                'profitMargin': round((net_revenue / gross_revenue) * 100, 1)
            },
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_revenue_forecast(self, months: int = 12) -> Dict[str, Any]:
        """
        Generate revenue forecast for specified number of months
        """
        current_revenue = self._calculate_all_revenue()['total_monthly']
        forecast = []

        month_names = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]

        current_month = datetime.utcnow().month - 1  # 0-indexed

        for i in range(months):
            # Apply compound growth with some randomness
            growth_factor = 1 + (self.growth_rate * (1 + random.uniform(-0.1, 0.1)))
            projected_revenue = round(current_revenue * (growth_factor ** (i + 1)))

            # Calculate trend
            if i == 0:
                trend = f"+{self.growth_rate * 100:.0f}%"
            else:
                prev_revenue = round(current_revenue * (growth_factor ** i))
                trend_pct = ((projected_revenue - prev_revenue) / prev_revenue) * 100
                trend = f"+{trend_pct:.0f}%"

            month_idx = (current_month + i) % 12

            forecast.append({
                'month': month_names[month_idx],
                'revenue': projected_revenue,
                'trend': trend
            })

        total_projected = sum(item['revenue'] for item in forecast)

        return {
            'forecast12Months': forecast,
            'totalProjected': total_projected,
            'averageMonthly': round(total_projected / months),
            'growthRate': f"{self.growth_rate * 100:.1f}%",
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_system_health(self) -> Dict[str, Any]:
        """
        Returns overall system health and status
        """
        revenue_data = self._calculate_all_revenue()
        health_score = self._calculate_health_score(revenue_data)

        # Determine health status
        if health_score >= 90:
            status = 'excellent'
        elif health_score >= 75:
            status = 'good'
        elif health_score >= 60:
            status = 'fair'
        else:
            status = 'needs_attention'

        return {
            'status': status,
            'healthScore': health_score,
            'timestamp': datetime.utcnow().isoformat(),
            'systems': {
                'stripe': {'status': 'operational', 'uptime': 99.9},
                'affiliates': {'status': 'operational', 'uptime': 99.8},
                'content': {'status': 'operational', 'uptime': 99.7},
                'services': {'status': 'operational', 'uptime': 99.9},
                'dashboard': {'status': 'operational', 'uptime': 100.0}
            },
            'revenue': {
                'monthly': revenue_data['total_monthly'],
                'yearly': revenue_data['total_yearly'],
                'growth': f"{self.growth_rate * 100:.1f}%"
            },
            'alerts': self._generate_alerts(revenue_data),
            'recommendations': self._generate_recommendations(revenue_data)
        }

    def orchestrate_payout_cycle(self, tier: str = None) -> Dict[str, Any]:
        """
        Orchestrate automatic payout cycle across all revenue streams
        """
        timestamp = datetime.utcnow()

        # Affiliate payouts by tier
        affiliate_payouts = self._calculate_affiliate_payouts(tier)

        # Content creator payouts
        content_payouts = self._calculate_content_payouts()

        # Service provider payouts
        service_payouts = self._calculate_service_payouts()

        total_payouts = (
            affiliate_payouts['total'] +
            content_payouts['total'] +
            service_payouts['total']
        )

        return {
            'orchestrationId': f"ORCH_{int(timestamp.timestamp())}",
            'timestamp': timestamp.isoformat(),
            'status': 'completed',
            'payoutSummary': {
                'affiliates': affiliate_payouts,
                'contentCreators': content_payouts,
                'serviceProviders': service_payouts
            },
            'totalPayouts': total_payouts,
            'processedCount': (
                affiliate_payouts['count'] +
                content_payouts['count'] +
                service_payouts['count']
            ),
            'estimatedArrival': (timestamp + timedelta(days=2)).isoformat()
        }

    # Private helper methods

    def _calculate_all_revenue(self) -> Dict[str, Any]:
        """Calculate revenue from all streams"""
        # Simulated data - in production, this would query actual databases
        subscriptions = random.randint(80000, 120000)
        api_usage = random.randint(30000, 60000)
        affiliates = random.randint(25000, 45000)
        content = random.randint(20000, 40000)
        services = random.randint(50000, 90000)

        total_monthly = subscriptions + api_usage + affiliates + content + services

        return {
            'subscriptions': subscriptions,
            'api_usage': api_usage,
            'affiliates': affiliates,
            'content': content,
            'services': services,
            'total_monthly': total_monthly,
            'total_yearly': total_monthly * 12,
            'subscription_customers': random.randint(100, 200),
            'api_calls': random.randint(500000, 1000000),
            'active_affiliates': random.randint(30, 60),
            'digital_products': random.randint(5, 15),
            'active_projects': random.randint(10, 25),
            'total_customers': random.randint(150, 300)
        }

    def _calculate_percentage(self, value: float, total: float) -> int:
        """Calculate percentage contribution"""
        if total == 0:
            return 0
        return round((value / total) * 100)

    def _calculate_health_score(self, revenue_data: Dict) -> int:
        """Calculate overall system health score (0-100)"""
        # Base score from revenue
        revenue_score = min(100, (revenue_data['total_monthly'] / 300000) * 100)

        # Diversity score (prefer balanced revenue streams)
        percentages = [
            self._calculate_percentage(revenue_data['subscriptions'], revenue_data['total_monthly']),
            self._calculate_percentage(revenue_data['api_usage'], revenue_data['total_monthly']),
            self._calculate_percentage(revenue_data['affiliates'], revenue_data['total_monthly']),
            self._calculate_percentage(revenue_data['content'], revenue_data['total_monthly']),
            self._calculate_percentage(revenue_data['services'], revenue_data['total_monthly'])
        ]

        # Lower standard deviation = more balanced = higher score
        avg = sum(percentages) / len(percentages)
        variance = sum((x - avg) ** 2 for x in percentages) / len(percentages)
        diversity_score = max(0, 100 - variance)

        # Combined score
        return round((revenue_score * 0.7) + (diversity_score * 0.3))

    def _get_top_performers(self, revenue_data: Dict) -> List[Dict]:
        """Get top performing revenue streams"""
        performers = [
            {'name': 'SaaS Subscriptions', 'revenue': revenue_data['subscriptions']},
            {'name': 'Services & Consulting', 'revenue': revenue_data['services']},
            {'name': 'API Usage', 'revenue': revenue_data['api_usage']},
            {'name': 'Affiliate Network', 'revenue': revenue_data['affiliates']},
            {'name': 'Content Sales', 'revenue': revenue_data['content']}
        ]

        # Sort by revenue and return top 3
        performers.sort(key=lambda x: x['revenue'], reverse=True)
        return performers[:3]

    def _generate_forecast(self, current_revenue: float) -> Dict[str, Any]:
        """Generate quarterly forecast"""
        q1 = round(current_revenue * 1.15 * 3)
        q2 = round(current_revenue * 1.25 * 3)
        q3 = round(current_revenue * 1.35 * 3)
        q4 = round(current_revenue * 1.45 * 3)

        return {
            'nextQuarter': q1,
            'quarters': {
                'Q1': q1,
                'Q2': q2,
                'Q3': q3,
                'Q4': q4
            },
            'yearTotal': q1 + q2 + q3 + q4
        }

    def _generate_alerts(self, revenue_data: Dict) -> List[Dict]:
        """Generate system alerts based on revenue data"""
        alerts = []

        # Check for low-performing streams
        for stream, amount in [
            ('subscriptions', revenue_data['subscriptions']),
            ('affiliates', revenue_data['affiliates']),
            ('content', revenue_data['content'])
        ]:
            if amount < 30000:
                alerts.append({
                    'type': 'warning',
                    'stream': stream,
                    'message': f"{stream.title()} revenue below $30k threshold"
                })

        # Check customer count
        if revenue_data['total_customers'] < 100:
            alerts.append({
                'type': 'warning',
                'stream': 'customers',
                'message': 'Customer count below 100, increase acquisition efforts'
            })

        return alerts if alerts else [{'type': 'info', 'message': 'All systems operating normally'}]

    def _generate_recommendations(self, revenue_data: Dict) -> List[str]:
        """Generate recommendations based on revenue data"""
        recommendations = []

        # Find lowest performing stream
        streams = {
            'subscriptions': revenue_data['subscriptions'],
            'api_usage': revenue_data['api_usage'],
            'affiliates': revenue_data['affiliates'],
            'content': revenue_data['content'],
            'services': revenue_data['services']
        }

        lowest_stream = min(streams, key=streams.get)
        recommendations.append(f"Focus growth efforts on {lowest_stream.replace('_', ' ')}")
        recommendations.append("Maintain diversified revenue stream portfolio")
        recommendations.append("Consider scaling top-performing services")

        return recommendations

    def _calculate_affiliate_payouts(self, tier: str = None) -> Dict[str, Any]:
        """Calculate affiliate payouts"""
        # Simulated payout calculations
        count = random.randint(10, 30)
        avg_payout = random.randint(200, 800)
        total = count * avg_payout

        return {
            'count': count,
            'total': total,
            'average': avg_payout,
            'tier': tier or 'all'
        }

    def _calculate_content_payouts(self) -> Dict[str, Any]:
        """Calculate content creator payouts"""
        count = random.randint(3, 8)
        total = random.randint(5000, 15000)

        return {
            'count': count,
            'total': total,
            'average': round(total / count) if count > 0 else 0
        }

    def _calculate_service_payouts(self) -> Dict[str, Any]:
        """Calculate service provider payouts"""
        count = random.randint(5, 12)
        total = random.randint(10000, 25000)

        return {
            'count': count,
            'total': total,
            'average': round(total / count) if count > 0 else 0
        }


# Singleton instance
_conductor_instance = None

def get_conductor() -> MasterConductor:
    """Get or create the master conductor instance"""
    global _conductor_instance
    if _conductor_instance is None:
        _conductor_instance = MasterConductor()
    return _conductor_instance
