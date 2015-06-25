# -*-coding:utf-8-*-

__all__ = ["stringify"]


def stringify(default_dict):
    """ make an object can be serialized by JSON. """
    result = dict()
    for k1, vs1 in default_dict.iteritems():
        if isinstance(vs1, (list, set)):
            vs1 = map(str, vs1)
        else:
            vs1 = str(vs1)
        result[str(k1)] = vs1
    return result