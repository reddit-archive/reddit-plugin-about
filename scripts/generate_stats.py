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
from r2.lib.db.operators import asc, desc
from r2.lib.utils import timeago

def subreddit_stats(config, ranges):
    def get_id(*args, **kwargs):
        kwargs.setdefault('limit', 1)
        results = list(kind._query(*args, **kwargs))
        if not results:
            return None
        else:
            return results[0]._id

    sr_counts = defaultdict(int)
    for kind in (Link, Comment):
        thing_table, data_table = get_thing_table(kind._type_id)
        first_id = get_id(kind.c._date > ranges['yesterday'][0], sort=asc('_date'))
        last_id = get_id(kind.c._date < ranges['yesterday'][1], sort=desc('_date'))
        if not first_id or not last_id:
            continue

        q = sa.select([data_table.c.value, sa.func.count(data_table.c.value)],
                (data_table.c.thing_id > first_id)
                    & (data_table.c.thing_id < last_id)
                    & (data_table.c.key == 'sr_id')
                    & (thing_table.c.thing_id == data_table.c.thing_id)
                    & (thing_table.c.spam == False),
                group_by=data_table.c.value)

        for sr_id, count in q.execute():
            sr_counts[sr_id] += count

    return {'subreddits_active_yesterday': len(list(count for count in sr_counts.itervalues() if count > 5))}

def vote_stats(config, ranges):
    stats = {}

    link_votes = Vote.rel(Account, Link)
    comment_votes = Vote.rel(Account, Comment)

    for name, rel in (('link', link_votes), ('comment', comment_votes)):
        table = get_rel_table(rel._type_id)[0]
        q = table.count(
                (table.c.date > ranges['yesterday'][0])
                & (table.c.date < ranges['yesterday'][1]))
        stats[name+'_vote_count_yesterday'] = q.execute().fetchone()[0]

    stats['vote_count_yesterday'] = stats['link_vote_count_yesterday'] + stats['comment_vote_count_yesterday']
    return stats

def ga_stats(config, ranges):
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

    # get last month stats
    month_stats = analytics.data().ga().get(
        ids='ga:24573069',
        start_date=ranges['last_month'][0].strftime('%Y-%m-%d'),
        end_date=ranges['last_month'][1].strftime('%Y-%m-%d'),
        metrics='ga:visitors, ga:pageviews',
        dimensions='ga:country'
    ).execute()
    stats['country_count_last_month'] = month_stats['totalResults']
    stats['uniques_last_month'] = int(month_stats['totalsForAllResults']['ga:visitors'])
    stats['pageviews_last_month'] = int(month_stats['totalsForAllResults']['ga:pageviews'])

    # get yesterday's stats
    day_loggedin_stats = analytics.data().ga().get(
        ids='ga:24573069',
        start_date=ranges['yesterday'][0].strftime('%Y-%m-%d'),
        end_date=ranges['yesterday'][1].strftime('%Y-%m-%d'),
        metrics='ga:visitors',
        filters='ga:customVarValue3=@loggedin'
    ).execute()
    stats['redditors_visited_yesterday'] = int(day_loggedin_stats['totalsForAllResults']['ga:visitors'])
    return stats

def update_stats(config):
    today = datetime.date.today()
    yesterday_start = (today - datetime.timedelta(days=2))
    yesterday_end = (today - datetime.timedelta(days=1))
    last_month_end = (today.replace(day=1) - datetime.timedelta(days=1))
    last_month_start = last_month_end.replace(day=1)
    ranges = {
        'yesterday': (yesterday_start, yesterday_end),
        'last_month': (last_month_start, last_month_end),
    }

    stats = {}
    def run_stats(f):
        start_time = time.time()
        stats.update(f(config, ranges))
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
