class Normalization:
    """Additional functions to extract or normalize data"""

    @staticmethod
    def get_digits(string):
        """
        Function that removes chars or punctuation and returns only digits as a string
        If gets None value returns None.

        :param string: Any string with numbers, chars or punctuation 
        :return: Digits from incoming string as a string or None
        """
        if string is not None:
            result = ''.join([number for number in string if number.isdigit()])
        else:
            result = None
        return result
