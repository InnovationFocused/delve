from pathlib import Path
from socket import gethostname

default_installation_directory = Path("~/.delve").expanduser()

def get_defaults(installation_directory: Path):
    return {
        "default_server_config": {
            'global': {
                'disableWatchdogWarning': False,
                'showWarningOnDirectExecution': True,
                'dataFrameSerialization': 'arrow'},
                'logger': {
                    'level': 'info',
                    'messageFormat': '%(asctime)s %(message)s'
                },
                'client': {
                    'caching': True,
                    'displayEnabled': True,
                    'showErrorDetails': True
                },
                'runner': {
                    'magicEnabled': True,
                    'installTracer': False,
                    'fixMatplotlib': True,
                    'postScriptGC': True,
                    'fastReruns': False
                },
                'server': {
                    'folderWatchBlacklist': [],
                    'fileWatcherType': 'auto',
                    'cookieSecret': 'lksjdfhlsiuhfiasuhliw321o38u9sduh9',
                    'headless': False,
                    'runOnSave': False,
                    'port': 8501,
                    'baseUrlPath': '',
                    'enableCORS': True,
                    'enableXsrfProtection': True,
                    'maxUploadSize': 200,
                    'maxMessageSize': 200,
                    'enableWebsocketCompression': False
                },
                'browser': {
                    'serverAddress': 'localhost',
                    'gatherUsageStats': True,
                    'serverPort': 8501
                },
                'mapbox': {
                    'token': ''
                },
                'deprecation': {
                    'showfileUploaderEncoding': True,
                    'showPyplotGlobalUse': True
                },
                'theme': {}
        },
        "default_database_config": {
            "bind": {
                "provider": "sqlite",
                "filename":  str(installation_directory.resolve().joinpath("db.sqlite")),
                "create_db": True,
            },
        },
        "default_plugins_config": {
            "installed_apps": [
                "delve.contrib.search",
            ],
            "default_dashboard": "delve.contrib.search.dashboards.main",
            "search": {
                "rex": "delve.plugins.search.rex",
                "save": "delve.plugins.search.save",
                "search": "delve.plugins.search.search",
                # "stats": "delve.plugins.search.stats",
                # "df-plot": "delve.plugins.search.df_plot",
                "extract-json": "delve.plugins.search.extract_json",
                "add-field": "delve.plugins.search.add_field",
                "drop": "delve.plugins.search.drop",
                "extracted": "delve.plugins.search.extracted",
                "to-df": "delve.plugins.search.to_df",
                "describe": "delve.plugins.search.df.describe.describe",
                "line": "delve.plugins.search.df.line.line",
            },
            "input": {
                "handler_map": {
                    "python": "delve.plugins.input.PythonInputHandler",
                    "file": "delve.plugins.input.FileInputHandler",
                },
            },
        },
        "default_inputs_config": {
            # "python://sys.stdin": {
            #     "index": "stdin",
            #     "host": gethostname(),
            #     "source": "stdin",
            #     "sourcetype": "text stream",
            #     "extractions": [],
            #     "transformations": [],
            #     "tags": [
            #         "stdin",
            #         gethostname(),
            #     ],
            # },
            "python://delve.fake_cpu_readings": {
                "index": "default",
                "host": gethostname(),
                "source": "metrics",
                "sourcetype": "cpu_usage",
                "extractions": [],
                "transformations": [],
                "tags": [
                    "stdin",
                    gethostname(),
                ],
            },
            "file:///var/log/dpkg.log": {
                "index": "default",
                "host": gethostname(),
                "source": "dpkg",
                "sourcetype": "dpkg",
                "extractions": [
                    "delve.plugins.extractions.syslog",
                ],
                "transformations": [],
                "tags": [
                    "syslog",
                    gethostname(),
                ],
            },
        },
        "default_logging_config": {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(process)d - %(thread)d - %(levelname)-8s - %(message)s"
                }
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout",
                },
                "stderr": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "simple",
                    "stream": "ext://sys.stderr"
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "simple",
                    "filename": str(installation_directory.joinpath("logs").joinpath("out.log")),
                    "mode": "w"
                }
            },
            "root": {
                "level": "DEBUG",
                "handlers": [
                    # "stderr",
                    "stdout",
                    "file"
                ]
            },
        }
    }