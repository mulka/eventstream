[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

These environment variables need to be set:

- COOKIE\_SECRET
- TWITTER\_CONSUMER\_KEY
- TWITTER\_CONSUMER\_SECRET
- TWITTER\_ACCESS\_TOKEN
- TWITTER\_ACCESS\_TOKEN\_SECRET

COOKIE_SECRET is just a random string you generate used to sign Tornado's secure cookies. You could just mash on the keyboard, pick a password, or do what I do which is generate a secure password using LastPass. You can get the Twitter variables by creating a Twitter application here:
https://apps.twitter.com/app/new
