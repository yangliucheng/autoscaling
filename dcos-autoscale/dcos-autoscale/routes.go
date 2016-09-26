package main

import (
	"github.com/dcos/dcos-autoscale/common"
)

var routes = map[string]map[string]common.Handler{
	"GET": {
		"/autoscale/api/v1/auto_query_list/{marathonName}":             auto_query_list,
		"/autoscale/api/v1/auto_query_details/{marathonName}/{app_id}": auto_query_details,
	},
	"POST": {
		"/autoscale/api/v1/elastic_expansion_configuration": elastic_expansion_configuration,
	},
	"PATCH": {
		"/autoscale/api/v1/updating_elastic_expansion":     updating_elastic_expansion,
		"/autoscale/api/v1/suspend/{app_id}/{marathon_id}": suspend,
		"/autoscale/api/v1/turn_on/{app_id}/{marathon_id}": turn_on,
	},
}
