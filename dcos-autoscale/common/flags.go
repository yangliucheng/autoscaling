package common

import (
	"github.com/codegangsta/cli"
)

var (
	FlAddr = cli.StringFlag{
		Name:  "addr",
		Usage: "<ip>:<port> to listen on",
		Value: "10.254.10.18:9099",
	}
)
