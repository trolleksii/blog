from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class PostsPaginaton(LimitOffsetPagination):

    default_limit = 5

    def get_paginated_response(self, data):
        return Response(
            {
                'postsCount': self.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'posts': data
            },
            status=status.HTTP_200_OK
        )
