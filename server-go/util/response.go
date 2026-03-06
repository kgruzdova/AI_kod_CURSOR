package util

import (
	"encoding/json"
	"io"
	"net/http"
)

// DecodeJSON декодирует тело запроса в v.
func DecodeJSON(r *http.Request, v any) error {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		return err
	}
	return json.Unmarshal(body, v)
}

// WriteJSON записывает JSON-ответ с указанным статусом.
func WriteJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

// ErrorResponse — ответ с ошибкой.
func ErrorResponse(msg string) map[string]string {
	return map[string]string{"error": msg}
}
