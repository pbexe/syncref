# Syncref

[![Build Status](https://travis-ci.com/pbexe/syncref.svg?token=AeAAwB1rsJ3YfHiyXGQy&branch=master)](https://travis-ci.com/pbexe/syncref)

## Install

### Docker

Set the admin username and password using environment variables:

```sh
export DJANGO_SUPERUSER_PASSWORD="your_password_here"
export USERNAME_FIELD="probably_something_like_admin"
export EMAIL_FIELD="email@example.com"
```

```
docker-compose up --build
```

### Manually

Make sure there is an instance of PostgreSQL running and `/src/syncref/settings.py` is configured accordingly. The project is currently configured to use a remote version of Grobid but a local version can be run using the script in `/scripts/grobid`.

The development server can then be started with:
```
cd src
python manage.py runserver
```

![Screenshot](/screenshots/app.png)
