def input_check(prompt, input_type, acceptance):
    while True:
        response = input(prompt)
        if input_type == int:
            try:
                int(response)
            except ValueError:
                print("The type of the value you inputted is wrong:\n\tYou need to input the type " + input_type)
            else:
                try:
                    acceptance
                except NameError:
                    return response
                else:
                    if __check_range(int(response), acceptance):
                        return response


def __check_range(response, acceptance):
    if response in acceptance:
        return True
    else:
        temp = "["
        for item in acceptance:
            temp = temp + item + ","
        print("You have to enter in the range " + temp + "\b]")
        return False
