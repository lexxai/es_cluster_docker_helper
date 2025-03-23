## Example of run:

### Logs
```
2025-03-19 02:23:24 [INFO] Running...
2025-03-19 02:23:24 [INFO] Node with role in cluster: 'master', count: 1
2025-03-19 02:23:24 [INFO] Node with role in cluster: 'data', count: 3
2025-03-19 02:23:24 [INFO] Node with role in cluster: 'ingest', count: 2
2025-03-19 02:23:24 [INFO] Node with role in cluster: 'coordinator', count: 1
2025-03-19 02:23:24 [INFO] Total services with nodes roles in cluster: 7
2025-03-19 02:23:24 [INFO] Other additional services is: 'setup, kibana'
2025-03-19 02:23:24 [INFO] Total services for docker compose file: 9
2025-03-19 02:23:25 [INFO] Saved results to 'docker-compose.yml'
```

### docker-compose.yml
```yaml
services:
  kibana:
    cap_drop:
    - ALL
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 8096M
    environment:
    - SERVERNAME=kibana
    - ELASTICSEARCH_HOSTS=es-server-0.example.com:9200
    - ELASTICSEARCH_USERNAME=kibana_system
    - ELASTICSEARCH_PASSWORD=12345678
    - ELASTICSEARCH_SSL_CERTIFICATEAUTHORITIES=config/certs/ca/ca.crt
    healthcheck:
      interval: 10s
      retries: 120
      test:
      - CMD-SHELL
      - curl -s -I http://localhost:5601 | grep -q 'HTTP/1.1 302 Found'
      timeout: 10s
    image: docker.elastic.co/kibana/kibana:8.17.3
    platform: linux/amd64
    ports:
    - 5601:5601
    privileged: false
    restart: unless-stopped
    security_opt:
    - no-new-privileges=true
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: true
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/kibana/config/certs
      type: bind
    - kibanadata:/usr/share/kibana/data
  node_1:
    cap_drop:
    - ALL
    container_name: node_1
    depends_on:
      setup:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 8096M
    environment:
    - node.name=node_1
    - ES_NETWORK_HOST="0.0.0.0,[::]"
    - cluster.name=es-cluster
    - discovery.seed_hosts=es-server-0.example.com:9300
    - cluster.initial_master_nodes=node_1
    - node.roles=master
    - http.port=9200
    - transport.port=9300
    - ELASTIC_PASSWORD=12345678
    - xpack.security.http.ssl.enabled=true
    - xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.http.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.http.ssl.verification_mode=certificate
    - xpack.security.transport.ssl.enabled=true
    - xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.transport.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.transport.ssl.verification_mode=certificate
    - TZ="Etc/UTC"
    - UMASK="002"
    - UMASK_SET="002"
    healthcheck:
      interval: 10s
      retries: 120
      test:
      - CMD-SHELL
      - 'curl --silent --output /dev/null --show-error --fail --cacert config/certs/ca/ca.crt
        --header "Authorization: Basic $(echo -n elastic:12345678 | base64)" https://es-server-0.example.com:9200/_cluster/health?local=true'
      timeout: 10s
    image: elasticsearch:8.17.3
    network_mode: host
    platform: linux/amd64
    privileged: false
    restart: unless-stopped
    security_opt:
    - no-new-privileges=true
    ulimits:
      memlock:
        hard: -1
        soft: -1
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: true
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/elasticsearch/config/certs
      type: bind
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: false
      source: /mnt/mdata/database/es_data/cluster/node_1
      target: /usr/share/elasticsearch/data
      type: bind
  node_2:
    cap_drop:
    - ALL
    container_name: node_2
    depends_on:
      setup:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16384M
    environment:
    - node.name=node_2
    - ES_NETWORK_HOST="0.0.0.0,[::]"
    - cluster.name=es-cluster
    - discovery.seed_hosts=es-server-0.example.com:9300
    - cluster.initial_master_nodes=''
    - node.roles=data
    - http.port=9201
    - transport.port=9301
    - ELASTIC_PASSWORD=12345678
    - xpack.security.http.ssl.enabled=true
    - xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.http.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.http.ssl.verification_mode=certificate
    - xpack.security.transport.ssl.enabled=true
    - xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.transport.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.transport.ssl.verification_mode=certificate
    - TZ="Etc/UTC"
    - UMASK="002"
    - UMASK_SET="002"
    healthcheck:
      interval: 10s
      retries: 120
      test:
      - CMD-SHELL
      - 'curl --silent --output /dev/null --show-error --fail --cacert config/certs/ca/ca.crt
        --header "Authorization: Basic $(echo -n elastic:12345678 | base64)" https://es-server-0.example.com:9201/_cluster/health?local=true'
      timeout: 10s
    image: elasticsearch:8.17.3
    network_mode: host
    platform: linux/amd64
    privileged: false
    restart: unless-stopped
    security_opt:
    - no-new-privileges=true
    ulimits:
      memlock:
        hard: -1
        soft: -1
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: true
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/elasticsearch/config/certs
      type: bind
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: false
      source: /mnt/mdata/database/es_data/cluster/node_2
      target: /usr/share/elasticsearch/data
      type: bind
  node_3:
    cap_drop:
    - ALL
    container_name: node_3
    depends_on:
      setup:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16384M
    environment:
    - node.name=node_3
    - ES_NETWORK_HOST="0.0.0.0,[::]"
    - cluster.name=es-cluster
    - discovery.seed_hosts=es-server-0.example.com:9300
    - cluster.initial_master_nodes=''
    - node.roles=data
    - http.port=9202
    - transport.port=9302
    - ELASTIC_PASSWORD=12345678
    - xpack.security.http.ssl.enabled=true
    - xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.http.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.http.ssl.verification_mode=certificate
    - xpack.security.transport.ssl.enabled=true
    - xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.transport.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.transport.ssl.verification_mode=certificate
    - TZ="Etc/UTC"
    - UMASK="002"
    - UMASK_SET="002"
    healthcheck:
      interval: 10s
      retries: 120
      test:
      - CMD-SHELL
      - 'curl --silent --output /dev/null --show-error --fail --cacert config/certs/ca/ca.crt
        --header "Authorization: Basic $(echo -n elastic:12345678 | base64)" https://es-server-0.example.com:9202/_cluster/health?local=true'
      timeout: 10s
    image: elasticsearch:8.17.3
    network_mode: host
    platform: linux/amd64
    privileged: false
    restart: unless-stopped
    security_opt:
    - no-new-privileges=true
    ulimits:
      memlock:
        hard: -1
        soft: -1
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: true
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/elasticsearch/config/certs
      type: bind
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: false
      source: /mnt/mdata/database/es_data/cluster/node_3
      target: /usr/share/elasticsearch/data
      type: bind
  node_4:
    cap_drop:
    - ALL
    container_name: node_4
    depends_on:
      setup:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16384M
    environment:
    - node.name=node_4
    - ES_NETWORK_HOST="0.0.0.0,[::]"
    - cluster.name=es-cluster
    - discovery.seed_hosts=es-server-0.example.com:9300
    - cluster.initial_master_nodes=''
    - node.roles=data
    - http.port=9203
    - transport.port=9303
    - ELASTIC_PASSWORD=12345678
    - xpack.security.http.ssl.enabled=true
    - xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.http.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.http.ssl.verification_mode=certificate
    - xpack.security.transport.ssl.enabled=true
    - xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.transport.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.transport.ssl.verification_mode=certificate
    - TZ="Etc/UTC"
    - UMASK="002"
    - UMASK_SET="002"
    healthcheck:
      interval: 10s
      retries: 120
      test:
      - CMD-SHELL
      - 'curl --silent --output /dev/null --show-error --fail --cacert config/certs/ca/ca.crt
        --header "Authorization: Basic $(echo -n elastic:12345678 | base64)" https://es-server-0.example.com:9203/_cluster/health?local=true'
      timeout: 10s
    image: elasticsearch:8.17.3
    network_mode: host
    platform: linux/amd64
    privileged: false
    restart: unless-stopped
    security_opt:
    - no-new-privileges=true
    ulimits:
      memlock:
        hard: -1
        soft: -1
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: true
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/elasticsearch/config/certs
      type: bind
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: false
      source: /mnt/mdata/database/es_data/cluster/node_4
      target: /usr/share/elasticsearch/data
      type: bind
  node_5:
    cap_drop:
    - ALL
    container_name: node_5
    depends_on:
      setup:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '16'
          memory: 16384M
    environment:
    - node.name=node_5
    - ES_NETWORK_HOST="0.0.0.0,[::]"
    - cluster.name=es-cluster
    - discovery.seed_hosts=es-server-0.example.com:9300
    - cluster.initial_master_nodes=''
    - node.roles=ingest
    - http.port=9204
    - transport.port=9304
    - ELASTIC_PASSWORD=12345678
    - xpack.security.http.ssl.enabled=true
    - xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.http.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.http.ssl.verification_mode=certificate
    - xpack.security.transport.ssl.enabled=true
    - xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.transport.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.transport.ssl.verification_mode=certificate
    - TZ="Etc/UTC"
    - UMASK="002"
    - UMASK_SET="002"
    healthcheck:
      interval: 10s
      retries: 120
      test:
      - CMD-SHELL
      - 'curl --silent --output /dev/null --show-error --fail --cacert config/certs/ca/ca.crt
        --header "Authorization: Basic $(echo -n elastic:12345678 | base64)" https://es-server-0.example.com:9204/_cluster/health?local=true'
      timeout: 10s
    image: elasticsearch:8.17.3
    network_mode: host
    platform: linux/amd64
    privileged: false
    restart: unless-stopped
    security_opt:
    - no-new-privileges=true
    ulimits:
      memlock:
        hard: -1
        soft: -1
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: true
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/elasticsearch/config/certs
      type: bind
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: false
      source: /mnt/mdata/database/es_data/cluster/node_5
      target: /usr/share/elasticsearch/data
      type: bind
  node_6:
    cap_drop:
    - ALL
    container_name: node_6
    depends_on:
      setup:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '16'
          memory: 16384M
    environment:
    - node.name=node_6
    - ES_NETWORK_HOST="0.0.0.0,[::]"
    - cluster.name=es-cluster
    - discovery.seed_hosts=es-server-0.example.com:9300
    - cluster.initial_master_nodes=''
    - node.roles=ingest
    - http.port=9205
    - transport.port=9305
    - ELASTIC_PASSWORD=12345678
    - xpack.security.http.ssl.enabled=true
    - xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.http.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.http.ssl.verification_mode=certificate
    - xpack.security.transport.ssl.enabled=true
    - xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.transport.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.transport.ssl.verification_mode=certificate
    - TZ="Etc/UTC"
    - UMASK="002"
    - UMASK_SET="002"
    healthcheck:
      interval: 10s
      retries: 120
      test:
      - CMD-SHELL
      - 'curl --silent --output /dev/null --show-error --fail --cacert config/certs/ca/ca.crt
        --header "Authorization: Basic $(echo -n elastic:12345678 | base64)" https://es-server-0.example.com:9205/_cluster/health?local=true'
      timeout: 10s
    image: elasticsearch:8.17.3
    network_mode: host
    platform: linux/amd64
    privileged: false
    restart: unless-stopped
    security_opt:
    - no-new-privileges=true
    ulimits:
      memlock:
        hard: -1
        soft: -1
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: true
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/elasticsearch/config/certs
      type: bind
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: false
      source: /mnt/mdata/database/es_data/cluster/node_6
      target: /usr/share/elasticsearch/data
      type: bind
  node_7:
    cap_drop:
    - ALL
    container_name: node_7
    depends_on:
      setup:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16384M
    environment:
    - node.name=node_7
    - ES_NETWORK_HOST="0.0.0.0,[::]"
    - cluster.name=es-cluster
    - discovery.seed_hosts=es-server-0.example.com:9300
    - cluster.initial_master_nodes=''
    - node.roles=[]
    - http.port=9206
    - transport.port=9306
    - ELASTIC_PASSWORD=12345678
    - xpack.security.http.ssl.enabled=true
    - xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.http.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.http.ssl.verification_mode=certificate
    - xpack.security.transport.ssl.enabled=true
    - xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.key
    - xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/es-server-0.example.com/es-server-0.example.com.crt
    - xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca/ca.crt
    - xpack.security.transport.ssl.supported_protocols="TLSv1.2,TLSv1.3"
    - xpack.security.transport.ssl.verification_mode=certificate
    - TZ="Etc/UTC"
    - UMASK="002"
    - UMASK_SET="002"
    healthcheck:
      interval: 10s
      retries: 120
      test:
      - CMD-SHELL
      - 'curl --silent --output /dev/null --show-error --fail --cacert config/certs/ca/ca.crt
        --header "Authorization: Basic $(echo -n elastic:12345678 | base64)" https://es-server-0.example.com:9206/_cluster/health?local=true'
      timeout: 10s
    image: elasticsearch:8.17.3
    network_mode: host
    platform: linux/amd64
    privileged: false
    restart: unless-stopped
    security_opt:
    - no-new-privileges=true
    ulimits:
      memlock:
        hard: -1
        soft: -1
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: true
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/elasticsearch/config/certs
      type: bind
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: false
      source: /mnt/mdata/database/es_data/cluster/node_7
      target: /usr/share/elasticsearch/data
      type: bind
  setup:
    command: "bash -c 'if [ x12345678 == x ]; then\n    echo \"Set the ELASTIC_PASSWORD\
      \ environment variable in the .env file\";\n    exit 1;\n  elif [ x12345678\
      \ == x ]; then\n    echo \"Set the KIBANA_PASSWORD environment variable in the\
      \ .env file\";\n    exit 1;\n  fi;\n  if [ ! -f config/certs/ca.zip ]; then\n\
      \    echo \"Creating CA\";\n    bin/elasticsearch-certutil ca --silent --pem\
      \ -out config/certs/ca.zip;\n    unzip config/certs/ca.zip -d config/certs;\n\
      \  fi;\n  if [ ! -f config/certs/certs.zip ]; then\n    echo \"Creating certs\"\
      ;\n    echo -ne \\\n    \"instances:\\n\"\\\n    \"- name: es-server-0.example.com\\\
      n\"\\\n    \"  dns:\\n\"\\\n    \"  - es-server-0.example.com\\n\"\\\n    \"\
      \  - localhost\\n\"\\\n    \"  ip:\\n\"\\\n    \"  - 10.1.10.1\\n\"\\\n    \"\
      \  - 127.0.0.1\\n\"\\\n    > config/certs/instances.yml;\n    bin/elasticsearch-certutil\
      \ cert --silent --pem -out config/certs/certs.zip --in config/certs/instances.yml\
      \ --ca-cert config/certs/ca/ca.crt --ca-key config/certs/ca/ca.key;\n    unzip\
      \ config/certs/certs.zip -d config/certs;\n  fi;\n  echo \"Waiting for Elasticsearch\
      \ availability\";\n  until curl -s --cacert config/certs/ca/ca.crt https://es-server-0.example.com:9200\
      \ | grep -q \"missing authentication credentials\"; do sleep 30; done;\n  echo\
      \ \"Setting kibana_system password\";\n  until curl -s -X POST --cacert config/certs/ca/ca.crt\
      \ -u \"elastic:12345678\" -H \"Content-Type: application/json\" https://es-server-0.example.com:9200/_security/user/kibana_system/_password\
      \ -d \"{\\\"password\\\":\\\"12345678\\\"}\" | grep -q \"^{}\"; do sleep 10;\
      \ done;\n  echo \"All done!\";'\n"
    healthcheck:
      interval: 1s
      retries: 120
      test:
      - CMD-SHELL
      - '[ -f config/certs/es-server-0.example.com/es-server-0.example.com.crt ]'
      timeout: 5s
    image: elasticsearch:8.17.3
    user: 1000:1000
    volumes:
    - bind:
        create_host_path: false
        propagation: rprivate
      read_only: false
      source: /mnt/mdata/database/es_data/cluster/certs
      target: /usr/share/elasticsearch/config/certs
      type: bind
volumes:
  kibanadata:
    driver: local
```

### services-resources.yml
```yaml
services:
  node-master:
    limits:
      cpu: "8"
      memory: "8096M"
  node-data:
    limits:
      cpu: "8"
      memory: "16384M"
  node-ingest:
    limits:
      cpu: "16"
      memory: "16384M"
  node-coordinator:
    limits:
      cpu: "8"
      memory: "16384M"
  node-data_ingest:
    limits:
      cpu: "16"
      memory: "24384M"      
  node-master_data_ingest:
    limits:
      cpu: "32"
      memory: "64000M"
  node-master_data:
    limits:
      cpu: "16"
      memory: "32768M"      
  setup:
    limits:
      cpu: "1"
      memory: "2048M"
  kibana:
    limits:
      cpu: "8"
      memory: "8096M"
```