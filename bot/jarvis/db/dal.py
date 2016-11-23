import collections
import contextlib

from jarvis.db import connection


def in_context(fn):
    def decorated(*args, **kwargs):
        with contextlib.closing(connection.cursor()) as cur:
            ret = fn(cur, *args, **kwargs)
            connection.commit()
            return ret

    return decorated


class DalMetaclass(type):
    @classmethod
    def __prepare__(mcs, _name, _bases, **_kwargs):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, namespace, **_kwargs):
        for name, function in namespace.items():
            if isinstance(function, collections.Callable):
                namespace[name] = staticmethod(in_context(function))
        return type.__new__(mcs, name, bases, dict(namespace))


class Dal(object, metaclass=DalMetaclass):
    pass
