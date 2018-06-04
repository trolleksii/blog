FROM django as django-with-pkgs

RUN pip install --upgrade pip

COPY requirements.txt /src/

RUN pip install -r /src/requirements.txt



FROM django-with-pkgs

COPY ./blog /src/blog

WORKDIR /src/blog

RUN python manage.py migrate

EXPOSE 8000

ENTRYPOINT [ "gunicorn", "--bind", "0.0.0.0:8000", "blog.wsgi:application" ]