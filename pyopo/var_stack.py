from typing import List, Tuple, Any


class stack:
    """The variable stack is a 2 variable Tuple LIFO stack

    The tuple is composed of the variable type code and variable value:


        0 - Int16 - Word
        1 - Int32 - Long
        2 - 64bit - Float
        3 - QStr
        4 - Addr

    Most (if not all) opcodes do not use the type information, as it is expected the compiler has already
    performed type checking. It is however used for debugging purposes to diagnose incorrect opcode inputs.
    """

    def __init__(self):
        self.stack_frame: List[Tuple[int, Any]] = []

    def pop(self) -> Any:
        """Pop the top variable value from the stack"""
        assert len(self.stack_frame) > 0

        return self.stack_frame.pop()[1]

    def pop_2(self) -> Tuple[Any, Any]:
        """Returns the values of the top two stack entries.

        Performs the same as pop(), pop() but requires reduced calls.

        This is optimal for graphics calls that require (x,y) or (w,h) params

        Due to LIFO of the stack, they are done in reverse order b -> a
        """
        assert len(self.stack_frame) > 1

        _, b = self.stack_frame.pop()
        _, a = self.stack_frame.pop()
        return (a, b)

    def pop_with_type(self) -> Tuple[int, Any]:
        """Pop the top variable value from the stack as well as its type code"""
        assert len(self.stack_frame) > 0

        return self.stack_frame.pop()

    def push(self, type: int, value: Any) -> None:
        """Push a value and its type code to the top of the stack"""
        assert value is not None
        assert type is not None
        assert type >= 0 and type <= 4

        self.stack_frame.append((type, value))

    def peek(self) -> Tuple[int, Any]:
        """Peek the top variable and its type code from the stack"""
        return self.stack_frame[-1]
