# rsg_website
Website made for the developers of RSG Software
All rights to RSG software, Eliaz T and Vanya

## Render configuration

Set `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `ADMIN_EMAIL` in
Render's **Environment** page. On startup the app creates the configured
account (if it does not exist) and grants it the `Owner` role. Existing
databases are also upgraded automatically before login and signup requests
are handled.
