import sys
import time
import datetime
import httplib2
import ConfigParser
import sqlalchemy as sa
from collections import defaultdict
from pylons import g
from r2.models import Account, Link, Comment, Vote
from r2.lib.db.tdb_sql import get_thing_table, get_rel_table
from r2.lib.db.operators import asc
from r2.lib.utils import timeago

def subreddit_stats(config):
    sr_counts = defaultdict(int)
    for kind in (Link, Comment):
        thing_table, data_table = get_thing_table(kind._type_id)
        first_id = list(kind._query(kind.c._date > timeago('1 day'), sort=asc('_date'), limit=1))
        if not first_id:
            continue
        else:
            first_id = first_id[0]._id

        q = sa.select([data_table.c.value, sa.func.count(data_table.c.value)],
                (data_table.c.thing_id > first_id)
                    & (data_table.c.key == 'sr_id')
                    & (thing_table.c.thing_id == data_table.c.thing_id)
                    & (thing_table.c.spam == False),
                group_by=data_table.c.value)

        for sr_id, count in q.execute():
            sr_counts[sr_id] += count

    return {'subreddits_active_past_day': len(list(count for count in sr_counts.itervalues() if count > 5))}

def vote_stats(config):
    stats = {}

    link_votes = Vote.rel(Account, Link)
    comment_votes = Vote.rel(Account, Comment)

    for name, rel in (('link', link_votes), ('comment', comment_votes)):
        table = get_rel_table(rel._type_id)[0]
        q = table.count(table.c.date > timeago('1 day'))
        stats[name+'_vote_count_past_day'] = q.execute().fetchone()[0]

    stats['vote_count_past_day'] = stats['link_vote_count_past_day'] + stats['comment_vote_count_past_day']
    return stats

def ga_stats(config):
    stats = {}

    from apiclient.discovery import build
    from oauth2client.file import Storage
    from oauth2client.client import OAuth2WebServerFlow
    from oauth2client.tools import run, FLAGS

    storage = Storage(config.get('about_stats', 'ga_credentials_file'))
    credentials = storage.get()

    if credentials is None or credentials.invalid == True:
        flow = OAuth2WebServerFlow(
            client_id=config.get('about_stats', 'ga_client_id'),
            client_secret=config.get('about_stats', 'ga_client_secret'),
            scope='https://www.googleapis.com/auth/analytics.readonly',
            user_agent='reddit-stats/1.0')

        FLAGS.auth_local_webserver = False
        credentials = run(flow, storage)

    http = httplib2.Http()
    http = credentials.authorize(http)

    analytics = build("analytics", "v3", http=http)

    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    end_date = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    visitors = analytics.data().ga().get(
        ids='ga:24573069',
        start_date=start_date,
        end_date=end_date,
        metrics='ga:visitors',
        dimensions='ga:country',
        filters='ga:customVarValue3=@loggedin'
    ).execute()

    stats['country_count_yesterday'] = visitors['totalResults']
    stats['redditors_visited_yesterday'] = int(visitors['totalsForAllResults']['ga:visitors'])
    return stats

def update_stats(config):
    stats = {}
    def run_stats(f):
        start_time = time.time()
        stats.update(f(config))
        end_time = time.time()
        print >> sys.stderr, '%s took %0.2f seconds.' % (f.__name__, end_time - start_time)

    print >> sys.stderr, 'recalculating reddit stats...'
    run_stats(subreddit_stats)
    run_stats(vote_stats)
    run_stats(ga_stats)
    print >> sys.stderr, 'finished:', stats
    g.memcache.set('about_reddit_stats', stats)

def main(config_file):
    parser = ConfigParser.RawConfigParser()
    with open(config_file, "r") as cf:
        parser.readfp(cf)
    update_stats(parser)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, "USAGE: %s /path/to/config-file.ini" % sys.argv[0]
        sys.exit(1)

    main(sys.argv[1])
