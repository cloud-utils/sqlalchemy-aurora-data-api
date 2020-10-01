sqlalchemy-aurora-data-api - An AWS Aurora Serverless Data API dialect for SQLAlchemy
=====================================================================================

This package provides a `SQLAlchemy <https://www.sqlalchemy.org>`_
`dialect <https://docs.sqlalchemy.org/en/13/dialects/>`_ for accessing PostgreSQL and MySQL databases via the
`AWS Aurora Data API <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html>`_.

Installation
------------
::

    pip install sqlalchemy-aurora-data-api

Prerequisites
-------------
* Set up an
  `AWS Aurora Serverless cluster <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.html>`_
  and enable Data API access for it. If you have previously set up an Aurora Serverless cluster, you can enable Data API
  with the following `AWS CLI <https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html>`_ command::

      aws rds modify-db-cluster --db-cluster-identifier DB_CLUSTER_NAME --enable-http-endpoint --apply-immediately

* Save the database credentials in
  `AWS Secrets Manager <https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html>`_ using a format
  expected by the Data API (a JSON object with the keys ``username`` and ``password``)::

      aws secretsmanager create-secret --secret-id rds-db-credentials/MY_DB
      aws secretsmanager put-secret-value --secret-id rds-db-credentials/MY_DB --secret-string "$(jq -n '.username=env.PGUSER | .password=env.PGPASSWORD')"

* Configure your AWS command line credentials using
  `standard AWS conventions <https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html>`_.
  You can verify that everything works correctly by running a test query via the AWS CLI::

      aws rds-data execute-statement --resource-arn RESOURCE_ARN --secret-arn SECRET_ARN --sql "select * from pg_catalog.pg_tables"

  * Here, RESOURCE_ARN refers to the Aurora RDS database ARN, which can be found in the
    `AWS RDS Console <https://console.aws.amazon.com/rds/home#databases:>`_ (click on your database, then "Configuration")
    or in the CLI by running ``aws rds describe-db-clusters``. SECRET_ARN refers to the AWS Secrets Manager secret
    created above.

  * When running deployed code (on an EC2 instance, ECS/EKS container, or Lambda), you can use the managed IAM policy
    **AmazonRDSDataFullAccess** to grant your IAM role permissions to access the RDS Data API (while this policy is
    convenient for testing, we recommend that you create your own scoped down least-privilege policy for production
    applications).

Usage
-----

The package registers two SQLAlchemy dialects, ``mysql+auroradataapi://`` and ``postgresql+auroradataapi://``. Two
``sqlalchemy.create_engine()`` `connect_args <https://docs.sqlalchemy.org/en/13/core/engines.html#custom-dbapi-args>`_
keyword arguments are required to connect to the database:

* ``aurora_cluster_arn`` (also referred to as ``resourceArn`` in the
  `Data API documentation <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds-data.html>`_)

  * If not given as a keyword argument, this can also be specified using the ``AURORA_CLUSTER_ARN`` environment variable

* ``secret_arn`` (the database credentials secret)

  * If not given as a keyword argument, this can also be specified using the ``AURORA_SECRET_ARN`` environment variable

All connection string contents other than the protocol (dialect) and the database name (path component, ``my_db_name``
in the example below) are ignored.

.. code-block:: python

    from sqlalchemy import create_engine

    cluster_arn = "arn:aws:rds:us-east-1:123456789012:cluster:my-aurora-serverless-cluster"
    secret_arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds-db-credentials/MY_DB"

    engine = create_engine('postgresql+auroradataapi://:@/my_db_name',
                           echo=True,
                           connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))

    with engine.connect() as conn:
        for result in conn.execute("select * from pg_catalog.pg_tables"):
            print(result)

Motivation
----------
The `RDS Data API <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html>`_ is the link between the
AWS Lambda serverless environment and the sophisticated features provided by PostgreSQL and MySQL. The Data API tunnels
SQL over HTTP, which has advantages in the context of AWS Lambda:

* It eliminates the need to open database ports to the AWS Lambda public IP address pool
* It uses stateless HTTP connections instead of stateful internal TCP connection pools used by most database drivers
  (the stateful pools become invalid after going through
  `AWS Lambda freeze-thaw cycles <https://docs.aws.amazon.com/lambda/latest/dg/running-lambda-code.html>`_, causing
  connection errors and burdening the database server with abandoned invalid connections)
* It uses AWS role-based authentication, eliminating the need for the Lambda to handle database credentials directly

Debugging
---------

This package uses standard Python logging conventions. To enable debug output, set the package log level to DEBUG::

    logging.basicConfig()

    logging.getLogger("aurora_data_api").setLevel(logging.DEBUG)

Links
-----
* `Project home page (GitHub) <https://github.com/chanzuckerberg/sqlalchemy-aurora-data-api>`_
* `Documentation (Read the Docs) <https://sqlalchemy-aurora-data-api.readthedocs.io/en/latest/>`_
* `Package distribution (PyPI) <https://pypi.python.org/pypi/sqlalchemy-aurora-data-api>`_
* `Change log <https://github.com/chanzuckerberg/sqlalchemy-aurora-data-api/blob/master/Changes.rst>`_
* `aurora-data-api <https://github.com/chanzuckerberg/aurora-data-api>`_, the Python DB-API 2.0 client that
  sqlalchemy-aurora-data-api depends on

Bugs
~~~~
Please report bugs, issues, feature requests, etc. on
`GitHub <https://github.com/chanzuckerberg/sqlalchemy-aurora-data-api/issues>`_.

License
-------
Licensed under the terms of the `Apache License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_.

.. image:: https://travis-ci.org/chanzuckerberg/sqlalchemy-aurora-data-api.png
        :target: https://travis-ci.org/chanzuckerberg/sqlalchemy-aurora-data-api
.. image:: https://codecov.io/github/chanzuckerberg/sqlalchemy-aurora-data-api/coverage.svg?branch=master
        :target: https://codecov.io/github/chanzuckerberg/sqlalchemy-aurora-data-api?branch=master
.. image:: https://img.shields.io/pypi/v/sqlalchemy-aurora-data-api.svg
        :target: https://pypi.python.org/pypi/sqlalchemy-aurora-data-api
.. image:: https://img.shields.io/pypi/l/sqlalchemy-aurora-data-api.svg
        :target: https://pypi.python.org/pypi/sqlalchemy-aurora-data-api
.. image:: https://readthedocs.org/projects/sqlalchemy-aurora-data-api/badge/?version=latest
        :target: https://sqlalchemy-aurora-data-api.readthedocs.org/
