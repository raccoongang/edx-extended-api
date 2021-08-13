# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from serializers import UserSerializer, ListUserSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class CreateUserView(CreateModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        return super(CreateUserView, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super(CreateUserView, self).update(request, *args, **kwargs)


class ListUserView(ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ListUserSerializer

    def get_queryset(self):
        """
        Restricts the returned users, by filtering by `username` or `user_id` query parameter.
        """
        queryset = User.objects.all()
        usernames = [u.strip() for u in self.request.query_params.get('username', '').split(',') if u.strip()]
        user_ids = [int(_id) for _id in self.request.query_params.get('user_id', '').split(',') if _id.strip().isdigit()]

        if usernames:
            queryset = queryset.filter(username__in=usernames)
        elif user_ids:
            queryset = queryset.filter(pk__in=user_ids)
        return queryset
