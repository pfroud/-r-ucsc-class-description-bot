"""
Vastly superior version of find_mentions which is faster can can see:
* multi-mentions: mentions of same department with list of numbers, e.g. "Math 21, 23b, 24 and 100"
* letter-list mentions: mentions of same number with list of letters, e.g. "CE 129A/B/C"
* letter-list mentions in a multi mention, e.g. "CS 4a, 37a/b, 15, 163w/x/y/z"
"""

import re

# from build_database.all_departments, with build_database.lit_department_codes.values() and "CS" and "CE"
pattern_depts = "acen|ams|anth|aplx|art|artg|astr|bioc|bme|ce|chem|chin|clei|clni|clte|cmmu|cmpe|cmpm|cmps|cowl|cres|" \
                "crwn|cs|danm|eart|econ|educ|ee|eeb|envs|film|fmst|fren|game|germ|gree|havc|hebr|his|hisc|ital|japn|" \
                "jwst|krsg|laad|lals|latn|lgst|ling|lit|ltcr|ltel|ltfr|ltge|ltgr|ltin|ltit|ltmo|ltpr|ltsp|ltwl|math|" \
                "mcdb|merr|metx|musc|oaks|ocea|phil|phye|phys|poli|port|prtr|psyc|punj|russ|scic|socd|socy|span|sphs|" \
                "stev|thea|tim|ucdc|writ|yidd"

# matches a letter-list mention: a mention of same number with list of letters, e.g. "CE 129A/B/C"
pattern_mention_letter_list = "(\d+(?:[A-Za-z] ?/ ?)+[A-Za-z])"

# matches a normal mention: a mention with a course number and one optional letter, e.g. "12" or "12a"
pattern_mention_normal = "(\d+[A-Za-z]?)"

# matches either a letter-list mention or a normal mention
pattern_mention_any = "(" + pattern_mention_letter_list + "|" + pattern_mention_normal + ")"

# matches a delimiter in a multi-mention, e.g. "Math 21, 23b, 24 and 100"
pattern_delimiter = "(?:[,/ &+]|or|and|with)*"

# matches a whole mention string - a department code then multiple course numbers and possibly multiple course letters.
# e.g. matches "CS 10, 15a, or 35a/b/c"
pattern_final = "(" + pattern_depts + ") ?(" + pattern_mention_any + pattern_delimiter + ")*" + pattern_mention_any


def parse_letter_list(dept, list_letter_mention):
    """Given a string of one course number a list of letters, returns a list with one letter per number.
    e.g. '129A/B/C' becomes ['129A', '129B', '129C']

    :param dept: the department the mention is in
    :type dept: str
    :param list_letter_mention: a string with one course number and a list of letters, e.g. '129A/B/C'
    :type list_letter_mention: str
    :return: a list of normal mentions, e.g. ['129A', '129B', '129C']
    :rtype: list
    """
    m = re.match(" ?(\d+) ?((?:[A-Za-z] ?/ ?)+[A-Za-z])", list_letter_mention)  # != pattern_mention_letter_list
    num = m.group(1)
    letters = m.group(2).split('/')

    return_list = []
    for l in letters:
        return_list.append(dept + " " + num + l.strip())

    return return_list


def parse_multi_mention(multi_mention):
    """Parses multi-mentions into normal mentions.

    :param multi_mention: a multi-mention, e.g. "Math 21, 23b, 24 and 100"
    :type multi_mention: str
    :return: normal mentions from the multi-mention
    :rtype: list
    """
    mentions = []

    # extract department code
    match_dept = re.match(pattern_depts, multi_mention, re.IGNORECASE)
    dept = multi_mention[match_dept.start():match_dept.end()].lower()
    if dept == 'cs':
        dept = 'cmps'
    if dept == 'ce':
        dept = 'cmpe'

    # the rest of the string, past department code
    rest = multi_mention[match_dept.end():]

    # look for letter-list mentions, like "129a/b/c"
    mentions_letter_list = re.findall(pattern_mention_letter_list, rest)
    for m in mentions_letter_list:
        mentions.extend(parse_letter_list(dept, m))

    # take out letter-list mentions, if any
    rest = re.sub(pattern_mention_letter_list, "", rest)

    # look for normal mentions, like "12" or "12a"
    men_normal = re.findall(pattern_mention_normal, rest)
    for m in men_normal:
        mentions.append(dept + ' ' + m)

    return mentions


def parse_string(str_):
    """Finds mentions in a string.
    Can see...
    * multi-mentions: mentions of same department with list of numbers, e.g. "Math 21, 23b, 24 and 100"
    * letter-list mentions: mentions of same number with list of letters, e.g. "CE 129A/B/C"
    * letter-list mentions in a multi mention, e.g. "CS 4a, 37a/b, 15, 163w/x/y/z"

    :param str_: string to find mentions in
    :type str_: string
    :return: list of strings of mentions
    :rtype: list
    """
    if not str_:
        return []

    mentions = []

    multi_mentions = re.findall(pattern_final, str_, re.IGNORECASE)
    for m in multi_mentions:
        mentions.extend(parse_multi_mention(m))

    return mentions


print(parse_string(
    "CS 11a, 16A/B/C, 14, and 129w/x/y/z? Someone told me I should take econ 114q/r, 1, 2 and lit 990"))
