# Blog API Specs

This a specofication for a blog API.

### Authentication Header:

`Authorization: Token jwt_token`

## JSON Objects returned by API:

All data are returned in JSON format with content type header `Content-Type: application/json`.

### User

```JSON
{
  "user": {
    "username": "kenny",
    "email": "kenny@somemail.com",
    "about": "I'm a cool guy",
    "pic": "https://static.blog.com/images/kennyface.png",
    "token": "jwt_token",
  }
}
```

### Profile

```JSON
{
  "profile": {
    "username": "kenny",
    "about": "I'm a cool guy",
    "pic": "https://static.blog.com/images/kennyface.png",
    "following": false
  }
}
```

### Single Article

```JSON
{
  "article": {
    "slug": "my-first-blog-post-by-kenny",
    "title": "My first blog post",
    "body": "Hello everyone...",
    "tags": ["tag1", "tag2"],
    "favorited": false,
    "likes": 0,
    "dislikes": 0,
    "author": {
      "username": "kenny",
      "about": "I'm a cool guy",
      "pic": "https://static.blog.com/images/kennyface.png",
      "following": false
    }
  }
}
```

### Multiple Articles

```JSON
{
  "articles":[{
    "slug": "my-first-blog-post-by-kenny",
    "title": "My first blog post",
    "body": "Hello everyone...",
    "tags": ["tag1", "tag2"],
    "favorited": false,
    "likes": 0,
    "dislikes": 0,
    "author": {
      "username": "kenny",
      "about": "I'm a cool guy",
      "pic": "https://static.blog.com/images/kennyface.png",
      "following": false
    }
  }, {
    "slug": "my-second-blog-post-by-kenny",
    "title": "My second blog post",
    "body": "Hi again...",
    "tags": [],
    "favorited": false,
    "likes": 0,
    "dislikes": 0,
    "author": {
      "username": "kenny",
      "about": "I'm a cool guy",
      "pic": "https://static.blog.com/images/kennyface.png",
      "following": false
    }
  }],
  "articlesCount": 2
}
```

### Single Comment

```JSON
{
  "comment": {
    "id": 1,
    "body": "This article is awesome!",
    "createdAt": "2018-03-26T15:51:16.637Z",
    "updatedAt": "2018-03-26T17:03:11.637Z",
    "author": {
      "username": "kenny",
      "following": false
    }
  }
}
```

### Multiple comments

```JSON
{
  "comment": [{
    "id": 1,
    "createdAt": "2018-03-26T03:22:56.637Z",
    "updatedAt": "2018-03-26T03:22:56.637Z",
    "body": "This article is awesome!",
    "author": {
      "username": "kenny",
      "following": false
    }
  }],
  "commentsCount": 1
}
```

### List of Tags

```JSON
{
  "tags": [
    "tag1",
    "tag2"
  ]
}
```

