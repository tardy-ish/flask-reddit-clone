import re


def salt_password(pwd):
    #for every 2 characters add a hash sign
    pwd_salt = ""
    for i in range(len(pwd)):
        pwd_salt += pwd[i]
        if i % 2:
            pwd_salt += "#"
    return pwd_salt
# print(salt_password("password1234"))

def uname_check(txt):
    uname_reg = re.compile(r"^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$")
    if uname_reg.match(txt):
        return False
    return True


def db_table(table_name):
    def leCount(args):
        return table_name.query.filter_by(**args)
    return leCount
