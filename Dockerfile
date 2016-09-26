FROM centos:7

RUN yum -y update && yum clean all
RUN yum -y install epel-release
RUN yum -y install net-tools
RUN yum install -y \
        python-pip \
        python-requests\
        python-bottle\
        python-gevent\
        mysql-connector-python
RUN  mkdir /opt/conf_query
COPY conf_query /opt/conf_query/
RUN chmod +x /opt/conf_query/start_server.sh

ENTRYPOINT ["bash", "/opt/conf_query/start_server.sh"]
