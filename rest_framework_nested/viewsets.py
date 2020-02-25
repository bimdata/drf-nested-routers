import functools
import operator

from django.db.models import Q


class NestedViewSetMixin(object):
    def get_queryset(self):
        """
        Filter the `QuerySet` based on its parents as defined in the
        `serializer_class.parent_lookup_kwargs` or `viewset.parent_lookup_kwargs`
        """
        queryset = super(NestedViewSetMixin, self).get_queryset()

        parent_lookup_kwargs = getattr(self, 'parent_lookup_kwargs', None)

        if not parent_lookup_kwargs:
            serializer_class = self.get_serializer_class()
            parent_lookup_kwargs = getattr(serializer_class, 'parent_lookup_kwargs', None)

        if parent_lookup_kwargs:
            orm_kwargs_filters = {}
            orm_arg_filters = []
            for query_param, field_name in parent_lookup_kwargs.items():
                if isinstance(field_name, tuple):
                    q_fields = (Q(**{field: self.kwargs[query_param]}) for field in field_name)
                    arg_filter = functools.reduce(operator.or_, q_fields)
                    orm_arg_filters.append(arg_filter)
                else:
                    orm_kwargs_filters[field_name] = self.kwargs[query_param]
            return queryset.filter(*orm_arg_filters, **orm_kwargs_filters)
        return queryset
