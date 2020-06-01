FROM jerob/pipenv as build
MAINTAINER <j.robert@ccifrance.fr>

ENV DEBUG=False

ADD Pipfile /app/Pipfile
# RUN rm Pipfile.lock || echo "no Pipelick.lock found"
RUN pipenv --version && pipenv install
RUN pipenv lock -r > requirements.txt
RUN cat requirements.txt

FROM jerob/django3
MAINTAINER <j.robert@ccifrance.fr>

# +-----------------------------------------------------+
# | Set defautl env vars                                |
# +-----------------------------------------------------+

# Postgres HA Database
# connexion parameter
# default is set for local_dev
ENV DJANGO_DATABASE ${DJANGO_DATABASE:-local_dev}
ENV POSTGRES_DB_HOST ${POSTGRES_DB_HOST:-''}
ENV POSTGRES_DB_PORT ${POSTGRES_DB_PORT:-''}
ENV POSTGRES_LOGIN ${POSTGRES_LOGIN:-''}
ENV POSTGRES_PASSWORD ${POSTGRES_PASSWORD:-''}
# Create django admin user with password
# while create container
ENV DJANGO_ADMIN_LOGIN ${DJANGO_ADMIN_LOGIN:-}
ENV DJANGO_ADMIN_PASSWORD ${DJANGO_ADMIN_PASSWORD:-}
ENV DJANGO_ADMIN_EMAIL ${DJANGO_ADMIN_EMAIL:-}

# Copy src to app src in container
# and set as default directory
COPY . /app
WORKDIR /app
COPY --from=build /app/requirements.txt .
RUN cat requirements.txt

# +-----------------------------------------------------+
# | OS level dependencies                               |
# +-----------------------------------------------------+
RUN apt update && apt install memcached git -y

# +-----------------------------------------------------+
# | Python level dependencies                           |
# +-----------------------------------------------------+
# RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir git+https://github.com/akhilputhiry/keycloak-client
# Remove Pipflie.lock
# New lock will be created with
# pipenv install command
# allow pipenv to resolve automatically
RUN rm Pipfile.lock || echo "no Pipelick.lock found"
# Install pipenv
# RUN pip install --upgrade pip
# RUN pip install pipenv
# Install dependencies from Pipfile
# RUN pipenv install --verbose

# CMD python manage.py runserver 0.0.0.0:8000
ENTRYPOINT bash