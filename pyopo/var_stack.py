class stack:
    # 0 - Int16 - Word
    # 1 - Int32 - Long
    # 2 - 64bit - Float
    # 3 - QStr
    # 4 - Addr

    def __init__(
        self
    ):

        self.stack_frame = []

    def pop(
        self
    ):

        assert len(self.stack_frame) > 0

        return self.stack_frame.pop()[1]
    

    def pop_2(
        self
    ):
        
        assert len(self.stack_frame) > 1

        b = self.stack_frame.pop()[1]
        a = self.stack_frame.pop()[1]
        return (a, b)
    

    def pop_with_type(
        self
    ):

        assert len(self.stack_frame) > 0

        return self.stack_frame.pop()

    def push(
        self,
        type,
        value
    ):
        
        assert value is not None
        assert type is not None
        assert type>=0 and type<=4

        self.stack_frame.append((type, value))

    def peek(
        self
    ):

        return self.stack_frame[-1]
