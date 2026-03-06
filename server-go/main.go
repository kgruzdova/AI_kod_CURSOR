// API-сервер для управления пользователями на Go.
package main

import (
	"net/http"
	"time"

	"server-go/db"
	"server-go/router"
)

func main() {
	if err := db.Init(); err != nil {
		panic(err)
	}

	server := &http.Server{
		Addr:         "0.0.0.0:8080",
		Handler:      router.Setup(),
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	if err := server.ListenAndServe(); err != nil {
		panic(err)
	}
}
