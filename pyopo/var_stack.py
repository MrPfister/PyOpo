from typing import Any


class stack:
    """The variable stack is a 2 variable tuple LIFO stack

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
        self.stack_frame: list[tuple[int, Any]] = []

    def pop(self) -> Any:
        """Pop the top variable value from the stack"""
        assert len(self.stack_frame) > 0

        return self.stack_frame.pop()[1]

    def pop_n(self, n: int) -> tuple[Any, ...]:
        """Pops the top n variable values from the stack"""
        assert n > 0
        assert len(self.stack_frame) >= n

        popped_vals = [self.stack_frame.pop()[1] for _ in range(n)]
        popped_vals.reverse()

        return (*popped_vals,)

    def pop_2(self) -> tuple[Any, Any]:
        """Returns the values of the top two stack entries.

        Performs the same as pop(), pop() but requires reduced calls.

        This is optimal for graphics calls that require (x,y) or (w,h) params

        Due to LIFO of the stack, they are done in reverse order b -> a

        Note: For n=2 this function is faster than pop_n(2)
        """
        assert len(self.stack_frame) > 0

        _, b = self.stack_frame.pop()
        _, a = self.stack_frame.pop()
        return (a, b)

    def pop_with_type(self) -> tuple[int, Any]:
        """Pop the top variable value from the stack as well as its type code"""
        assert len(self.stack_frame) > 0

        return self.stack_frame.pop()

    def push(self, type: int, value: Any) -> None:
        """Push a value and its type code to the top of the stack"""
        assert value is not None
        assert type is not None
        assert type >= 0 and type <= 4

        self.stack_frame.append((type, value))

    def peek(self) -> tuple[int, Any]:
        """Peek the top variable and its type code from the stack"""
        return self.stack_frame[-1]
