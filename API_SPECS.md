# Blog API Specs

This a specification for a blog API.

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

### Single Post

```JSON
{
  "post": {
    "slug": "my-first-blog-post-by-kenny",
    "title": "My first blog post",
    "body": "Hello everyone...",
    "tags": ["tag1", "tag2"],
    "createdAt": "2018-03-27T07:43:33.926Z",
    "modifiedAt": "2018-03-27T08:15:42.609Z",
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

### Multiple Posts

```JSON
{
  "posts":[{
    "slug": "my-first-blog-post-by-kenny",
    "title": "My first blog post",
    "body": "Hello everyone...",
    "tags": ["tag1", "tag2"],
    "createdAt": "2018-03-27T07:43:33.926Z",
    "modifiedAt": "2018-03-27T08:15:42.609Z",
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
  "postsCount": 2
}
```

### Single Comment

```JSON
{
  "comment": {
    "id": 1,
    "body": "This post is awesome!",
    "createdAt": "2018-03-27T07:43:33.926Z",
    "modifiedAt": "2018-03-27T08:15:42.609Z",
    "post": "my-first-blog-post-by-kenny",
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
    "body": "This post is awesome!",
    "createdAt": "2018-03-27T07:43:33.926Z",
    "modifiedAt": "2018-03-27T08:15:42.609Z",
    "post": "my-first-blog-post-by-kenny",
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

