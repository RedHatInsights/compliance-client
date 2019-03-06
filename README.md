# compliance-client
Code for the compliance client.

## Set up

Clone insights-client, insights-core, and compliance-client. This loosly follows
the docs in the [insights-client repo](https://github.com/RedHatInsights/insights-client#developer-setup):

```sh
export CWD=`pwd`
git clone https://github.com/RedHatInsights/insights-client.git
git clone https://github.com/RedHatInsights/insights-core.git
git clone https://github.com/RedHatInsights/compliance-client.git
```

Install insights-core and insights-client eggs

```sh
cd insights-client; sudo sh lay-the-eggs.sh; cd ..
sudo pip install -I file://$CWD/insights-core#egg=insights
```

Run the compliance client

```sh
sudo x-rh-identity=<your x-rh-identity header> python $CWD/compliance-client/compliance_client/__init__.py
```
