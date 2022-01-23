Changes for v0.3.2 (2022-01-23)
===============================

-  Bump dependency to incorporate fix; add regression test

Changes for v0.3.1 (2021-12-25)
===============================

-  Update release script

Changes for v0.3.0 (2021-12-25)
===============================

-  Add supports_statement_cache flag. Fixes #29

-  Add error code extraction (#31)

-  Format with DataAPI supported format for dates (#24)

-  Set supports_sane_multi_rowcount = False on
   AuroraPostgresDataAPIDialect (#28)

-  Tell SQLAlchemy: mysql supports native decimal (fixes #25) (#26)

Changes for v0.2.7 (2020-12-12)
===============================

Bump dependency version

Changes for v0.2.6 (2020-11-13)
===============================

Bump dependency version

Changes for v0.2.5 (2020-10-03)
===============================

Bump dependency version

Changes for v0.2.4 (2020-10-02)
===============================

Bump dependency version

Changes for v0.2.3 (2020-10-02)
===============================

-  Bump dependency version

-  Fix strptime handling in Python 3.6 and earlier

Changes for v0.2.2 (2020-10-02)
===============================

-  Bump aurora-data-api dependency

Changes for v0.2.1 (2020-10-01)
===============================

-  Fall back to strptime if fromisoformat is not available

-  Merge pull request #8 from olinger/master (Add colspecs for mySQL
   date, time and datetime types)

-  Merge pull request #11 from romibuzi/master (Return error code
   instead of enum entry)

Changes for v0.2.0 (2020-01-02)
===============================

-  Bump aurora-data-api dependency

Changes for v0.1.6 (2020-01-02)
===============================

-  Add enum support

Changes for v0.1.5 (2020-01-01)
===============================

Fix handling of non-dialect-specific datetime types

Changes for v0.1.4 (2019-11-18)
===============================

-  Conform to dialect interface definition

-  MySQL: Return actual client charset

Changes for v0.1.3 (2019-11-10)
===============================

-  Begin MySQL support

Changes for v0.1.2 (2019-10-31)
===============================

-  Fix timestamp microsecond handling

Changes for v0.1.1 (2019-10-31)
===============================

-  Begin array support

-  Improve datetime support

Changes for v0.1.0 (2019-10-29)
===============================

-  Fix postgresql type compatibility issues

Changes for v0.0.2 (2019-10-24)
===============================

Add MySQL dialect

Changes for v0.0.1 (2019-10-10)
===============================

-  Begin sqlalchemy-aurora-data-api

