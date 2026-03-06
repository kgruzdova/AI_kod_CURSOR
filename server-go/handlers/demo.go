package handlers

import (
	"fmt"
	"net/http"
	"strconv"

	"server-go/util"
)

// Slow выполняет тяжёлые вычисления.
func Slow(w http.ResponseWriter, r *http.Request) {
	var x int64
	for i := 0; i < 1_000_000; i++ {
		for j := 0; j < 100; j++ {
			x += int64(i * j)
		}
	}
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte(strconv.FormatInt(x, 10)))
}

// Wrong — пример обработки panic при делении на ноль.
func Wrong(w http.ResponseWriter, r *http.Request) {
	defer func() {
		if err := recover(); err != nil {
			util.WriteJSON(w, http.StatusInternalServerError, map[string]any{
				"msg":   "error",
				"error": fmt.Sprint(err),
			})
		}
	}()
	a := 0
	_ = 10 / a // division by zero
	util.WriteJSON(w, http.StatusOK, map[string]any{"msg": "ok", "data": a})
}
