class DecoratorBase:
    _wihtout_instance = set()

    def __init__(self, fn):
        self.fn = fn

    def __set_name__(self, owner, name):
        # TODO check first is a class
        assert name != "__init__", "Cannot add callback to __init__ method"

        # Do the default __set_name__ action
        setattr(owner, name, self.fn)

        if not hasattr(owner, "__original_init__"):

            def new_init(*args, **kwargs):
                print("Custom init running")
                DecoratorBase._wihtout_instance.remove(owner)
                owner.__original_init__(*args, **kwargs)

            setattr(owner, "__original_init__", owner.__init__)
            setattr(owner, "__init__", new_init)

            DecoratorBase._wihtout_instance.add(owner)

    @staticmethod
    def _init_ones_without_instance():
        for cls in list(DecoratorBase._wihtout_instance):
            cls()


if __name__ == "__main__":

    class Class:
        def __init__(self):
            print("Class")

        @DecoratorBase
        def test(self):
            print("test")

    # b = Class()
    # b.test()
    DecoratorBase._init_ones_without_instance()
