package main

import (
	//"bufio"
	//"bytes"
	//"net"
	"encoding/json"
	log "github.com/Sirupsen/logrus"
	"github.com/prometheus/client_golang/prometheus"
	"io/ioutil"
	"os/exec"
	"strconv"
	"strings"
)

type tomcatCollector struct {
	upIndicator *prometheus.Desc
	metrics     map[string]tomcatMetric
}
type tomcatMetric struct {
	desc          *prometheus.Desc
	extract       func(string) float64
	extractLabels []string
	valType       prometheus.ValueType
}

type DockerInfo struct {
	DockerConfig DockerConfig `json:"Config"`
}

type DockerConfig struct {
	Hostname string   `json:"Hostname"`
	Label    Label    `json:"Labels"`
	Env      []string `json:"Env"`
}

type Label struct {
	ThreadMonitor string `json:"THREAD_MONITOR"`
}

func init() {
	prometheus.MustRegister(NewTomcatCollector())
}

func parseFloat(s string) float64 {
	s = strings.Replace(s, " ", "", -1)
	res, err := strconv.ParseFloat(s, 64)
	if err != nil {
		log.Warningf("Failed to parse to int: %s", err)
		return 0
	}
	return res
}
func NewTomcatCollector() *tomcatCollector {
	var variableLabels = []string{"containerId", "appId", "marathonName"}
	return &tomcatCollector{
		upIndicator: prometheus.NewDesc("tomcat_up", "Exporter successful", variableLabels, nil),
		metrics: map[string]tomcatMetric{
			"tomcat_micSessionTotal": {
				desc:    prometheus.NewDesc("tomcat_micSessionTotal", "Number of sessions in use", variableLabels, nil),
				extract: func(s string) float64 { return parseFloat(s) },
				valType: prometheus.GaugeValue,
			},
			"tomcat_threadTotal": {
				desc:    prometheus.NewDesc("tomcat_threadTotal", "total thread amount", variableLabels, nil),
				extract: func(s string) float64 { return parseFloat(s) },
				valType: prometheus.GaugeValue,
			},
			"tomcat_threadIdle": {
				desc:    prometheus.NewDesc("tomcat_threadIdle", "current idle thread amount", variableLabels, nil),
				extract: func(s string) float64 { return parseFloat(s) },
				valType: prometheus.GaugeValue,
			},
			"tomcat_threadStandby": {
				desc:    prometheus.NewDesc("tomcat_threadStandby", "current stanby thread amount", variableLabels, nil),
				extract: func(s string) float64 { return parseFloat(s) },
				valType: prometheus.GaugeValue,
			},
			"tomcat_threadRunning": {
				desc:    prometheus.NewDesc("tomcat_threadRunning", "current running thread amount", variableLabels, nil),
				extract: func(s string) float64 { return parseFloat(s) },
				valType: prometheus.GaugeValue,
			},
			"tomcat_jvmMemMax": {
				desc:    prometheus.NewDesc("tomcat_jvmMemMax", "tomcat jvm max mem", variableLabels, nil),
				extract: func(s string) float64 { return parseFloat(s) },
				valType: prometheus.GaugeValue,
			},
			"tomcat_jvmMemUsed": {
				desc:    prometheus.NewDesc("tomcat_jvmMemUsed", "tomcat jvm used mem", variableLabels, nil),
				extract: func(s string) float64 { return parseFloat(s) },
				valType: prometheus.GaugeValue,
			},
		},
	}
}

func (c *tomcatCollector) Describe(ch chan<- *prometheus.Desc) {
	log.Debugf("Sending %d metrics descriptions", len(c.metrics))
	for _, i := range c.metrics {
		ch <- i.desc
	}
}

func (c *tomcatCollector) Collect(ch chan<- prometheus.Metric) {
	log.Info("Fetching metrics from tomcat")

	containerList, err := getContainerList()
	if nil != err {
		log.Error("get container list by docker ps error ")
		return
	}
	if nil == containerList {
		log.Error("there is no docker running container ")
		return
	}
	for _, containerId := range containerList {
		log.Error("containerId :", containerId)

		if "CONTAINER" == containerId || "" == containerId {
			continue
		}

		dockerInfo, err := getDockerConfig(containerId)
		if nil != err {
			log.Error("docker inspect container failed, containerId :", containerId)
			continue
		}
		tmf := getThreadMonitorFlag(dockerInfo)

		if tmf == "true" {
			appId := getAppId(dockerInfo)
			getMarathonName := getMarathonName(dockerInfo)
			sessions, threadTotal, threadIdle, threadStandBy, threadRunning, jvmMaxMem, jvmUsedMem := getThreadInfo(containerId)
			metric, ok := c.metrics["tomcat_micSessionTotal"]
			if ok {
				ch <- prometheus.MustNewConstMetric(metric.desc, metric.valType, metric.extract(sessions), []string{containerId, appId, getMarathonName}...)
			}

			metric, ok = c.metrics["tomcat_threadTotal"]
			if ok {
				ch <- prometheus.MustNewConstMetric(metric.desc, metric.valType, metric.extract(threadTotal), []string{containerId, appId, getMarathonName}...)
			}

			metric, ok = c.metrics["tomcat_threadIdle"]
			if ok {
				ch <- prometheus.MustNewConstMetric(metric.desc, metric.valType, metric.extract(threadIdle), []string{containerId, appId, getMarathonName}...)
			}

			metric, ok = c.metrics["tomcat_threadStandby"]
			if ok {
				ch <- prometheus.MustNewConstMetric(metric.desc, metric.valType, metric.extract(threadStandBy), []string{containerId, appId, getMarathonName}...)
			}

			metric, ok = c.metrics["tomcat_threadRunning"]
			if ok {
				ch <- prometheus.MustNewConstMetric(metric.desc, metric.valType, metric.extract(threadRunning), []string{containerId, appId, getMarathonName}...)
			}

			metric, ok = c.metrics["tomcat_jvmMemMax"]
			if ok {
				ch <- prometheus.MustNewConstMetric(metric.desc, metric.valType, metric.extract(jvmMaxMem), []string{containerId, appId, getMarathonName}...)
			}

			metric, ok = c.metrics["tomcat_jvmMemUsed"]
			if ok {
				ch <- prometheus.MustNewConstMetric(metric.desc, metric.valType, metric.extract(jvmUsedMem), []string{containerId, appId, getMarathonName}...)
			}
			ch <- prometheus.MustNewConstMetric(c.upIndicator, prometheus.GaugeValue, 1, []string{containerId, appId, getMarathonName}...)
		}
	}

}

func getAppId(dokcerInfo DockerInfo) string {
	envs := dokcerInfo.DockerConfig.Env
	for _, env := range envs {
		if strings.Contains(env, "MARATHON_APP_ID") {
			length := len(env)
			fi := strings.Index(env, "=") + 1
			appId := string([]byte(env)[fi:length])
			log.Error("get marathon appid", appId)

			return appId
		}
	}
	return ""
}

func getMarathonName(dokcerInfo DockerInfo) string {
	envs := dokcerInfo.DockerConfig.Env
	for _, env := range envs {
		if strings.Contains(env, "MARATHON_NAME") {
			length := len(env)
			fi := strings.Index(env, "=") + 1
			marathonName := string([]byte(env)[fi:length])
			log.Error("get marathon NAME", marathonName)

			return marathonName
		}
	}
	return ""
}

func getThreadMonitorFlag(dokcerInfo DockerInfo) string {
	envs := dokcerInfo.DockerConfig.Env
	for _, env := range envs {
		if strings.Contains(env, "MARATHON_APP_LABEL_THREAD_MONITOR_FLAG") {
			length := len(env)
			fi := strings.Index(env, "=") + 1
			log.Error("get marathon monitor flag")

			return string([]byte(env)[fi:length])
		}
	}
	return ""
}

func getContainerList() (containers []string, err error) {
	cmd := exec.Command("/bin/sh", "-c", `docker ps |awk  '{print $1}'`)
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		log.Fatal(err)
		return nil, err
	}
	defer stdout.Close()
	if err := cmd.Start(); err != nil {
		log.Fatal(err)
		return nil, err
	}
	opBytes, err := ioutil.ReadAll(stdout)
	if err != nil {
		log.Fatal(err)
		return nil, err
	}

	lines := strings.Split(string(opBytes), "\n")
	return lines, nil
}

func getDockerConfig(containerId string) (dockerInfo DockerInfo, err error) {
	log.Error("getThreadMonitorFlag cId:", containerId)
	cmd := exec.Command("docker", "inspect", containerId)
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		log.Fatal(err)
		return DockerInfo{}, err
	}
	defer stdout.Close()
	if err := cmd.Start(); err != nil {
		log.Fatal(err)
		return DockerInfo{}, err
	}
	opBytes, err := ioutil.ReadAll(stdout)
	if err != nil {
		log.Fatal(err)
		return DockerInfo{}, err
	}

	out := string(opBytes)
	log.Error("inspect cId:", containerId)

	fi := strings.Index(out, "{") - 1
	li := strings.LastIndex(out, "}") + 1
	bodyBytes := []byte(out)[fi:li]

	var d DockerInfo
	json.Unmarshal(bodyBytes, &d)

	return d, nil
}

func getThreadInfo(containerId string) (sessions string, threadTotal string, threadIdle string,
	threadStandBy string, threadRunning string, jvmMaxMem string, jvmUsedMem string) {
	cmd := exec.Command("docker", "exec", containerId, "sh", "/app/bin/getThread.sh")
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		log.Fatal(err)
		return "0", "0", "0", "0", "0", "0", "0"
	}
	defer stdout.Close()
	if err := cmd.Start(); err != nil {
		log.Fatal(err)
		return "0", "0", "0", "0", "0", "0", "0"
	}
	opBytes, err := ioutil.ReadAll(stdout)
	if err != nil {
		log.Fatal(err)
		return "0", "0", "0", "0", "0", "0", "0"
	}
	lines := strings.Split(string(opBytes), "\n")
	if len(lines) < 7 {
		return "0", "0", "0", "0", "0", "0", "0"
	}
	return strings.Split(lines[0], ":")[1], strings.Split(lines[1],
			":")[1], strings.Split(lines[2], ":")[1], strings.Split(lines[3], ":")[1], strings.Split(lines[4], ":")[1],
		strings.Split(lines[5], ":")[1], strings.Split(lines[6], ":")[1]
}
