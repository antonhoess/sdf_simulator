import functools


class ArgumentValidationError(ValueError):
    """Raised when the type of an argument to a function is not what it should be."""

    def __init__(self, arg_num, func_name, accepted_arg_type):
        self.error = 'The {0} argument of {1}() is not a {2}'.format(arg_num, func_name, accepted_arg_type)
    # end def

    def __str__(self):
        return self.error
    # end def
# end class


class InvalidArgumentNumberError(ValueError):
    """Raised when the number of arguments supplied to a function is incorrect.
    Note that this check is only performed from the number of arguments
    specified in the validate_accept() decorator. If the validate_accept()
    call is incorrect, it is possible to have a valid function where this
    will report a false validation."""

    def __init__(self, func_name):
        self.error = 'Invalid number of arguments for {0}()'.format(func_name)
    # end def

    def __str__(self):
        return self.error
    # end def
# end class


class InvalidReturnType(ValueError):
    """As the name implies, the return value is the wrong type."""

    def __init__(self, return_type, func_name):
        self.error = 'Invalid return type {0} for {1}()'.format(return_type, func_name)
    # end def

    def __str__(self):
        return self.error
    # end def
# end def


def ordinal(num):
    """Returns the ordinal number of a given integer, as a string.
    E.g. 1 -> 1st, 2 -> 2nd, 3 -> 3rd, etc."""
    if 10 <= num % 100 < 20:
        return '{0}th'.format(num)
    else:
        ord = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')

        return '{0}{1}'.format(num, ord)
    # end if
# end def


def accepts(*accepted_arg_types):
    """A decorator to validate the parameter types of a given function.
    It is passed a tuple of types. eg. (<type 'tuple'>, <type 'int'>)
function_args
    Note: It doesn't do a deep check, for example checking through a
          tuple of types. The argument passed must only be types."""

    def accept_decorator(validate_function):
        # Check if the number of arguments to the validator
        # function is the same as the arguments provided
        # to the actual function to validate. We don't need
        # to check if the function to validate has the right
        # amount of arguments, as Python will do this
        # automatically (also with a TypeError).
        @functools.wraps(validate_function)
        def decorator_wrapper(*function_args, **function_args_dict):
            # Since there is no known way to find out, if the first parameter is "self" of a calling class,
            # we just can check the length
            if len(function_args) == len(accepted_arg_types) + 1:
                function_args_tmp = function_args[1:]
            else:
                function_args_tmp = function_args

            if len(accepted_arg_types) is not len(accepted_arg_types):
                raise InvalidArgumentNumberError(validate_function.__name__)

            # We're using enumerate to get the index, so we can pass the
            # argument number with the incorrect type to ArgumentValidationError.
            for arg_num, (actual_arg, accepted_arg_type) in enumerate(zip(function_args_tmp, accepted_arg_types)):
                error = False
                if actual_arg is None:
                    pass
                elif accepted_arg_type is callable:
                    if not callable(actual_arg):
                        error = True
                    # end if
                elif not type(actual_arg) is accepted_arg_type:
                    if not issubclass(type(actual_arg), accepted_arg_type):
                        error = True
                # end if

                if error:
                    ord_num = ordinal(arg_num + 1)
                    raise ArgumentValidationError(ord_num, validate_function.__name__, accepted_arg_type)
                # end if

            return validate_function(*function_args, **function_args_dict)
        # end def

        return decorator_wrapper
    # end def

    return accept_decorator
# end def


def returns(*accepted_return_type_tuple):
    """
    Validates the return type. Since there's only ever one
    return type, this makes life simpler. Along with the
    accepts() decorator, this also only does a check for
    the top argument. For example you couldn't check
    (<type 'tuple'>, <type 'int'>, <type 'str'>).
    In that case you could only check if it was a tuple.
    """

    def return_decorator(validate_function):
        # No return type has been specified.
        if len(accepted_return_type_tuple) == 0:
            raise TypeError('You must specify a return type.')

        @functools.wraps(validate_function)
        def decorator_wrapper(*function_args):
            # More than one return type has been specified.
            if len(accepted_return_type_tuple) > 1:
                raise TypeError('You must specify one return type.')

            # Since the decorator receives a tuple of arguments
            # and the is only ever one object returned, we'll just
            # grab the first parameter.
            accepted_return_type = accepted_return_type_tuple[0]

            # We'll execute the function, and
            # take a look at the return type.
            return_value = validate_function(*function_args)
            return_value_type = type(return_value)

            if return_value_type is not accepted_return_type and not issubclass(return_value_type, accepted_return_type):
                raise InvalidReturnType(return_value_type, validate_function.__name__)

            return return_value
        # end def

        return decorator_wrapper
    # end def

    return return_decorator
# end def
