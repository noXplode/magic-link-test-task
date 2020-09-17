# magic-link-test-task

Clone repository, Run:
```
python manage.py migrate
python manage.py createsuperuser
```

## task
Problem: 
We want to create an authentication solution that doesn’t require our users to input an email/password.  
We want to be able to generate a magic link that works for a specific user’s email until we remove access.

Example:
We want to allow test@email.com have access to the site.  So we generate a magic link to test@email.com and an email gets sent to them with the magic link url.  
Every time we hit the url with the magic link token, the counter for that user should increase by 1 (So we know how many times they checked out the link).

Important:
The route that requires the magic link token should not be accessible without the magic link.
We are not going to force any technology for this exercise, but we require that the solution is built in-house (no use of external magic link generators like auth0)
The project should be pushed to github or another repository of your choice.