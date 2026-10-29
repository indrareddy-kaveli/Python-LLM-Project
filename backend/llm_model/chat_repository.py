from contextlib import closing

from db import get_connection


def create_session(session_id: str):
    with closing(get_connection()) as conn:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chat_sessions (session_id)
                    VALUES (%s)
                    ON CONFLICT (session_id) DO NOTHING
                    """,
                    (session_id,),
                )


def save_message(session_id: str, role: str, content: str):
    with closing(get_connection()) as conn:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chat_messages (session_id, role, content)
                    VALUES (%s, %s, %s)
                    """,
                    (session_id, role, content),
                )

                cursor.execute(
                    """
                    UPDATE chat_sessions
                    SET updated_at = NOW()
                    WHERE session_id = %s
                    """,
                    (session_id,),
                )


def get_chat_history(session_id: str):
    with closing(get_connection()) as conn:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT role, content
                    FROM chat_messages
                    WHERE session_id = %s
                    ORDER BY create_at, id
                    """,
                    (session_id,),
                )

                return [
                    {"role": role, "content": content}
                    for role, content in cursor.fetchall()
                ]
                
def get_all_chats():
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    s.session_id,
                    s.create_at,
                    s.updated_at,
                    (
                        SELECT m.content
                        FROM chat_messages AS m
                        WHERE m.session_id = s.session_id
                          AND m.role = 'user'
                        ORDER BY m.create_at, m.id
                        LIMIT 1
                    ) AS title
                FROM chat_sessions AS s
                ORDER BY s.updated_at DESC
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "session_id": row[0],
                    "create_at": row[1],
                    "updated_at": row[2],
                    "title": row[3] or "New Chat",
                }
                for row in rows
            ]


def get_chat_messages(session_id: str):
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT role, content
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY create_at, id
                """,
                (session_id,),
            )

            return [
                {"role": role, "content": content}
                for role, content in cursor.fetchall()
            ]