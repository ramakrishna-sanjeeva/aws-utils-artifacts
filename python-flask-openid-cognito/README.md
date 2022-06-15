# Python Flask application leveraging Amazon Cognito as OpenID provider for user authentication

Reference Python Flash application which leverages Amazon Cognito as OpenID provider for user authentication. 

Cognito setup details are available @ https://www.cognitobuilders.training/20-lab1/20-setup-and-explore/40-explore-openid-config/ 

Ensure the Cognito's Allowed callback URLs has been configured with the redirect uri's as mentioned in the client_secrets.json.

Start the Flash application using the following command

    flask run --cert=adhoc

