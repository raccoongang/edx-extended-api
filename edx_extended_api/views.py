# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics, viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from serializers import CourseSerializer, UserSerializer, RetrieveListUserSerializer, UserProgressSerializer
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

User = get_user_model()


class ByUsernameMixin:
    lookup_field = 'username'


class UserFilterMixin:
    filter_by_supervisor = False

    def get_queryset(self):
        """
        Restricts the returned users, by filtering by `user_id` query parameter.
        """
        queryset = User.objects.all()
        user_ids = [int(_id) for _id in self.request.query_params.get('user_id', '').split(',') if _id.strip().isdigit()]
        usernames = [u.strip() for u in self.request.query_params.get('username', '').split(',') if u.strip()]

        self.queryset_filter = {}
        if user_ids:
            self.queryset_filter = {'pk__in': user_ids}
        elif usernames:
            self.queryset_filter = {'username__in': usernames}
        elif self.filter_by_supervisor:
            supervisors = [u.strip() for u in self.request.query_params.get('supervisor', '').split(',') if u.strip()]
            self.queryset_filter = supervisors and {'profile__lt_supervisor__in': supervisors} or {}
        return queryset.filter(**self.queryset_filter)


class UsersViewSet(UserFilterMixin, viewsets.ModelViewSet):
    queryset_filter = {}
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    DEACTIVATE_STATUSES = {
        True: 'user_deactivated',
        False: 'user_already_inactive',
        None: 'user_not_found'
    }

    def check_status(self, request, default_status):
        resp = {'status': default_status}
        queryset = self.get_queryset()
        lookup_field = self.lookup_url_kwarg or self.lookup_field
        lookup_filter = {lookup_field: self.kwargs.get(lookup_field)}

        if lookup_filter[lookup_field] and not queryset.filter(**lookup_filter).exists():
            resp = {'status': 'user_not_found'}
        elif lookup_filter[lookup_field] and queryset.filter(is_active=False, **lookup_filter).exists():
            resp = {'status': 'user_inactive'}
        elif queryset.filter(username=request.data.get('username')).exists():
            resp = {'status': 'username_already_used'}
        elif queryset.filter(email=request.data.get('email')).exists():
            resp = {'status': 'email_already_used'}
        else:
            return resp

        return Response(resp, status=status.HTTP_409_CONFLICT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        resp = self.check_status(request, 'user_created')
        if not isinstance(resp, dict):
            return resp

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        resp.update(serializer.data)
        return Response(resp, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        self.serializer_class.Meta.extra_kwargs = {"username": {"required": False}}
        partial = kwargs.pop('partial', False)

        resp = self.check_status(request, 'user_updated')
        if not isinstance(resp, dict):
            return resp

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        resp.update(serializer.data)
        return Response(resp)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = RetrieveListUserSerializer
        return super(UsersViewSet, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.serializer_class = RetrieveListUserSerializer
        return super(UsersViewSet, self).list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def delete(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg not in kwargs:
            return self.bulk_destroy(request, *args, **kwargs)
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        preview_is_active = instance.is_active
        self.perform_destroy(instance)
        resp = {
            'user_id': instance.id,
            'username': instance.username,
            'status': self.DEACTIVATE_STATUSES[preview_is_active]
        }
        return Response(resp, status=status.HTTP_200_OK)

    def bulk_destroy(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if self.queryset_filter:
            preview_statuses = dict(queryset.values_list('id', 'is_active'))
            users = self.queryset_filter.get('pk__in', self.queryset_filter.get('username__in', []))
            mapping_fields = ('id', 'username') if 'pk__in' in self.queryset_filter else ('username', 'id')
            mapping = dict(queryset.values_list(*mapping_fields))

            queryset.update(is_active=False)

            resp = []
            for u in users:
                user_id = mapping_fields[0] == 'id' and u or mapping.get(u)
                username = mapping_fields[0] == 'username' and u or mapping.get(u, '')
                resp.append({
                    'user_id': user_id,
                    'username': username,
                    'status': self.DEACTIVATE_STATUSES[preview_statuses.get(user_id)]
                })
            return Response(resp, status=status.HTTP_200_OK)
        return Response({'detail': _('You cannot deactivate all users.')}, status=status.HTTP_400_BAD_REQUEST)


class UsersByUsernameViewSet(ByUsernameMixin, UsersViewSet):
    pass


class CoursesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CourseSerializer
    queryset = CourseOverview.objects.all()


class UserProgressViewSet(UserFilterMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserProgressSerializer
    filter_by_supervisor = True


class UserProgressByUsernameViewSet(ByUsernameMixin, UserProgressViewSet):
    pass
