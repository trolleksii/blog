# Blog API Specs

This a specification for a Blog API.

## Authentication Header:

Authorization header should be in following format:

`Authorization: Bearer jwt_token`

## JSON Objects returned by API:

All data is returned in JSON format with content type header `Content-Type: application/json`.

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

### List of Followees

```JSON
{
  "followees": [
    "eric",
    "stan",
    "kyle"
  ]
}
```

### Single Post

```JSON
{
  "post": {
    "slug": "my-first-blog-post-by-kenny-sudhe7dy",
    "title": "My first blog post",
    "body": "Hello everyone...",
    "tags": ["tag1", "tag2"],
    "createdAt": "2018-03-27T07:43:33.926Z",
    "updatedAt": "2018-03-27T08:15:42.609Z",
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
    "slug": "my-first-blog-post-by-kenny-ktigjr84",
    "title": "My first blog post",
    "body": "Hello everyone...",
    "tags": ["tag1", "tag2"],
    "createdAt": "2018-03-27T07:43:33.926Z",
    "updatedAt": "2018-03-27T08:15:42.609Z",
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
    "slug": "my-second-blog-post-by-kenny-jwusha8r",
    "title": "My second blog post",
    "body": "Hi again...",
    "tags": [],
    "createdAt": "2018-03-28T07:43:33.926Z",
    "updatedAt": "2018-03-28T08:15:42.609Z",
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
  "postsCount": 2,
  "previous": null,
  "next": null
}
```

### Single Comment

```JSON
{
  "comment": {
    "id": 1,
    "title": "This post is awesome!",
    "body": "What a plesant surprise",
    "createdAt": "2018-03-27T07:43:33.926Z",
    "updatedAt": "2018-03-27T08:15:42.609Z",
    "post": "my-first-blog-post-by-kenny-hfyr74ye",
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
    "title": "This post is awesome!",
    "body": "What a plesant surprise",
    "createdAt": "2018-03-27T07:43:33.926Z",
    "updatedAt": "2018-03-27T08:15:42.609Z",
    "post": "my-first-blog-post-by-kenny-fh4jdyf6",
    "author": {
      "username": "kenny",
      "following": false
    }
  }],
  "commentsCount": 1,
  "previous": null,
  "next": null
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


### Errors and status codes

All errors are returned in the following format:

```JSON
{
  "errors": {
    "password": [
      "This field is required."
    ],
    "username": [
      "This field is required."
    ]
  }
}
```


#### Status codes in use:

400 - Bad Request, when a request data failed validation, or if there was no data at all

401 - Unauthorized requests, when a request requires authentication but it isn't provided

403 - Forbidden requests, when a request may be valid but the user doesn't have permissions to perform the action

404 - Not found requests, when a resource can't be found to fulfill the request



## Endpoints:

### Authentication:

`POST /api/posts/login`

Log in to get a JWT token, which will be necessary in every other endpoint that requires authentication.

Example request body:
```JSON
{
  "user":{
    "username": "kenny",
    "password": "qwerty123"
  }
}
```

No authentication required, returns a [User](#user)

Required fields: `username`, `password`


### Registration:

`POST /api/users`

Example request body:
```JSON
{
  "user":{
    "username": "kenny",
    "email": "kenneth@spmail.com",
    "password": "qwerty123"
  }
}
```

No authentication required, returns a [User](#user)

Required fields: `username`, `password`

Optional fields: `email`


### Get Current User

`GET /api/user`

Authentication required, returns a [User](#user)


### Update Current User

`PUT /api/user`

Example request body:
```JSON
{
  "user":{
    "email": "kenny@gmail.com",
    "pic": "https://static.blog.com/images/kennyface.png"
  }
}
```

Authentication required, returns the modified [User](#user)

Accepted fields: `email`, `password`, `about`, `pic`


### Get Profile Info

`GET /api/profiles/:username`

Authentication optional, returns a [Profile](#profile)


### Follow user

`POST /api/profiles/:username/follow`

Authentication required, returns a [Profile](#profile)

No additional parameters required


### Unfollow user

`DELETE /api/profiles/:username/follow`

Authentication required, returns a [Profile](#profile)

No additional parameters required


### Get Current User Followees

`GET /api/profile/followees`

Authentication required, returns a [List of Followees](#list-of-followees)


### List Posts

`GET /api/posts`

Returns paginated list of posts, provide `tag`, `author` or `favorited` query parameter to filter results

Query Parameters:

Filter by tag:

`?tag=Django`

Filter by author:

`?author=kenny`

Favorited by user:

`?favorited=stan`

Limit number of posts (default is 5):

`?limit=20`

Offset/skip number of posts (default is 0):

`?offset=0`

Authentication optional, will return [Multiple Posts](#multiple-posts), ordered by most recent first


### Feed Posts

`GET /api/posts/feed`

Returns list of posts writen by users you follow.

Can also take `limit` and `offset` query parameters like [List Posts](#list-posts)

Authentication required, will return [Multiple Posts](#multiple-posts), created by followed users, ordered by most recent first.


### Get Post

`GET /api/posts/:slug`

No authentication required, will return [single post](#single-post)


### Create Post

`POST /api/posts`

Example request body:

```JSON
{
  "post": {
    "title": "How to white a blog API from scratch",
    "body": "Easy as a pie!",
    "tagList": ["Django", "REST", "API"]
  }
}
```

Authentication required, will return a [Post](#single-post)

Required fields: `title`, `body`

Optional fields: `tagList` as an array of strings


### Update Post

`PUT /api/posts/:slug`

Example request body:

```JSON
{
  "post": {
    "body": "Actually its not that easy :("
  }
}
```

Authentication required, returns the updated [Post](#single-post)

Optional fields: `title`, `body`, `tagList`

The `slug` also gets updated when the `title` is changed


### Delete Post

`DELETE /api/posts/:slug`

Authentication required

User can only delete the posts he/she wrote


### Like the Post

`POST /api/posts/:slug/like`

Authentication required

User is not allowed to like his own posts, 'likes' can't be withdrawn or changed to 'dislikes'


### Dislike the Post

`DELETE /api/posts/:slug/like`

Authentication required

User is not allowed to dislike his own posts, 'dislikes' can't be withdrawn or changed to 'likes'


### Add Post to Favorites

`POST /api/posts/:slug/favorite`

Authentication required


### Remove Post from Favorites

`DELETE /api/posts/:slug/favorite`

Authentication required


### Add Comment to the Post

`POST /api/posts/:slug/comments`

Example request body:

```JSON
{
  "comment": {
    "title": "Thank you!",
    "body": "Such an informative read."
  }
}
```

Authentication required, returns the created [Comment](#single-comment)

Required field: `title`, `body`



### Get Comments from a Post

`GET /api/posts/:slug/comments`

Authentication optional, returns [multiple comments](#multiple-comments)



### Delete Comment

`DELETE /api/posts/:slug/comments/:id`

Authentication required

User can delete only the comments he/she wrote


`GET /api/tags`


### Get Tags

`GET /api/tags`

No authentication required, returns a [List of Tags](#list-of-tags)
