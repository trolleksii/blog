FROM django

RUN pip install --upgrade pip

RUN pip install gunicorn

COPY ./blog /src/blog

COPY requirements.txt /src

RUN pip install -r /src/requirements.txt

WORKDIR /src/blog

RUN python manage.py migrate

EXPOSE 8000

ENTRYPOINT [ "gunicorn", "--bind", "0.0.0.0:8000", "blog.wsgi:application" ]