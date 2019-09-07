class PostcardState:
    class __PostcardServerState:
        def __init__(self):
            self.current = 'C1145_1'
        def __str__(self):
            return repr(self) + self.current

    instance = None

    def __init__(self):
        if not PostcardState.instance:
            PostcardState.instance = PostcardState.__PostcardServerState()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)
