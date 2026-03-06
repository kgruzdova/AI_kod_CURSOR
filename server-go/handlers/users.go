package handlers

import (
	"database/sql"
	"errors"
	"net/http"
	"strconv"
	"strings"

	"server-go/db"
	"server-go/models"
	"server-go/util"
)

// AddUser добавляет пользователя.
func AddUser(w http.ResponseWriter, r *http.Request) {
	var body models.AddUserRequest
	if err := util.DecodeJSON(r, &body); err != nil {
		util.WriteJSON(w, http.StatusBadRequest, util.ErrorResponse("invalid JSON"))
		return
	}
	name := strings.TrimSpace(body.Name)
	if name == "" {
		util.WriteJSON(w, http.StatusBadRequest, util.ErrorResponse("name is required"))
		return
	}

	conn, err := db.Open()
	if err != nil {
		util.WriteJSON(w, http.StatusInternalServerError, util.ErrorResponse(err.Error()))
		return
	}
	defer conn.Close()

	_, err = conn.Exec("INSERT INTO users (name) VALUES (?)", name)
	if err != nil {
		util.WriteJSON(w, http.StatusInternalServerError, util.ErrorResponse(err.Error()))
		return
	}

	util.WriteJSON(w, http.StatusCreated, map[string]string{"status": "ok"})
}

// GetUser возвращает пользователя по ID.
func GetUser(w http.ResponseWriter, r *http.Request) {
	uidStr := strings.TrimPrefix(r.URL.Path, "/user/")
	uid, err := strconv.ParseInt(uidStr, 10, 64)
	if err != nil || uid <= 0 {
		util.WriteJSON(w, http.StatusBadRequest, util.ErrorResponse("invalid id"))
		return
	}

	conn, err := db.Open()
	if err != nil {
		util.WriteJSON(w, http.StatusInternalServerError, util.ErrorResponse(err.Error()))
		return
	}
	defer conn.Close()

	var u models.User
	err = conn.QueryRow("SELECT id, name FROM users WHERE id = ?", uid).Scan(&u.ID, &u.Name)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			util.WriteJSON(w, http.StatusNotFound, util.ErrorResponse("not found"))
			return
		}
		util.WriteJSON(w, http.StatusInternalServerError, util.ErrorResponse(err.Error()))
		return
	}

	util.WriteJSON(w, http.StatusOK, u)
}
