# Studio Dashboard Guide

Welcome to LeaderboardX! This guide will help you get started with managing your games and leaderboards through our studio dashboard.

## 🚀 Getting Started

### 1. Studio Registration
- Register your studio at `/studios/register`
- Verify your email address
- Wait for admin approval (typically 1-2 business days)
- Receive your studio access credentials

### 2. First Login
- Access the dashboard at `/dashboard`
- Use your registered email and password
- Complete your studio profile setup

## 🎮 Managing Games

### Creating Your First Game
1. Navigate to **Games** in the sidebar
2. Click **"Add New Game"**
3. Fill in game details:
   - **Game Name**: Display name for your game
   - **Description**: Brief description of your game
   - **Platform**: PC, Mobile, Console, etc.

4. Save to receive your **Game ID** and **API Key**
5. Keep your API key secure - you'll need it for integration

### Game Settings
- **API Key Management**: Regenerate keys if compromised
- **Rate Limits**: Monitor your API usage
- **Webhook URLs**: Receive real-time notifications
- **Status Control**: Enable/disable game access

## 🏆 Leaderboard Management

### Creating Leaderboards
1. Select your game from the Games list
2. Click **"Add Leaderboard"**
3. Configure leaderboard settings:
   - **Name**: Human-readable name (e.g., "Daily High Scores")
   - **Key**: Unique identifier for API calls (e.g., "daily_scores")
   - **Score Type**: Highest score wins vs. Lowest time wins
   - **Max Entries**: Maximum number of scores to store
   - **Public**: Whether leaderboard is publicly viewable

### Leaderboard Types
- **Global Leaderboards**: All-time best scores
- **Daily/Weekly**: Time-based competitions
- **Seasonal**: Special events or tournaments
- **Private**: Internal testing or special groups

## 👥 Team Management

### Adding Team Members
1. Go to **Team** in the dashboard
2. Click **"Invite Member"**
3. Enter their email and select role:
   - **Admin**: Full access to all studio features
   - **Manager**: Game and leaderboard management
   - **Developer**: Read-only access and API integration

### Role Permissions
| Feature | Admin | Manager | Developer |
|---------|-------|---------|-----------|
| Invite team members | ✅ | ❌ | ❌ |
| Manage billing | ✅ | ❌ | ❌ |
| Create/edit games | ✅ | ✅ | ❌ |
| View analytics | ✅ | ✅ | ✅ |
| API integration | ✅ | ✅ | ✅ |

## 📊 Analytics Dashboard

### Key Metrics
- **Total Players**: Unique players across all games
- **Daily Active Players**: Players who submitted scores today
- **API Requests**: Total API calls this month
- **Top Games**: Your most popular games by activity

### Analytics Features
- **Real-time Updates**: Live player activity
- **Filtering**: By game, date range, leaderboard
- **Export**: Download data as CSV or JSON
- **Trends**: Historical performance charts

### Performance Monitoring
- **Response Times**: API performance metrics
- **Error Rates**: Failed API requests
- **Usage Patterns**: Peak activity times
- **Geographic Data**: Player distribution

## 💳 Subscription & Billing

### Subscription Tiers
- **Free**: 10,000 API requests/month, 3 games max
- **Pro**: 100,000 API requests/month, unlimited games
- **Enterprise**: Custom limits, dedicated support

### Managing Your Subscription
- View current usage and limits
- Upgrade/downgrade plans
- Download invoices
- Set up payment methods
- Configure billing alerts

### Usage Monitoring
- Real-time request counters
- Monthly usage trends
- Overage notifications
- Cost projections

## 🔧 Settings & Configuration

### Studio Settings
- **Profile**: Studio name, description, contact info
- **API Keys**: Regenerate studio-level API keys
- **Webhooks**: Configure real-time notifications
- **Security**: Two-factor authentication

### Notification Settings
- **Email Alerts**: API limit warnings, new scores
- **Webhook Events**: Real-time game events
- **Slack Integration**: Team notifications (coming soon)

## 🆘 Support & Help

### Getting Help
- **Documentation**: Complete API and integration guides
- **Support Tickets**: Contact our support team
- **Community**: Join our Discord for discussions
- **Status Page**: Check system status and uptime

### Common Issues
- **API Key Issues**: How to regenerate and update keys
- **Rate Limiting**: Understanding and managing limits
- **Score Validation**: Preventing cheating and invalid scores
- **Integration Problems**: Common setup mistakes

---

*Need help? Contact our support team at support@leaderboardx.com*