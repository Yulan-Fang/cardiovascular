# This file was automatically generated by SWIG (http://www.swig.org).
# Version 4.0.1
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info < (2, 7, 0):
    raise RuntimeError("Python 2.7 or later required")

# Import the low-level C/C++ module
if __package__ or "." in __name__:
    from . import _shape
else:
    import _shape

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_instance_variable(set):
    def set_instance_attr(self, name, value):
        if name == "thisown":
            self.this.own(value)
        elif name == "this":
            set(self, name, value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name), property):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add instance attributes to %s" % self)
    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):
    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError("You cannot add class attributes to %s" % cls)
    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""
    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)


class SwigPyIterator(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    __swig_destroy__ = _shape.delete_SwigPyIterator

    def value(self):
        return _shape.SwigPyIterator_value(self)

    def incr(self, n=1):
        return _shape.SwigPyIterator_incr(self, n)

    def decr(self, n=1):
        return _shape.SwigPyIterator_decr(self, n)

    def distance(self, x):
        return _shape.SwigPyIterator_distance(self, x)

    def equal(self, x):
        return _shape.SwigPyIterator_equal(self, x)

    def copy(self):
        return _shape.SwigPyIterator_copy(self)

    def next(self):
        return _shape.SwigPyIterator_next(self)

    def __next__(self):
        return _shape.SwigPyIterator___next__(self)

    def previous(self):
        return _shape.SwigPyIterator_previous(self)

    def advance(self, n):
        return _shape.SwigPyIterator_advance(self, n)

    def __eq__(self, x):
        return _shape.SwigPyIterator___eq__(self, x)

    def __ne__(self, x):
        return _shape.SwigPyIterator___ne__(self, x)

    def __iadd__(self, n):
        return _shape.SwigPyIterator___iadd__(self, n)

    def __isub__(self, n):
        return _shape.SwigPyIterator___isub__(self, n)

    def __add__(self, n):
        return _shape.SwigPyIterator___add__(self, n)

    def __sub__(self, *args):
        return _shape.SwigPyIterator___sub__(self, *args)
    def __iter__(self):
        return self

# Register SwigPyIterator in _shape:
_shape.SwigPyIterator_swigregister(SwigPyIterator)

class DoubleVector(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr

    def iterator(self):
        return _shape.DoubleVector_iterator(self)
    def __iter__(self):
        return self.iterator()

    def __nonzero__(self):
        return _shape.DoubleVector___nonzero__(self)

    def __bool__(self):
        return _shape.DoubleVector___bool__(self)

    def __len__(self):
        return _shape.DoubleVector___len__(self)

    def __getslice__(self, i, j):
        return _shape.DoubleVector___getslice__(self, i, j)

    def __setslice__(self, *args):
        return _shape.DoubleVector___setslice__(self, *args)

    def __delslice__(self, i, j):
        return _shape.DoubleVector___delslice__(self, i, j)

    def __delitem__(self, *args):
        return _shape.DoubleVector___delitem__(self, *args)

    def __getitem__(self, *args):
        return _shape.DoubleVector___getitem__(self, *args)

    def __setitem__(self, *args):
        return _shape.DoubleVector___setitem__(self, *args)

    def pop(self):
        return _shape.DoubleVector_pop(self)

    def append(self, x):
        return _shape.DoubleVector_append(self, x)

    def empty(self):
        return _shape.DoubleVector_empty(self)

    def size(self):
        return _shape.DoubleVector_size(self)

    def swap(self, v):
        return _shape.DoubleVector_swap(self, v)

    def begin(self):
        return _shape.DoubleVector_begin(self)

    def end(self):
        return _shape.DoubleVector_end(self)

    def rbegin(self):
        return _shape.DoubleVector_rbegin(self)

    def rend(self):
        return _shape.DoubleVector_rend(self)

    def clear(self):
        return _shape.DoubleVector_clear(self)

    def get_allocator(self):
        return _shape.DoubleVector_get_allocator(self)

    def pop_back(self):
        return _shape.DoubleVector_pop_back(self)

    def erase(self, *args):
        return _shape.DoubleVector_erase(self, *args)

    def __init__(self, *args):
        _shape.DoubleVector_swiginit(self, _shape.new_DoubleVector(*args))

    def push_back(self, x):
        return _shape.DoubleVector_push_back(self, x)

    def front(self):
        return _shape.DoubleVector_front(self)

    def back(self):
        return _shape.DoubleVector_back(self)

    def assign(self, n, x):
        return _shape.DoubleVector_assign(self, n, x)

    def resize(self, *args):
        return _shape.DoubleVector_resize(self, *args)

    def insert(self, *args):
        return _shape.DoubleVector_insert(self, *args)

    def reserve(self, n):
        return _shape.DoubleVector_reserve(self, n)

    def capacity(self):
        return _shape.DoubleVector_capacity(self)
    __swig_destroy__ = _shape.delete_DoubleVector

# Register DoubleVector in _shape:
_shape.DoubleVector_swigregister(DoubleVector)

class Shape(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    nshapes = property(_shape.Shape_nshapes_get, _shape.Shape_nshapes_set)
    __swig_destroy__ = _shape.delete_Shape

    def Move(self, dx, dy):
        return _shape.Shape_Move(self, dx, dy)

    def Area(self):
        return _shape.Shape_Area(self)

    def Perimeter(self):
        return _shape.Shape_Perimeter(self)

    def GetList(self):
        return _shape.Shape_GetList(self)
    x = property(_shape.Shape_x_get, _shape.Shape_x_set)
    y = property(_shape.Shape_y_get, _shape.Shape_y_set)

# Register Shape in _shape:
_shape.Shape_swigregister(Shape)
cvar = _shape.cvar

class Circle(Shape):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr

    def __init__(self, r):
        _shape.Circle_swiginit(self, _shape.new_Circle(r))

    def Area(self):
        return _shape.Circle_Area(self)

    def Perimeter(self):
        return _shape.Circle_Perimeter(self)

    def GetList(self):
        return _shape.Circle_GetList(self)
    __swig_destroy__ = _shape.delete_Circle

# Register Circle in _shape:
_shape.Circle_swigregister(Circle)

class Square(Shape):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr

    def __init__(self, w):
        _shape.Square_swiginit(self, _shape.new_Square(w))

    def Area(self):
        return _shape.Square_Area(self)

    def Perimeter(self):
        return _shape.Square_Perimeter(self)

    def GetList(self):
        return _shape.Square_GetList(self)
    __swig_destroy__ = _shape.delete_Square

# Register Square in _shape:
_shape.Square_swigregister(Square)



