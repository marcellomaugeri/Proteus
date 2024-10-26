# Data Analysis Track

The scope of the notebook in this folder is to download the data of June 2024 from the Polygon chain using BigQuery and demeter-fetch.


### Use demeter-fetch
The version of demeter-fetch in PyPi has some bugs.
As a consequence, it is suggested to run it from source code.

```
# Clone the repository
git clone https://github.com/zelos-alpha/demeter-fetch
# Install requirements (Python >= 3.11)
pip install -r demeter-fetch/requirements.txt
```

Then you need to setup a Google Cloud project, a service user with BigQuery admin permissions and download the credentials in JSON format.
Rename the file bigquerykey.json

```
# Finally, run demeter-fetch with the provided config file
python3 demeter-fetch/main.py -c config.aave.toml
```

The output will be in a sample folder.
Now you can open the Jupyter notebook.
