package models

// User — модель пользователя.
type User struct {
	ID   int64  `json:"id"`
	Name string `json:"name"`
}

// AddUserRequest — тело запроса на добавление пользователя.
type AddUserRequest struct {
	Name string `json:"name"`
}
