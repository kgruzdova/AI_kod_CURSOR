package handlers

import (
	"net/http"
	"strings"
	"sync"
	"time"

	"server-go/util"
)

var (
	active    []string
	activeMux sync.Mutex
)

// Activate добавляет uid в список активных в фоновой горутине.
func Activate(w http.ResponseWriter, r *http.Request) {
	uid := strings.TrimPrefix(r.URL.Path, "/activate/")
	if uid == "" {
		util.WriteJSON(w, http.StatusBadRequest, util.ErrorResponse("uid required"))
		return
	}

	go func() {
		time.Sleep(500 * time.Millisecond)
		activeMux.Lock()
		active = append(active, uid)
		if len(active) > 3 {
			active = active[1:]
		}
		activeMux.Unlock()
	}()

	activeMux.Lock()
	activeCopy := make([]string, len(active))
	copy(activeCopy, active)
	activeMux.Unlock()

	util.WriteJSON(w, http.StatusAccepted, map[string]any{
		"status": "processing",
		"active": activeCopy,
	})
}
