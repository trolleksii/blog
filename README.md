# Blog API

This is a simple blog API with a bare minimum of functions associated with a typical blog.


## How to install

1. Install Python3, pip, venv:

```SH
sudo apt install python3 python3-pip python3-venv
```

2. Clone this repository:

```SH
mkdir project
cd ./project
git clone https://github.com/trolleksii/blog.git
```

3. Create a new virtual environment with Python 3 interpreter:

```SH
virtualenv -p $(which python3) ./venv
```

4. Activate it:

```SH
source ./venv/bin/activate
```

6. Install required packages from requirements.txt:

```SH
pip install -r ./blog/requirements.txt
```

7. `cd` into ./blog/blog:

```SH
cd ./blog/blog/
```

8. Perform database migrations:

```SH
python manage.py migrate
```

9. Run tests to make sure that everything is working as it should:

`python manage.py test`

## How to use it

You can use cURL, Postman or any other application which allows you to make API requests.


1. Register a user:
```SH
curl --request POST --header "Content-Type: application/json" \
--data '{"user":{"username": "testuser", "password": "qwerty123"}}' \
http://localhost:8000/api/users/login
```
Response will contain your token.


2. Write a new post(don't forget tu put your token into corresponding header field):

```SH
curl --request POST --header "Content-Type: application/json" \
--header "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NiwiZXhwIjoxNTIzMzg2NzE3LjU1ODY0N30.scxIVv7YVy9FWyjYNxMf-VHlLqfdjhppWbfs1oSMdpw" \
--data '{"post":{"title": "API post title", "body": "API post body"}}' \
http://localhost:8000/api/posts
```

3. Try out any other endpoint described in [API specs](https://github.com/trolleksii/blog/blob/master/API_SPECS.md).
