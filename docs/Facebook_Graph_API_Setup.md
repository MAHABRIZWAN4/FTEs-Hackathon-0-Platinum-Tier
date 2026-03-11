# Facebook Graph API Setup Guide

## Step 1: Create Facebook Developer Account

1. **Visit**: https://developers.facebook.com/
2. **Click**: "Get Started" (top right)
3. **Login**: Apne Facebook account se login karo
4. **Complete Registration**: Developer account registration complete karo

## Step 2: Create Facebook App

1. **Go to**: https://developers.facebook.com/apps/
2. **Click**: "Create App"
3. **Select**: "Business" type
4. **Fill Details**:
   - App Name: "Gold Tier AI Employee"
   - App Contact Email: Your email
   - Business Account: (optional)
5. **Click**: "Create App"

## Step 3: Add Facebook Pages Product

1. **In your App Dashboard**, left sidebar mein "Add Products" section
2. **Find**: "Facebook Login" - Click "Set Up"
3. **Settings** > **Basic**:
   - App Domains: localhost (for testing)
   - Privacy Policy URL: (optional for testing)

## Step 4: Get Page Access Token

### Method A: Using Graph API Explorer (Easy for Testing)

1. **Visit**: https://developers.facebook.com/tools/explorer/
2. **Select**: Your App (top dropdown)
3. **Click**: "Generate Access Token"
4. **Select Permissions**:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
5. **Click**: "Generate Token"
6. **Copy**: Token ko save karo

### Method B: Get Long-Lived Page Token (Recommended)

1. **Get User Access Token** (from Graph Explorer)
2. **Get Page ID**:
   ```bash
   curl "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_USER_TOKEN"
   ```
3. **Response mein** tumhare pages ki list aayegi with Page Access Tokens
4. **Copy**: Page Access Token

## Step 5: Test Token

```bash
curl "https://graph.facebook.com/v18.0/me?access_token=YOUR_PAGE_TOKEN"
```

Agar response mein page details aaye, token working hai!

## Step 6: Post to Facebook

```bash
curl -X POST "https://graph.facebook.com/v18.0/PAGE_ID/feed" \
  -d "message=Test post from Gold Tier AI Employee" \
  -d "access_token=YOUR_PAGE_TOKEN"
```

## Important Notes

- **User Token**: Short-lived (1-2 hours)
- **Page Token**: Can be long-lived (60 days or never expires)
- **Permissions**: Make sure app has required permissions
- **App Review**: For production, Facebook app review required

## Security

- **Never commit** access tokens to git
- **Use .env file** for tokens
- **Rotate tokens** regularly
