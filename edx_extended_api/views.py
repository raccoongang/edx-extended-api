# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from serializers import UserSerializer
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
