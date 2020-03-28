# Syncref

[![Build Status](https://travis-ci.com/pbexe/syncref.svg?token=AeAAwB1rsJ3YfHiyXGQy&branch=master)](https://travis-ci.com/pbexe/syncref)

## Install

### Docker

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

![Screenshot](/screenshots/screenshot.png)