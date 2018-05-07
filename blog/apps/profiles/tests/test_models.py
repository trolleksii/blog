from django.test import TestCase

from apps.posts.models import Post

from apps.authentication.models import User

from apps.profiles.models import Profile


class ProfileModelTests(TestCase):

    fixtures = ['profiles.json']

    def test_str_method(self):
        user = User.objects.get(username='kenny')
        profile = Profile.objects.get(user=user)
        self.assertEqual(str(profile), user.username)

    def test_follow(self):
        kenny = Profile.objects.get(user__username='kenny')
        kyle = Profile.objects.get(user__username='kyle')
        followees_before = kyle.followees.all().count()
        kyle.follow(kenny)
        followees_after = kyle.followees.all().count()
        self.assertEqual(followees_after - followees_before, 1)
        self.assertTrue(
            kyle.followees.filter(user__username='kenny').exists()
        )

    def test_unfollow(self):
        kenny = Profile.objects.get(user__username='kenny')
        kyle = Profile.objects.get(user__username='kyle')
        followees_before = kenny.followees.all().count()
        kenny.unfollow(kyle)
        followees_after = kenny.followees.all().count()
        self.assertEqual(followees_before - followees_after, 1)
        self.assertFalse(
            kenny.followees.filter(user__username='kyle').exists()
        )

    def test_has_in_followees(self):
        kenny = Profile.objects.get(user__username='kenny')
        kyle = Profile.objects.get(user__username='kyle')
        self.assertTrue(
            kenny.has_in_followees(kyle)
        )
        self.assertFalse(
            kyle.has_in_followees(kenny)
        )

    def test_follow_yourself(self):
        profile = Profile.objects.get(user__username='kyle')
        profile.follow(profile)
        self.assertFalse(
            profile.followees.filter(user__username='kyle').exists()
        )

    def test_favorite(self):
        kenny = Profile.objects.get(user__username='kenny')
        post = Post.objects.first()
        followees_before = kenny.favorites.all().count()
        kenny.favorite(post)
        followees_after = kenny.favorites.all().count()
        self.assertEqual(followees_after - followees_before, 1)
        self.assertTrue(
            kenny.favorites.filter(slug=post.slug).exists()
        )

    def test_unfavorite(self):
        kyle = Profile.objects.get(user__username='kyle')
        post = Post.objects.first()
        followees_before = kyle.favorites.all().count()
        kyle.unfavorite(post)
        followees_after = kyle.favorites.all().count()
        self.assertEqual(followees_before - followees_after, 1)
        self.assertFalse(
            kyle.favorites.filter(slug=post.slug).exists()
        )

    def test_has_in_favorites(self):
        kenny = Profile.objects.get(user__username='kenny')
        kyle = Profile.objects.get(user__username='kyle')
        post = Post.objects.first()
        self.assertTrue(
            kyle.has_in_favorites(post)
        )
        self.assertFalse(
            kenny.has_in_favorites(post)
        )

    def test_like(self):
        kyle = Profile.objects.get(user__username='kyle')
        post = Post.objects.first()
        likes_before = post.liked_by.count()
        kyle.like(post)
        likes_after = post.liked_by.count()
        self.assertEqual(likes_after - likes_before, 1)

    def test_like_own_post(self):
        kenny = Profile.objects.get(user__username='kenny')
        post = Post.objects.first()
        likes_before = post.liked_by.count()
        kenny.like(post)
        likes_after = post.liked_by.count()
        self.assertEqual(likes_after, likes_before)

    def test_2xlike(self):
        kyle = Profile.objects.get(user__username='kyle')
        post = Post.objects.first()
        likes_before = post.liked_by.count()
        kyle.like(post)
        kyle.like(post)
        likes_after = post.liked_by.count()
        self.assertNotEqual(likes_after - likes_before, 2)

    def test_dislike(self):
        kyle = Profile.objects.get(user__username='kyle')
        post = Post.objects.first()
        dislikes_before = post.disliked_by.count()
        kyle.dislike(post)
        dislikes_after = post.disliked_by.count()
        self.assertEqual(dislikes_after - dislikes_before, 1)

    def test_2xdislike(self):
        kyle = Profile.objects.get(user__username='kyle')
        post = Post.objects.first()
        dislikes_before = post.disliked_by.count()
        kyle.dislike(post)
        kyle.dislike(post)
        dislikes_after = post.disliked_by.count()
        self.assertNotEqual(dislikes_after - dislikes_before, 2)

    def test_like_then_dislike(self):
        kyle = Profile.objects.get(user__username='kyle')
        post = Post.objects.first()
        likes_before = post.liked_by.count()
        dislikes_before = post.disliked_by.count()
        kyle.like(post)
        kyle.dislike(post)
        likes_after = post.liked_by.count()
        dislikes_after = post.disliked_by.count()
        self.assertEqual(likes_after - likes_before, 1)
        self.assertEqual(dislikes_after - dislikes_before, 0)

    def test_dislike_then_like(self):
        kyle = Profile.objects.get(user__username='kyle')
        post = Post.objects.first()
        likes_before = post.liked_by.count()
        dislikes_before = post.disliked_by.count()
        kyle.dislike(post)
        kyle.like(post)
        likes_after = post.liked_by.count()
        dislikes_after = post.disliked_by.count()
        self.assertEqual(likes_after - likes_before, 0)
        self.assertEqual(dislikes_after - dislikes_before, 1)

    def test_can_vote_for(self):
        kyle = Profile.objects.get(user__username='kyle')
        stan = Profile.objects.get(user__username='stan')
        post = Post.objects.first()
        self.assertTrue(kyle.can_vote_for(post))
        self.assertTrue(stan.can_vote_for(post))
        kyle.like(post)
        stan.dislike(post)
        self.assertFalse(kyle.can_vote_for(post))
        self.assertFalse(stan.can_vote_for(post))
