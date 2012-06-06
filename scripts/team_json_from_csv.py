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
    r.next()
    users = []
    for line in r:
        if not line[0]:
            continue

        u = {
            'username': line[0],
            'name': line[1],
            'role': line[2],
            'role_details': line[3],
            'description': line[4],
            'favorite_subreddits': line[5].split(' ') if line[5] else [],
            'new': tryconv(int, line[6]),
            'top': tryconv(float, line[7]),
            'beard': tryconv(int, line[8], 0),
            'pyro': tryconv(int, line[9], 0),
            'wpm': tryconv(int, line[10]),
        }
        if line[11]:
            u[line[12]] = tryconv(int, line[13], line[13])

        for k in u.keys():
            if u[k] is None:
                del u[k]

        users.append(u)

    return users

def main():
    users = read_csv(sys.argv[1])
    for u in users:
        print json.dumps(u, sort_keys=True) + ','

if __name__ == "__main__":
    main()
