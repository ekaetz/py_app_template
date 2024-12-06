class BorgMeta(type):
  """
  A metaclass is a class that defines class objects.
  This metaclass is used to convert a class into a Borg class.
  Borg classes have all of their instances share the same internal
  state dictionary.
  It ensurse that the created class's __init__ method is invoked only once
  when the first instance of that class is created, and that for any other
  instance it patches into the shared state.
  Usage: when creating a borg class, just include: 'metaclass = BorgMeta'
    in the class declaration's parenthesis. Ex. `class NewBorg(object, metaclass=BorgMeta)`
  """
  def __init__(cls, cls_name, parents, dct):
    type.__init__(cls, cls_name, parents, dct)

    # Do some monkey-wrenching.
    old_init = cls.__init__
    cls._borg_state = None

    def new_init(self, *args, **kwargs):
      if cls._borg_state is None:
        cls._borg_state = self.__dict__
        old_init(self, *args, **kwargs)
      else:
        self.__dict__ = cls._borg_state

    cls.__init__ = new_init
