from mindsdb_server.api.mysql.mysql_proxy.datasources.datasource import DataSource
import ray


class RayDataSourceWrapper(DataSource):
    instance = None

    def __init__(self, instance):
        self.instance = instance

    @property
    def type(self):
        return self.getType()

    def getType(self):
        return ray.get(
            self.instance.getType.remote()
        )

    def getTables(self):
        return ray.get(
            self.instance.getTables.remote()
        )

    def hasTable(self, tableName):
        return ray.get(
            self.instance.hasTable.remote(tableName)
        )

    def getTableColumns(self, tableName):
        return ray.get(
            self.instance.getTableColumns.remote(tableName)
        )

    def select(self, table=None, columns=None, where=None, where_data=None, order_by=None, group_by=None):
        return self.instance.select.remote(
            table=table,
            columns=columns,
            where=where,
            where_data=where_data,
            order_by=order_by,
            group_by=group_by
        )
