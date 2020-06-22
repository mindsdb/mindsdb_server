FROM mariadb:10.3

RUN apt update && apt install openjdk-8-jdk -y && export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64

RUN apt update
RUN apt-get install software-properties-common -y

RUN apt-key adv --fetch-keys "https://mariadb.org/mariadb_release_signing_key.asc"

RUN add-apt-repository 'deb [arch=amd64,arm64,ppc64el] http://mirror.host.ag/mariadb/repo/10.3/ubuntu bionic main'

RUN apt update

RUN apt-get install mariadb-plugin-connect -y

COPY ./jars/wrapper/* /usr/lib/mysql/plugin/

COPY ./jars/jdbc/* /usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/

COPY ./jars/jdbc/* /usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/

RUN chmod 0444 /etc/mysql/mariadb.conf.d/connect.cnf

VOLUME /var/lib/mysql

EXPOSE 3306

CMD [“mysqld”]
