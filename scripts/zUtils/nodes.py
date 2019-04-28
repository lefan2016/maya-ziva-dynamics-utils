import inspect
from zBuilder import nodes


ZIVA_NODES = {
    obj().type: obj
    for name, obj in inspect.getmembers(nodes)
    if inspect.isclass(obj)
    if obj().type
}