"""Sample data and utilities for IVR system initialization"""

SAMPLE_DOCUMENTS = [
    {
        "title": "Billing FAQ - How to Check Your Bill",
        "content": """How to Check Your Bill:
        
To check your current bill:
1. Log into your account with your username and password
2. Navigate to the 'Billing' section from the main menu
3. Click on 'View Current Bill'
4. You can see itemized charges and payment due date

Your bill is automatically generated on the 1st of each month. 
You can view up to 12 months of billing history.
If you have questions about specific charges, please contact our billing department.

Payment Methods:
- Credit/Debit Card
- Bank Transfer
- Wire Transfer
- Check (by mail)

Late fees apply if payment is not received by the due date.
You can set up automatic payments to avoid missed deadlines.""",
        "category": "billing",
        "tags": ["billing", "faq", "payment", "invoice"]
    },
    {
        "title": "Common Technical Issues and Solutions",
        "content": """Troubleshooting Common Issues:

Connection Problems:
- Restart your device
- Check your internet connection speed
- Try connecting to a different network
- Disable VPN temporarily
- Clear browser cache and cookies

Still having issues? Try:
1. Update your browser to the latest version
2. Disable browser extensions one-by-one
3. Try accessing from a different device
4. Check if the service is operational at our status page

Performance Issues:
- Close unnecessary applications
- Clear browser cache
- Check your device storage
- Reduce number of open tabs
- Try incognito/private mode

Browser Compatibility:
- Chrome: Version 90+
- Firefox: Version 88+
- Safari: Version 14+
- Edge: Version 90+

If problems persist, contact technical support with:
- Your device model
- Browser and version
- Error messages (if any)
- Time issue occurred
- Steps already taken""",
        "category": "technical",
        "tags": ["technical", "troubleshooting", "support", "browser"]
    },
    {
        "title": "Account Security and Management",
        "content": """Secure Your Account:

Password Security:
- Use a minimum of 12 characters
- Include uppercase, lowercase, numbers, and special characters (!@#$%^&*)
- Don't use personal information (birthdate, names)
- Change password every 90 days
- Never share your password

Two-Factor Authentication (2FA):
1. Go to Account Settings > Security
2. Enable "Two-Factor Authentication"
3. Choose method: SMS, Email, or Authenticator App
4. Verify with code when logging in

Recognize Phishing Attempts:
- Legitimate emails come from @ourdomain.com
- We never ask for passwords in emails
- Check sender email carefully
- Hover over links before clicking
- Report suspicious emails to security@ourdomain.com

What to Do if Compromised:
1. Change your password immediately
2. Enable 2FA if not already active
3. Review recent account activity
4. Check linked payment methods
5. Contact support if unauthorized charges found

Privacy:
- We never sell your data
- Your information is encrypted
- Review our privacy policy regularly
- Control what data is shared in settings""",
        "category": "account",
        "tags": ["security", "account", "privacy", "password"]
    },
    {
        "title": "Subscription Plans and Pricing",
        "content": """Available Plans:

Basic Plan - $9.99/month
- Up to 5 projects
- 5GB storage
- Community support
- Email support (24-48 hours)

Professional Plan - $29.99/month
- Up to 50 projects
- 100GB storage
- Priority email support (24 hours)
- Phone support (business hours)
- Advanced analytics

Enterprise Plan - Custom pricing
- Unlimited projects
- Unlimited storage
- 24/7 dedicated support
- Custom integrations
- SLA guaranteed
- Dedicated account manager

Plan Features:
- Cancel anytime (no long-term contracts)
- Upgrade/downgrade anytime
- No setup fees
- 30-day free trial available
- Billing cycles: Monthly or Annual

Payment:
- Credit cards (Visa, Mastercard, Amex)
- Bank transfers available
- Company purchase orders accepted
- Annual billing gets 15% discount

Getting Help:
For all billing and plan questions, contact: billing@ourdomain.com""",
        "category": "billing",
        "tags": ["pricing", "plans", "subscription", "billing"]
    },
    {
        "title": "Getting Started Guide",
        "content": """Welcome to Our Service! Getting Started:

Step 1: Create Your Account
1. Click Sign Up on the homepage
2. Enter your email address
3. Create a strong password
4. Verify your email
5. Complete your profile

Step 2: Set Up Your First Project
1. Go to Dashboard
2. Click "New Project"
3. Name your project
4. Choose your plan
5. Configure initial settings

Step 3: Add Users
1. Go to Project Settings
2. Click "Invite Team Member"
3. Enter email addresses
4. Set permission levels
5. Send invitations

Step 4: Explore Features
- Review documentation
- Watch tutorial videos
- Experiment in demo mode
- Join webinars

Step 5: Get Support
- Read FAQ section
- Browse knowledge base
- Contact support team
- Join community forum

Common Tasks:
- Creating projects: Admin dashboard > New Project
- Managing team: Settings > Team Members
- Viewing analytics: Dashboard > Analytics
- Exporting data: Settings > Data Export
- Updating settings: Account > Preferences

Need Help?
- Email: support@ourdomain.com
- Phone: 1-800-SUPPORT (24/7)
- Live chat: Available on website
- Status page: status.ourdomain.com""",
        "category": "general",
        "tags": ["getting-started", "onboarding", "tutorial", "help"]
    }
]


def initialize_sample_kb(rag_service):
    """Initialize knowledge base with sample documents"""
    print("Initializing sample knowledge base...")
    
    for doc in SAMPLE_DOCUMENTS:
        try:
            result = rag_service.add_document(
                title=doc["title"],
                content=doc["content"],
                category=doc["category"],
                tags=doc["tags"]
            )
            print(f"✓ Added: {doc['title']}")
        except Exception as e:
            print(f"✗ Error adding {doc['title']}: {e}")
    
    print(f"\n✓ Initialized {len(SAMPLE_DOCUMENTS)} sample documents")
