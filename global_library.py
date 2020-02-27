def input_check(prompt, input_type_example, acceptance, type_error_message="The type of the value you inputted is wrong!", not_in_range_message="The value you inputted is not in the range!"):
    while True:
        response = input(prompt)
        input_type = type(input_type_example)
        try:
            input_type(response)
        except ValueError:
            print(type_error_message)
        else:
            try:
                acceptance
            except NameError:
                return response
            else:
                try:
                    acceptance
                except NameError:
                    return response
                else:
                    if _check_range(input_type(response), acceptance, not_in_range_message):
                        return response


def _check_range(response, acceptance, not_in_range_message):
    if response in acceptance:
        return True
    else:
        print(not_in_range_message)
        return False
