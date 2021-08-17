# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from serializers import UserSerializer, RetrieveListUserSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Restricts the returned users, by filtering by `user_id` query parameter.
        """
        queryset = User.objects.all()
        user_ids = [int(_id) for _id in self.request.query_params.get('user_id', '').split(',') if _id.strip().isdigit()]

        if user_ids:
            queryset = queryset.filter(pk__in=user_ids)
        return queryset

    def create(self, request, *args, **kwargs):
        return super(UsersViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class.Meta.extra_kwargs = {"username": {"required": False}}
        return super(UsersViewSet, self).update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = RetrieveListUserSerializer
        return super(UsersViewSet, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.serializer_class = RetrieveListUserSerializer
        return super(UsersViewSet, self).list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class UsersByUsernameViewSet(UsersViewSet):
    lookup_field = 'username'

    def get_queryset(self):
        """
        Restricts the returned users, by filtering by `username` query parameter.
        """
        queryset = User.objects.all()
        usernames = [u.strip() for u in self.request.query_params.get('username', '').split(',') if u.strip()]

        if usernames:
            queryset = queryset.filter(username__in=usernames)
        return queryset
