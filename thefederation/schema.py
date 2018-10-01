import datetime

import graphene
from django.db.models import Subquery, OuterRef, Count, Max, IntegerField, F, Sum, Avg, FloatField
from django.db.models.functions import Cast
from django.utils.timezone import now
from graphene_django import DjangoObjectType

from thefederation.models import Node, Platform, Protocol, Stat, Service


class DateCountType(graphene.ObjectType):
    date = graphene.Date()
    count = graphene.Int()

    def resolve_count(self, info):
        return self.get('count')

    def resolve_date(self, info):
        return self.get('date')


class DateFloatCountType(graphene.ObjectType):
    date = graphene.Date()
    count = graphene.Float()

    def resolve_count(self, info):
        return self.get('count')

    def resolve_date(self, info):
        return self.get('date')


class NodeType(DjangoObjectType):
    country_code = graphene.String()
    country_flag = graphene.String()
    country_name = graphene.String()

    class Meta:
        model = Node

    def resolve_country_code(self, info):
        return self.country.code

    def resolve_country_flag(self, info):
        return self.country.unicode_flag

    def resolve_country_name(self, info):
        return self.country.name


class PlatformType(DjangoObjectType):
    class Meta:
        model = Platform


class ProtocolType(DjangoObjectType):
    class Meta:
        model = Protocol


class ServiceType(DjangoObjectType):
    class Meta:
        model = Service


class StatType(DjangoObjectType):
    class Meta:
        model = Stat


class Query:
    nodes = graphene.List(
        NodeType,
        host=graphene.String(),
        platform=graphene.String(),
        protocol=graphene.String(),
    )
    platforms = graphene.List(
        PlatformType,
        name=graphene.String(),
    )
    protocols = graphene.List(
        ProtocolType,
        name=graphene.String(),
    )
    services = graphene.List(
        ServiceType,
        name=graphene.String(),
    )
    stats = graphene.List(StatType)
    stats_counts_nodes = graphene.List(
        DateCountType,
        value=graphene.String(),
        itemType=graphene.String(),
    )
    stats_global_today = graphene.Field(
        StatType,
        platform=graphene.String(),
        protocol=graphene.String(),
    )
    stats_nodes = graphene.List(
        StatType,
        host=graphene.String(),
        itemType=graphene.String(),
        platform=graphene.String(),
        protocol=graphene.String(),
        value=graphene.String(),
    )
    stats_platform_today = graphene.Field(
        StatType,
        name=graphene.String(),
    )
    stats_protocol_today = graphene.Field(
        StatType,
        name=graphene.String(),
    )
    stats_users_active_ratio = graphene.List(
        DateFloatCountType,
        itemType=graphene.String(),
        value=graphene.String(),
    )
    stats_users_half_year = graphene.List(
        DateCountType,
        itemType=graphene.String(),
        value=graphene.String(),
    )
    stats_users_monthly = graphene.List(
        DateCountType,
        itemType=graphene.String(),
        value=graphene.String(),
    )
    stats_users_per_node = graphene.List(
        DateCountType,
        itemType=graphene.String(),
        value=graphene.String(),
    )
    stats_users_total = graphene.List(
        DateCountType,
        itemType=graphene.String(),
        value=graphene.String(),
    )
    stats_users_weekly = graphene.List(
        DateCountType,
        itemType=graphene.String(),
        value=graphene.String(),
    )
    stats_local_posts = graphene.List(
        DateCountType,
        itemType=graphene.String(),
        value=graphene.String(),
    )

    stats_local_comments = graphene.List(
        DateCountType,
        itemType=graphene.String(),
        value=graphene.String(),
    )

    @staticmethod
    def _get_stat_date_counts(stat, value=None, item_type=None):
        if value and item_type:
            if item_type == 'platform':
                qs = Stat.objects.filter(node__platform__name=value)
            elif item_type == 'protocol':
                qs = Stat.objects.filter(node__protocols__name=value)
            elif item_type == 'node':
                qs = Stat.objects.filter(node__host=value)
            else:
                raise ValueError('itemType should be "platform", "node" or "protocol')
        else:
            qs = Stat.objects.filter(node__isnull=False)

        return qs.values('date').annotate(
            count=Sum(stat)
        ).values('date', 'count').order_by('date')

    def resolve_nodes(self, info, **kwargs):
        if kwargs.get('platform'):
            qs = Node.objects.active().filter(platform__name=kwargs.get('platform'))
        elif kwargs.get('protocol'):
            qs = Node.objects.active().filter(protocols__name=kwargs.get('protocol'))
        else:
            qs = Node.objects.active()

        if kwargs.get('host'):
            qs = qs.filter(host=kwargs.get('host'))

        stat = Stat.objects.filter(
            node=OuterRef('pk'), date=now().date()
        ).values('users_monthly').annotate(users=Max('users_monthly')).values('users')

        return qs.active().annotate(
            users=Subquery(stat, output_field=IntegerField())
        ).order_by(
            F('users').desc(nulls_last=True)
        ).select_related('platform').prefetch_related('services')

    def resolve_platforms(self, info, **kwargs):
        if kwargs.get('name'):
            qs = Platform.objects.filter(name=kwargs.get('name').lower())
        else:
            qs = Platform.objects.all()

        nodes = Node.objects.active().filter(
            platform=OuterRef('pk')).values('platform').annotate(c=Count('*')).values('c')
        return qs.prefetch_related('nodes').annotate(
            active_nodes=Subquery(nodes, output_field=IntegerField())
        ).filter(active_nodes__gt=0).order_by('-active_nodes')

    def resolve_protocols(self, info, **kwargs):
        if kwargs.get('name'):
            qs = Protocol.objects.filter(name=kwargs.get('name').lower())
        else:
            qs = Protocol.objects.all()

        nodes = Node.objects.active().filter(
            protocols=OuterRef('pk')).values('protocols').annotate(c=Count('*')).values('c')
        return qs.prefetch_related('nodes').annotate(
            active_nodes=Subquery(nodes, output_field=IntegerField())
        ).filter(active_nodes__gt=0).order_by('-active_nodes')

    def resolve_stats(self, info, **kwargs):
        return Stat.objects.all()

    def resolve_stats_counts_nodes(self, info, **kwargs):
        return Stat.objects.node_counts(
            from_date=now() - datetime.timedelta(days=30),
            item_type=kwargs.get('itemType'),
            value=kwargs.get('value'),
        ).order_by('-date')

    def resolve_stats_global_today(self, info, **kwargs):
        return Stat.objects.for_days(platform=kwargs.get('platform'), protocol=kwargs.get('protocol')).first()

    def resolve_stats_nodes(self, info, **kwargs):
        if kwargs.get('itemType'):
            item_type = kwargs.get('itemType')
            value = kwargs.get('value')
        elif kwargs.get('platform'):
            item_type = 'platform'
            value = kwargs.get('platform')
        elif kwargs.get('protocol'):
            item_type = 'protocol'
            value = kwargs.get('protocol')
        else:
            item_type = None
            value = None

        if item_type == 'platform':
            qs = Stat.objects.filter(node__platform__name=value)
        elif item_type == 'protocol':
            qs = Stat.objects.filter(node__protocols__name=value)
        else:
            qs = Stat.objects.all()

        if kwargs.get('host'):
            qs = qs.filter(node__host=kwargs.get('host'))

        return qs.filter(date=now().date(), node__isnull=False, protocol__isnull=True, platform__isnull=True)

    def resolve_stats_platform_today(self, info, **kwargs):
        name = kwargs.get('name')
        if not name:
            return Stat.objects.none()

        return Stat.objects.filter(
            node__isnull=True, protocol__isnull=True, platform__name=name, date=now().date(),
        ).first()

    def resolve_stats_protocol_today(self, info, **kwargs):
        name = kwargs.get('name')
        if not name:
            return Stat.objects.none()

        return Stat.objects.filter(
            node__isnull=True, platform__isnull=True, protocol__name=name, date=now().date(),
        ).first()

    def resolve_stats_users_active_ratio(self, info, **kwargs):
        if kwargs.get('value') and kwargs.get('itemType'):
            if kwargs.get('itemType') == 'platform':
                qs = Stat.objects.filter(node__platform__name=kwargs.get('value'))
            elif kwargs.get('itemType') == 'protocol':
                qs = Stat.objects.filter(node__protocols__name=kwargs.get('value'))
            elif kwargs.get('itemType') == 'node':
                qs = Stat.objects.filter(node__host=kwargs.get('value'))
            else:
                raise ValueError('itemType should be "platform", "node" or "protocol')
        else:
            qs = Stat.objects.filter(node__isnull=False)
        return qs.values('date').annotate(
            count=Cast(Sum('users_monthly'), FloatField()) / Cast(Sum('users_total'), FloatField()),
        ).values('date', 'count').order_by('date')

    def resolve_stats_users_total(self, info, **kwargs):
        return Query._get_stat_date_counts('users_total', value=kwargs.get('value'), item_type=kwargs.get('itemType'))

    def resolve_stats_users_half_year(self, info, **kwargs):
        return Query._get_stat_date_counts(
            'users_half_year', value=kwargs.get('value'), item_type=kwargs.get('itemType')
        )

    def resolve_stats_users_monthly(self, info, **kwargs):
        return Query._get_stat_date_counts(
            'users_monthly', value=kwargs.get('value'), item_type=kwargs.get('itemType')
        )

    def resolve_stats_users_per_node(self, info, **kwargs):
        if kwargs.get('value') and kwargs.get('itemType'):
            if kwargs.get('itemType') == 'platform':
                qs = Stat.objects.filter(node__platform__name=kwargs.get('value'))
            elif kwargs.get('itemType') == 'protocol':
                qs = Stat.objects.filter(node__protocols__name=kwargs.get('value'))
            elif kwargs.get('itemType') == 'node':
                qs = Stat.objects.filter(node__host=kwargs.get('value'))
            else:
                raise ValueError('itemType should be "platform", "node" or "protocol')
        else:
            qs = Stat.objects.filter(node__isnull=False)
        return qs.values('date').annotate(
            count=Avg('users_total')
        ).values('date', 'count').order_by('date')

    def resolve_stats_users_weekly(self, info, **kwargs):
        return Query._get_stat_date_counts('users_weekly', value=kwargs.get('value'), item_type=kwargs.get('itemType'))

    def resolve_stats_local_posts(self, info, **kwargs):
        return Query._get_stat_date_counts('local_posts', value=kwargs.get('value'), item_type=kwargs.get('itemType'))

    def resolve_stats_local_comments(self, info, **kwargs):
        return Query._get_stat_date_counts(
            'local_comments', value=kwargs.get('value'), item_type=kwargs.get('itemType')
        )
