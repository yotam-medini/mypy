#!/usr/bin/env python3
# Author:  Yotam Medini  yotam.medini@gmail.com

import argparse
import configparser
import jira
import os
import pprint
import sys

def ew(msg):
    sys.stderr.write('%s\n' % msg)

def ow(msg):
    sys.stdout.write('%s\n' % msg)

class QJira:

    def __init__(self, args):
        self.rc = 0
        self.args = args
        
    def run(self):
        self.init_server()
        if self.rc == 0:
            if self.args.command == "list":
                self.list_issues()
            elif self.args.command == "issues":
                self.query_issues()
        return self.rc

    def init_server(self):
        args = self.args
        self.user = args.user
        self.apikey = args.apikey
        self.server = args.server
        if None in [self.user, self.apikey, self.server]:
            self.load_cfg()
        if None in [self.user, self.apikey, self.server]:
            ew(f"Some essential value(s) missing\n u={self.user} "
               f"server={self.server}, "
               f"apikey={len(self.apikey) if self.apikey else -1}")
            self.rc = 1
        if self.rc == 0:
           self.jira_server = jira.JIRA(
               basic_auth=(self.user, self.apikey),
               options={'server': self.server})

    def load_cfg(self):
        fn = '%s/.qjira' % os.getenv('HOME')
        if os.path.isfile(fn):
            config = configparser.ConfigParser()
            config.read(fn)
            if 'DEFAULT' in config.keys():
                sect = config['DEFAULT']
                self.user = self.user or sect.get('user')
                self.server = self.server or sect.get('server')
                self.apikey = self.apikey or sect.get('apikey')
        else:
            ew('No %s configuration' % fn)

    def list_issues(self):
        owner = self.args.owner or self.user
        jql = f'assignee = "{owner}"'
        if self.args.status is not None:
            statuses = self.comma_sep_to_comma_sep_dquoted(self.args.status)
            jql += f" AND status IN ({statuses})"
        if self.args.xstatus is not None:
            statuses = self.comma_sep_to_comma_sep_dquoted(self.args.xstatus)
            jql += f" AND status NOT IN ({statuses})"
        ew(f"jql={jql}")
        issues = self.jira_server.search_issues(jql, maxResults=20)
        ow(f"#(issues)={len(issues)}")
        self.print_issues(issues)

    def query_issues(self):
        if self.args.keys is None:
            ew("Missing keys")
            self.rc = 1
        else:
            dquoted_keys = self.comma_sep_to_comma_sep_dquoted(self.args.keys)
            jql = f"key in ({dquoted_keys})"
            ew(f"jql= {jql}")
            issues = self.jira_server.search_issues(jql, maxResults=20)
            self.print_issues(issues)

    def search_issues(self):
        jql = None
        if self.args.compronent is not None:
            pass
            
    def jql_and_conditon(jql, cond):
        if jql is None:
            jql = cond
        else:
            jql = f"{jql} AND {cond}"
        return jql

    def print_issues(self, issues):
        keys2issues = {}
        keys = []
        for issue in issues:
            key = issue.key
            keys2issues[key] = issue
            keys.append(key)
        keys.sort()
        for key in keys:
            issue = keys2issues[key]
            # ow(f"{issue}, dir={dir(issue)}")
            # ow(self.issue_str(issue))
            ow(self.issue_str(issue))
            for subtask in issue.fields.subtasks:
                ow("  " + self.issue_str(subtask))

    def issue_str(self, issue):
        fields = issue.fields
        type_name = f"[{fields.issuetype.name}]" if self.args.showtype else ""
        status = f" ({fields.status.name})" if self.args.showstatus else ""
        priority = (f" ({fields.priority.name})" if self.args.showpriority
                    else "")
        return f"{issue.key}{type_name}:{status}{priority} {fields.summary}"

    def comma_sep_to_comma_sep_dquoted(self, s):
        elements = s.split(',')
        dquoted_elements = ','.join(map(lambda s: f'"{s}"', elements))
        return dquoted_elements

def main(argv):
    rc = 0
    parser = argparse.ArgumentParser("qjira", "Query Jira")
    parser.add_argument("-u", "--user", help="extacted from ~/.qjira")
    parser.add_argument("--apikey", help="extacted from ~/.qjira")
    parser.add_argument("--server", help="extacted from ~/.qjira")
    parser.add_argument("--owner", help="default: as user")
    parser.add_argument('-c', '--command', required=True, choices=[
      "list", "issues"])
    parser.add_argument('--keys', help="comma separated issues keys")
    parser.add_argument('--status', help="restrict list to specified status")
    parser.add_argument('--xstatus', help="exclude specified status")
    parser.add_argument('--showstatus', action='store_true')
    parser.add_argument('--showtype', action='store_true')
    parser.add_argument('--showpriority', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parsed_args = parser.parse_args(argv)
    # ew(f"parsed_args={pprint.pformat(parsed_args)}")
    rc = QJira(parsed_args).run()
    return rc


if __name__ == '__main__':
    rc = main(sys.argv[1:])
    if rc != 0:
        ew(f"rc={rc}")
    sys.exit(rc)
