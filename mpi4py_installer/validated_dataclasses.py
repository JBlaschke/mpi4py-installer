class ValidatedDataClass(type):

    def __new__(cls, name, bases, namespace):
        print(f"{cls=}, {name=}, {bases=}, {namespace=}")
        namespace['__post_init__'] = cls.post_init
        return type.__new__(cls, name, bases, namespace)


    def post_init(self):
        for (name, field_type) in self.__annotations__.items():
            if not isinstance(self.__dict__[name], field_type):
                current_type = type(self.__dict__[name])
                raise TypeError(
                    f"{name} is not a {field_type} (instead of {current_type})"
                )

