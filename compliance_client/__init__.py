#!/usr/bin/env python

from sys import exit,stderr
from insights.client.connection import InsightsConnection
from insights.client.config import InsightsConfig
from insights.util.canonical_facts import get_canonical_facts
from subprocess import Popen, PIPE, STDOUT
from re import findall
from os import environ
from platform import linux_distribution
from glob import glob

OSCAP_RESULTS_OUTPUT = '/tmp/oscap_results.xml'
UPLOAD_ARGS = filter(None, [environ.get('UPLOAD_ARGS', None)])
NONCOMPLIANT_STATUS = 2

def get_config():
    try:
        return InsightsConfig(_print_errors=True).load_all()
    except ValueError as e:
        stderr.write('ERROR: ' + str(e) + '\n')
        exit(1)

# TODO: Not a typo! This endpoint gives OSCAP policies, not profiles
# We need to update compliance-backend to fix this
def get_policies(conn, hostname):
    response = conn.session.get("https://ci.foo.redhat.com:1337/api/compliance/profiles", params={'hostname': hostname}, verify=False)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return []

def os_release():
    _,version,_ = linux_distribution()
    return findall("^7", version)[0]

def profile_files():
    return glob("/usr/share/xml/scap/ssg/content/*rhel{}*.xml".format(os_release()))

def find_scap_policy(profile_ref_id):
    grep = Popen(["grep", profile_ref_id] + profile_files(), stdout=PIPE, stderr=STDOUT)
    if grep.wait():
        stderr.write('ERROR: XML profile file not found matching ref_id {}\n{}\n'.format(profile_ref_id, grep.stderr.read()))
        exit(1)
    filenames = findall('/usr/share/xml/scap/.+xml', grep.stdout.read())
    if not filenames:
        stderr.write('ERROR: Multiple XML profile files found matching ref_id {}\n{}\n'.format(profile_ref_id, ' '.join(filenames)))
        exit(1)
    return filenames[0]

def run_scan(profile_ref_id, policy_xml):
    print("Running scan... this may take a while")
    oscap = Popen(["oscap", "xccdf", "eval", "--profile", profile_ref_id, "--results", OSCAP_RESULTS_OUTPUT, policy_xml], stdout=PIPE, stderr=STDOUT)
    if oscap.wait() and oscap.wait() != NONCOMPLIANT_STATUS:
        stderr.write("ERROR: Scan failed")
        stderr.write(oscap.stderr.read())
        exit(1)

def upload_results():
    client = Popen(["insights-client", "--payload", OSCAP_RESULTS_OUTPUT, "--content-type", "application/vnd.redhat.compliance.something+tgz"] + UPLOAD_ARGS, stdout=PIPE, stderr=STDOUT)
    if client.wait():
        stderr.write("ERROR: Upload of OSCAP report failed")
        stderr.write(client.stderr.read())
        exit(1)
    return client.stdout.read()

def main():
    config = get_config()
    conn = InsightsConnection(config)
    conn.session.headers['x-rh-identity'] = environ.get('x-rh-identity', '')

    fqdn = get_canonical_facts()['fqdn']
    policies = get_policies(conn, fqdn)
    if not policies:
        stderr.write("ERROR: System does not exist!\n")
        exit(1)
    profile_ref_id = map(lambda policy: policy['attributes']['ref_id'], policies)[0]
    scap_policy_xml = find_scap_policy(profile_ref_id)
    run_scan(profile_ref_id, scap_policy_xml)
    print(upload_results())

if __name__ == '__main__':
    main()
