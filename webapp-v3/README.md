# Pinehead Records webapp v3

This version features:

- federated web identity (Cognito)
- fine-grained policies
- triggers
- improved security
- DAX

## Social Login

More info: <https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-social-idp.html>

### Prerequisites

Before you begin, you need:
- A user pool with an application client and a user pool domain
- A social identity provider (e.g. Amazon, Facebook, Google)

### Step 1 - Register with Social IdP

### Step 2 - Add Social IdP to Your User Pool

### Step 3 - Test Your Social IdP Configuration

```text
https://<your_user_pool_domain>/login?response_type=code&client_id=<your_client_id>&redirect_uri=https://www.example.com
```

You can find your domain on the user pool **Domain name** console page. The client_id is on the **App client settings** page. Use your callback URL for the **redirect_uri** parameter. This is the URL of the page where your user will be redirected after a successful authentication.

https://pinehead.auth.us-east-1.amazoncognito.com/login?response_type=code&client_id=24ftcdanu65gufq324de69hkif&redirect_uri=http://localhost:5000


### Step 4 - Configure Google API

https://developers.google.com/identity/sign-in/web/sign-in

Configure a project for Google signin

### Generate self-signed cert

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```
