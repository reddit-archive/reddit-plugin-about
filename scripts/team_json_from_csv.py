import sys
import csv
import json

def tryconv(conv, s, fallback=None):
    try:
        return conv(s)
    except ValueError:
        return fallback

def read_csv(path):
    r = csv.reader(open(path), delimiter=',', quotechar='"')
    r.next()
    users = []
    extra_sorts = []
    for line in r:
        if not line[0]:
            users.append(None)

        u = {
            'username': line[0],
            'name': line[1],
            'role': line[2],
            'role_details': line[3],
            'description': line[4].strip(),
            'favorite_subreddits': (line[5].strip().split(' ')
                                    if line[5] else []),
            'new': tryconv(int, line[6]),
            'top': tryconv(float, line[7]),
            'beard': tryconv(int, line[8], 0),
            'pyro': tryconv(int, line[9], 0),
            'wpm': tryconv(int, line[10]),
        }
        if line[11]:
            sort_value = tryconv(int, line[13], line[13])
            sort = {
                'id': line[12],
                'title': line[11],
                'dir': -1 if sort_value >= 0 else 1,
            }
            u[sort['id']] = sort_value
            extra_sorts.append(sort)

        for k in u.keys():
            if u[k] is None:
                del u[k]

        users.append(u)

    return users, extra_sorts


def main():
    users, extra_sorts = read_csv(sys.argv[1])
    for u in users:
        if u:
            print json.dumps(u, sort_keys=True) + ','
        else:
            print

    for s in extra_sorts:
        print json.dumps(s, sort_keys=True) + ','

if __name__ == "__main__":
    main()
