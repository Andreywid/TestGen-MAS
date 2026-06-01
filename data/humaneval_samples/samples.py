# A representative subset of HumanEval functions (public, MIT license).
# Source: https://github.com/openai/human-eval

SAMPLES: list[dict] = [
    # ── original 5 ────────────────────────────────────────────────────────────
    {
        "task_id": "HumanEval/0",
        "name": "has_close_elements",
        "source": """\
def has_close_elements(numbers: list, threshold: float) -> bool:
    \"\"\"Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    \"\"\"
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True
    return False
""",
    },
    {
        "task_id": "HumanEval/1",
        "name": "separate_paren_groups",
        "source": """\
def separate_paren_groups(paren_string: str) -> list:
    \"\"\"Input to this function is a string containing multiple groups of nested parentheses.
    Your goal is to separate those groups into separate strings and return the list of those.
    Separate groups are balanced (each open brace is properly closed) and not nested within
    each other. Ignore any spaces in the input string.
    >>> separate_paren_groups('( ) (( )) (( )( ))')
    ['()', '(())', '(()())']
    \"\"\"
    result = []
    current_string = []
    current_depth = 0
    for c in paren_string:
        if c == '(':
            current_depth += 1
            current_string.append(c)
        elif c == ')':
            current_depth -= 1
            current_string.append(c)
            if current_depth == 0:
                result.append(''.join(current_string))
                current_string = []
    return result
""",
    },
    {
        "task_id": "HumanEval/2",
        "name": "truncate_number",
        "source": """\
def truncate_number(number: float) -> float:
    \"\"\"Given a positive floating point number, it can be decomposed into
    and integer part (largest integer smaller or equal to given number) and
    decimals (leftover part always smaller than 1).
    Return the decimal part of the number.
    >>> truncate_number(3.5)
    0.5
    \"\"\"
    return number % 1.0
""",
    },
    {
        "task_id": "HumanEval/3",
        "name": "below_zero",
        "source": """\
def below_zero(operations: list) -> bool:
    \"\"\"You're given a list of deposit and withdrawal operations on a bank account that
    starts with zero balance. Your task is to detect if at some point the balance falls
    below zero, and at that point function should return True. Otherwise it should return False.
    >>> below_zero([1, 2, 3])
    False
    >>> below_zero([1, 2, -4, 5])
    True
    \"\"\"
    balance = 0
    for op in operations:
        balance += op
        if balance < 0:
            return True
    return False
""",
    },
    {
        "task_id": "HumanEval/4",
        "name": "mean_absolute_deviation",
        "source": """\
def mean_absolute_deviation(numbers: list) -> float:
    \"\"\"For a given list of input numbers, calculate Mean Absolute Deviation
    around the mean of this dataset.
    Mean Absolute Deviation is the average absolute difference between each
    element and a center point (mean in this case):
    MAD = average | x - x_mean |
    >>> mean_absolute_deviation([1.0, 2.0, 3.0, 4.0])
    1.0
    \"\"\"
    mean = sum(numbers) / len(numbers)
    return sum(abs(x - mean) for x in numbers) / len(numbers)
""",
    },
    # ── new functions (more complex) ───────────────────────────────────────────
    {
        "task_id": "HumanEval/36",
        "name": "fizz_buzz",
        "source": """\
def fizz_buzz(n: int) -> int:
    \"\"\"Return the number of times the digit 7 appears in integers less than n
    which are divisible by 11 or 13.
    >>> fizz_buzz(50)
    0
    >>> fizz_buzz(78)
    2
    >>> fizz_buzz(79)
    3
    \"\"\"
    ns = []
    for i in range(n):
        if i % 11 == 0 or i % 13 == 0:
            ns.append(i)
    s = ''.join(list(map(str, ns)))
    ans = 0
    for c in s:
        ans += (c == '7')
    return ans
""",
    },
    {
        "task_id": "HumanEval/72",
        "name": "will_it_fly",
        "source": """\
def will_it_fly(q, w):
    \"\"\"Write a function that returns True if the object q will fly, and False otherwise.
    The object can fly if it's balanced (it is a palindromic list) and the sum of its
    elements is less than or equal the maximum possible weight w.
    >>> will_it_fly([1, 2], 5)
    False
    >>> will_it_fly([3, 2, 3], 1)
    False
    >>> will_it_fly([3, 2, 3], 9)
    True
    >>> will_it_fly([3], 5)
    True
    \"\"\"
    if sum(q) > w:
        return False
    i, j = 0, len(q) - 1
    while i < j:
        if q[i] != q[j]:
            return False
        i += 1
        j -= 1
    return True
""",
    },
    {
        "task_id": "HumanEval/80",
        "name": "is_happy",
        "source": """\
def is_happy(s):
    \"\"\"You are given a string s.
    Your task is to check if the string is happy or not.
    A string is happy if its length is at least 3 and every 3 consecutive letters are distinct.
    >>> is_happy('a')
    False
    >>> is_happy('aa')
    False
    >>> is_happy('abcd')
    True
    >>> is_happy('aabb')
    False
    >>> is_happy('adb')
    True
    >>> is_happy('xyy')
    False
    \"\"\"
    if len(s) < 3:
        return False
    for i in range(len(s) - 2):
        if len(set(s[i:i+3])) < 3:
            return False
    return True
""",
    },
    {
        "task_id": "HumanEval/92",
        "name": "any_int",
        "source": """\
def any_int(x, y, z):
    \"\"\"Create a function that takes 3 numbers.
    Returns true if one of the numbers is equal to the sum of the other two,
    and all numbers are integers.
    Returns false in any other cases.
    >>> any_int(5, 2, 7)
    True
    >>> any_int(3, 2, 2)
    False
    >>> any_int(3, -2, 1)
    True
    >>> any_int(3.6, -2.2, 2)
    False
    \"\"\"
    if isinstance(x, int) and isinstance(y, int) and isinstance(z, int):
        if (x + y == z) or (x + z == y) or (y + z == x):
            return True
        return False
    return False
""",
    },
    {
        "task_id": "HumanEval/112",
        "name": "reverse_delete",
        "source": """\
def reverse_delete(s, c):
    \"\"\"Task: We are given two strings s and c, you have to delete all the characters
    in s that are equal to any character in c, then check if the result string is palindrome.
    A string is called palindrome if it reads the same backward as forward.
    You should return a tuple containing the result string and True/False for the check.
    >>> reverse_delete('abcde', 'ae')
    ('bcd', False)
    >>> reverse_delete('abcdef', 'b')
    ('acdef', False)
    >>> reverse_delete('abcdedcba', 'ab')
    ('cdedc', True)
    \"\"\"
    s = ''.join([char for char in s if char not in c])
    return (s, s[::-1] == s)
""",
    },
    {
        "task_id": "HumanEval/119",
        "name": "match_parens",
        "source": """\
def match_parens(lst):
    \"\"\"You are given a list of two strings, both consisting of open parentheses '('
    and close parentheses ')' characters.
    Your job is to check if it is possible to concatenate the two strings in some order,
    that the resulting string will be good.
    A string S is considered to be good if and only if all parentheses in S are balanced.
    For example: the string '(())()' is good, while the string '())' is not.
    Return 'Yes' if there's a way to make a good string, and return 'No' otherwise.
    >>> match_parens(['()(', ')'])
    'Yes'
    >>> match_parens([')', ')'])
    'No'
    \"\"\"
    def check(s):
        val = 0
        for i in s:
            if i == '(':
                val += 1
            else:
                val -= 1
            if val < 0:
                return False
        return val == 0

    s1 = lst[0] + lst[1]
    s2 = lst[1] + lst[0]
    return 'Yes' if check(s1) or check(s2) else 'No'
""",
    },
    {
        "task_id": "HumanEval/124",
        "name": "valid_date",
        "source": """\
def valid_date(date):
    \"\"\"You have to write a function which validates a given date string and
    returns True if the date is valid otherwise False.
    The date is valid if all of the following rules are satisfied:
    1. The date string is not empty.
    2. The number of days is not less than 1 or higher than 31 days for months 1,3,5,7,8,10,12.
       And the number of days is not less than 1 or higher than 30 days for months 4,6,9,11.
       And, the number of days is not less than 1 or higher than 29 for the month 2.
    3. The months should not be less than 1 or higher than 12.
    4. The date should be in the format: mm-dd-yyyy
    >>> valid_date('03-11-2000')
    True
    >>> valid_date('15-01-2012')
    False
    >>> valid_date('04-0-2040')
    False
    >>> valid_date('06-04-2020')
    True
    >>> valid_date('06/04/2020')
    False
    \"\"\"
    try:
        date = date.strip()
        month, day, year = date.split('-')
        month, day, year = int(month), int(day), int(year)
        if month < 1 or month > 12:
            return False
        if month in [1, 3, 5, 7, 8, 10, 12] and (day < 1 or day > 31):
            return False
        if month in [4, 6, 9, 11] and (day < 1 or day > 30):
            return False
        if month == 2 and (day < 1 or day > 29):
            return False
        return True
    except:
        return False
""",
    },
    {
        "task_id": "HumanEval/126",
        "name": "is_sorted",
        "source": """\
def is_sorted(lst):
    \"\"\"Given a list of numbers, return whether or not they are sorted in ascending order.
    If list has more than 1 duplicate of the same number, return False.
    Assume no negative numbers and only integers.
    >>> is_sorted([5])
    True
    >>> is_sorted([1, 2, 3, 4, 5])
    True
    >>> is_sorted([1, 3, 2, 4, 5])
    False
    >>> is_sorted([1, 2, 2, 3, 3, 4])
    True
    >>> is_sorted([1, 2, 2, 2, 3, 4])
    False
    \"\"\"
    count_digit = dict([(i, 0) for i in lst])
    for i in lst:
        count_digit[i] += 1
    if any(count_digit[i] > 2 for i in count_digit):
        return False
    if all(lst[i-1] <= lst[i] for i in range(1, len(lst))):
        return True
    else:
        return False
""",
    },
    {
        "task_id": "HumanEval/127",
        "name": "intersection",
        "source": """\
def intersection(interval1, interval2):
    \"\"\"You are given two intervals, where each interval is a pair of integers.
    For example, interval = (start, end) = (1, 2).
    The given intervals are closed which means that the interval (start, end)
    includes both start and end.
    For each given interval, it is assumed that its start is less than or equal its end.
    This function should output the length of its intersection. If the length of the
    intersection is a prime number, return 'YES', otherwise, return 'NO'.
    If the two intervals don't intersect, return 'NO'.
    >>> intersection((1, 2), (2, 3))
    'NO'
    >>> intersection((-1, 1), (0, 4))
    'NO'
    >>> intersection((-3, -1), (-5, 5))
    'YES'
    \"\"\"
    def is_prime(num):
        if num == 1 or num == 0:
            return False
        if num == 2:
            return True
        for i in range(2, num):
            if num % i == 0:
                return False
        return True

    l = max(interval1[0], interval2[0])
    r = min(interval1[1], interval2[1])
    length = r - l
    if length > 0 and is_prime(length):
        return "YES"
    return "NO"
""",
    },
    {
        "task_id": "HumanEval/140",
        "name": "fix_spaces",
        "source": """\
def fix_spaces(text):
    \"\"\"Given a string text, replace all spaces in it with underscores,
    and if a string has more than 2 consecutive spaces,
    then replace all consecutive spaces with -
    >>> fix_spaces('Example')
    'Example'
    >>> fix_spaces('Example 1')
    'Example_1'
    >>> fix_spaces(' Example 2')
    '_Example_2'
    >>> fix_spaces(' Example   3')
    '_Example-3'
    \"\"\"
    new_text = ""
    i = 0
    start, end = 0, 0
    while i < len(text):
        if text[i] == " ":
            end += 1
        else:
            if end - start > 2:
                new_text += "-" + text[i]
            elif end - start > 0:
                new_text += "_" * (end - start) + text[i]
            else:
                new_text += text[i]
            start, end = i + 1, i + 1
        i += 1
    if end - start > 2:
        new_text += "-"
    elif end - start > 0:
        new_text += "_" * (end - start)
    return new_text
""",
    },
]
