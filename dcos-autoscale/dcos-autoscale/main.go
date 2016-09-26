package main

import (
	"fmt"
	"github.com/codegangsta/cli"
	"github.com/dcos/dcos-autoscale/common"
	"golang.org/x/net/context"
	"log"
	"os"
)

// Init database before
// CREATE TABLE images(id varchar(36) NOT NULL,image_id varchar(120) NOT NULL, visibility boolean, owner varchar(120), submission_date DATE, image_name varchar(120) NOT NULL, label varchar(120), PRIMARY KEY(owner,image_name,label));
func main() {
	serveCommand := cli.Command{
		Name:      "serve",
		ShortName: "s",
		Usage:     "Serve the API",
		Flags:     []cli.Flag{common.FlAddr, common.Fllistaddr},
		Action:    action(serveAction),
	}

	fmt.Println(common.FlAddr.Value)
	log.SetPrefix("==>")
	log.Printf("listen: %v", common.FlAddr.Value)
	common.Run("dcos-autoscale", serveCommand)
}

func serveAction(c *cli.Context) error {
	ctx := context.Background()
	ctx = context.WithValue(ctx, "addr", c.String("addr"))
	ctx = context.WithValue(ctx, "listaddr", c.String("listaddr"))
	return common.ServeCmd(c, ctx, routes)
}

func action(f func(c *cli.Context) error) func(c *cli.Context) {
	return func(c *cli.Context) {
		err := f(c)
		if err != nil {
			os.Exit(1)
		}
	}
}
