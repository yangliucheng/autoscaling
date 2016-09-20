package main

import (
	"fmt"
	"github.com/dcos/dcos-autoscale/common"
	"github.com/gorilla/mux"
	"golang.org/x/net/context"
	"io/ioutil"
	"net/http"
)

func auto_query_list(ctx context.Context, w http.ResponseWriter, r *http.Request) *common.HttpError {

	client := &http.Client{}
	marathonName := mux.Vars(r)["marathonName"]
	new_query_list_Url := ctx.Value("listaddr").(string) + "/applist/" + marathonName
	fmt.Println("api url %s", new_query_list_Url)
	req, _ := http.NewRequest("POST", new_query_list_Url, nil)
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		return common.NewHttpError("auto_query_list failed", http.StatusInternalServerError)
	}

	list, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		return common.NewHttpError("Read auto_query_list resp body failed", http.StatusInternalServerError)
	}
	w.WriteHeader(http.StatusOK)
	w.Write(list)
	return nil

}

func auto_query_details(ctx context.Context, w http.ResponseWriter, r *http.Request) *common.HttpError {

	client := &http.Client{}
	marathonname := mux.Vars(r)["marathonName"]
	appid := mux.Vars(r)["app_id"]
	new_query_list_Url := ctx.Value("listaddr").(string) + "/appinfo/" + marathonname + "/" + appid
	fmt.Println("api url %s", new_query_list_Url)
	req, _ := http.NewRequest("POST", new_query_list_Url, nil)
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)

	if err != nil {
		return common.NewHttpError("auto_query_details failed", http.StatusInternalServerError)
	}
	list, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		return common.NewHttpError("Read auto_query_details resp body failed", http.StatusInternalServerError)
	}
	w.WriteHeader(http.StatusOK)
	w.Write(list)
	return nil

}

func elastic_expansion_configuration(ctx context.Context, w http.ResponseWriter, r *http.Request) *common.HttpError {

	client := &http.Client{}
	new_query_list_Url := ctx.Value("listaddr").(string) + "/ruleset"
	fmt.Println("api url %s", new_query_list_Url)
	req, _ := http.NewRequest("POST", new_query_list_Url, r.Body)
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)

	if err != nil {
		return common.NewHttpError("elastic_expansion_configuration failed", http.StatusInternalServerError)
	}

	list, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		return common.NewHttpError("Read elastic_expansion_configuration resp body failed", http.StatusInternalServerError)
	}
	w.WriteHeader(http.StatusOK)
	w.Write(list)
	return nil

}

func updating_elastic_expansion(ctx context.Context, w http.ResponseWriter, r *http.Request) *common.HttpError {

	client := &http.Client{}
	new_query_list_Url := ctx.Value("listaddr").(string) + "/ruleupdate"
	fmt.Println("api url %s", new_query_list_Url)
	req, _ := http.NewRequest("POST", new_query_list_Url, r.Body)
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)

	if err != nil {
		return common.NewHttpError("updating_elastic_expansion failed", http.StatusInternalServerError)
	}
	list, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		return common.NewHttpError("Read updating_elastic_expansion resp body failed", http.StatusInternalServerError)
	}
	w.WriteHeader(http.StatusOK)
	w.Write(list)
	return nil

}

func suspend(ctx context.Context, w http.ResponseWriter, r *http.Request) *common.HttpError {

	client := &http.Client{}
	app_id := mux.Vars(r)["app_id"]
	marathon_id := mux.Vars(r)["marathon_id"]
	new_query_list_Url := ctx.Value("listaddr").(string) + "/pause/" + marathon_id + "/" + app_id
	fmt.Println("api url %s", new_query_list_Url)
	req, _ := http.NewRequest("POST", new_query_list_Url, nil)
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		return common.NewHttpError("suspend failed", http.StatusInternalServerError)
	}
	list, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		return common.NewHttpError("Read suspend resp body failed", http.StatusInternalServerError)
	}
	w.WriteHeader(http.StatusOK)
	w.Write(list)
	return nil

}

func turn_on(ctx context.Context, w http.ResponseWriter, r *http.Request) *common.HttpError {

	client := &http.Client{}
	app_id := mux.Vars(r)["app_id"]
	marathon_id := mux.Vars(r)["marathon_id"]
	new_query_list_Url := ctx.Value("listaddr").(string) + "/recover/" + marathon_id + "/" + app_id
	fmt.Println("api url %s", new_query_list_Url)
	req, _ := http.NewRequest("POST", new_query_list_Url, nil)
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		return common.NewHttpError("turn_on failed", http.StatusInternalServerError)
	}
	list, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		return common.NewHttpError("Read turn_on resp body failed", http.StatusInternalServerError)
	}
	w.WriteHeader(http.StatusOK)
	w.Write(list)
	return nil

}
