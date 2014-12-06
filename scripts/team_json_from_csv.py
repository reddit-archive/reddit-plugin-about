import sys
import csv
import json

def tryconv(conv, s, fallback=None):
    try:
        return conv(s)
    except ValueError:
        return fallback

def read_csv(path):
    with open(path) as f:
        r = csv.DictReader(f, delimiter=',', quotechar='"')
        users = []
        alums = []
        extra_sorts = []
        for fields in r:
            fields = {k: v.strip() for k, v in fields.iteritems()}

            if not fields['username']:
                continue

            u = {
                'username': fields['username'],
                'name': fields['name'],
                'role': fields['silly role'],
                'role_details': fields['sillier role'],
                'description': fields['description'],
                'favorite_subreddits': fields['favorite subreddits'].split(),
                'new': tryconv(int, fields['new']),
                'top': tryconv(float, fields['top']),
                'pyro': tryconv(int, fields['pyro'], 0),
                'wpm': tryconv(int, fields['wpm']),
            }
            if fields['extra sort title']:
                sort_value = tryconv(int, fields['extra sort value'], fields['extra sort value'])
                sort = {
                    'id': fields['extra sort id'],
                    'title': fields['extra sort title'],
                    'dir': -1 if sort_value >= 0 else 1,
                }
                u[sort['id']] = sort_value
                extra_sorts.append(sort)

            for k in u.keys():
                if u[k] is None:
                    del u[k]

            if fields['alum']:
                alums.append(u)
            else:
                users.append(u)

    extra_sorts.sort(key=lambda s: s['id'])
    users.sort(key=lambda s: s['username'])
    alums.sort(key=lambda s: s['username'])
    return users, alums, extra_sorts


def main():
    if len(sys.argv) != 3:
        print 'usage: team_json_from_csv.py CSV_FILE JSON_FILE'
        sys.exit(1)

    with open(sys.argv[2], 'r') as team_file:
        team_data = json.load(team_file)

    users, alums, extra_sorts = read_csv(sys.argv[1])

    team_data['team'] = users
    team_data['alumni'] = alums
    team_data['extra_sorts'] = extra_sorts

    print json.dumps(
        team_data,
        sort_keys=True,
        indent=4,
        separators=(',', ': '),  # remove pretty print trailing whitespace
    )

if __name__ == "__main__":
    main()
