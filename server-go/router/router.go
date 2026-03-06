package router

import (
	"net/http"

	"server-go/handlers"
)

// Setup возвращает настроенный http.Handler.
func Setup() http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("POST /adduser", handlers.AddUser)
	mux.HandleFunc("GET /user/", handlers.GetUser)
	mux.HandleFunc("GET /activate/", handlers.Activate)
	mux.HandleFunc("GET /slow", handlers.Slow)
	mux.HandleFunc("GET /wrong", handlers.Wrong)

	return mux
}
