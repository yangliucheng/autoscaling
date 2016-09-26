package common

import (
	"github.com/codegangsta/cli"
	"golang.org/x/net/context"
	"net/http"
)

func ServeCmd(c *cli.Context, ctx context.Context, routes map[string]map[string]Handler) error {
	r := NewRouter(ctx, routes)
	return http.ListenAndServe(c.String("addr"), r)
}
