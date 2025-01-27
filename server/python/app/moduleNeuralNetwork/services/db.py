import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional


class DB:
    def __init__(self, db_name, user, password, host='localhost', port=5432):
        """
        db_name: Название базы данных.
        user: Пользователь PostgreSQL.
        password: Пароль пользователя.
        host: Адрес хоста (по умолчанию 'localhost').
        port: Порт (по умолчанию 5432).
        """
        self.__db_name = db_name
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port

        self.__conn = None
        self.__cur = None

        self.__connect()

    def __connect(self):
        """Устанавливает соединение и создаёт курсор."""
        self.__conn = psycopg2.connect(
            dbname=self.__db_name,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port
        )
        self.__cur = self.__conn.cursor()

    def close(self):
        """Закрывает курсор и соединение с БД."""
        if self.__cur:
            self.__cur.close()
            self.__cur = None
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    def __table_exists(self, table_name: str) -> bool:
        """
        Проверяет, существует ли таблица в текущей базе.
        Возвращает True, если таблица существует, иначе False.
        """

        query = sql.SQL("SELECT to_regclass(%s)")
        self.__cur.execute(query, (table_name,))
        result = self.__cur.fetchone()

        return result[0] is not None

    def get_data(
            self,
            table_name: str,
            fields: Optional[List[str]] = None,
            filters: Optional[Dict[str, Any]] = None
    ):
        """
        Получает данные из заданной таблицы (по умолчанию все столбцы).
        :param table_name: Название таблицы
        :param fields: Список нужных полей (например: ['id', 'username']).
                       Если не указано, будет SELECT *.
        :param filters: Словарь вида:
            {
                'id': {
                    'value': 123,
                    'operator_compare': '<',
                    'operator_condition': 'AND'
                },
                'user': {
                    'value': 'ioio',
                    'operator_compare': '=',
                    'operator_condition': ''
                }
            }
            - Ключ: имя столбца
            - value: значение для этого столбца
            - operator_compare: оператор сравнения (<, >, =, LIKE, ...)
            - operator_condition: логический оператор, которым соединяем УСЛОВИЕ с **следующим** (AND/OR/...).
                                  Пустая строка — значит без оператора (последнее условие или единичное).
        :return: Список кортежей с результатами запроса (или None, если таблицы нет).
        """
        # Проверяем существование таблицы
        if not self.__table_exists(table_name=table_name):
            return None

        # Если поля не указаны (или пусты) — SELECT *
        if not fields:
            fields_sql = sql.SQL('*')
        else:
            # Если в списке есть '*', обрабатываем её отдельно
            # Простейший вариант: если там ТОЛЬКО '*', делаем так:
            if fields == ['*']:
                fields_sql = sql.SQL('*')
            else:
                # Иначе составляем список sql.Identifier для каждого поля
                # (кроме тех случаев, когда хотите допустим mix "*, field1, field2" — тогда нужно сложнее обрабатывать)
                fields_sql = sql.SQL(', ').join(sql.Identifier(f) for f in fields)

        # SELECT {fields} FROM {table}
        base_query = sql.SQL("SELECT {fields} FROM {table}").format(
            fields=fields_sql,
            table=sql.Identifier(table_name),
        )

        where_clause = sql.SQL("")
        params = {}

        if filters:
            conditions_parts = []

            for col, filter_data in filters.items():
                val = filter_data.get('value')
                operator_compare = filter_data.get('operator_compare', '=')
                operator_condition = filter_data.get('operator_condition', '').upper()

                condition_expr = sql.Composed([
                    sql.Identifier(col),
                    sql.SQL(f" {operator_compare} "),
                    sql.Placeholder(col)
                ])
                conditions_parts.append(condition_expr)

                params[col] = val

                if operator_condition:
                    op_cond_expr = sql.SQL(f" {operator_condition} ")
                    conditions_parts.append(op_cond_expr)

            if conditions_parts:
                last_part = conditions_parts[-1]
                if isinstance(last_part, sql.SQL):
                    last_str = last_part.as_string(self.__conn).strip()
                    if last_str in ("AND", "OR"):
                        conditions_parts.pop()

            if conditions_parts:
                where_clause = sql.SQL("WHERE ") + sql.Composed(conditions_parts)

        query = sql.SQL(" ").join([base_query, where_clause])

        self.__cur.execute(query, params)
        rows = self.__cur.fetchall()

        col_names = [desc[0] for desc in self.__cur.description]

        result = []
        for row in rows:
            row_dict = dict(zip(col_names, row))
            result.append(row_dict)

        return result

    def add_data(self, table_name: str, data: dict, return_column: str = 'id'):
        """
        Добавляет данные в таблицу.
        data: словарь вида {поле: значение}.
        Возвращает id вставленной записи, если он определяется (RETURNING id).
        """
        if not self.__table_exists(table_name=table_name):
            return None

        columns = data.keys()
        values = data.values()

        insert_query = sql.SQL(
            "INSERT INTO {table} ({fields}) VALUES ({placeholders}) RETURNING " + return_column).format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(', ').join(sql.Identifier(col) for col in columns),
            placeholders=sql.SQL(', ').join(sql.Placeholder() for _ in columns)
        )

        self.__cur.execute(insert_query, tuple(values))
        new_id_row = self.__cur.fetchone()
        self.__conn.commit()

        if new_id_row:
            return new_id_row[0]
        return None

    def update_data(self, table_name: str, record_id: int, new_data: dict):
        """
        Обновляет запись по id (record_id).
        new_data: словарь {поле: новое_значение}.
        Возвращает True, если хотя бы одна строка обновилась.
        """
        if not self.__table_exists(table_name=table_name):
            return None

        # Сформируем динамический SET, например: "username = %s, email = %s"
        set_clause = []
        values = []
        for col, val in new_data.items():
            set_clause.append(sql.SQL("{} = %s").format(sql.Identifier(col)))
            values.append(val)

        update_query = sql.SQL("UPDATE {table} SET {set_clause} WHERE id = %s").format(
            table=sql.Identifier(table_name),
            set_clause=sql.SQL(", ").join(set_clause)
        )

        # Добавляем record_id последним параметром
        values.append(record_id)

        self.__cur.execute(update_query, tuple(values))
        self.__conn.commit()

        return self.__cur.rowcount > 0  # rowcount показывает, сколько строк затронуто

    def delete_data(self, table_name: str, record_id: int) -> Optional[bool]:
        """
        Удаляет запись из таблицы по её id.
        Возвращает True, если запись была удалена (rowcount > 0).
        """
        if not self.__table_exists(table_name=table_name):
            return None

        delete_query = sql.SQL("DELETE FROM {table} WHERE id = %s").format(
            table=sql.Identifier(table_name)
        )
        self.__cur.execute(delete_query, (record_id,))
        self.__conn.commit()

        return self.__cur.rowcount > 0
