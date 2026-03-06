package db

import (
	"database/sql"

	_ "modernc.org/sqlite"
)

const Path = "test.db"

// Init создаёт таблицы при первом запуске.
func Init() error {
	conn, err := sql.Open("sqlite", Path)
	if err != nil {
		return err
	}
	defer conn.Close()

	_, err = conn.Exec("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
	return err
}

// Open возвращает новое соединение с БД.
func Open() (*sql.DB, error) {
	return sql.Open("sqlite", Path)
}
