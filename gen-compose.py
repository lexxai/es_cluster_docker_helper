import logging
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
import os
import re

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


class NodeRoles(StrEnum):
    master = "master"
    data = "data"
    ingest = "ingest"
    coordinator = "[]"
    data_ingest = "data,ingest"
    master_data_ingest = "master,data,ingest"
    master_data = "master,data"


@dataclass
class Defaults:
    base_folder = "templates"
    output_file = "docker-compose.yml"
    templates = {
        "base": "docker-compose-es.template.yml",
        "kibana": "docker-compose-es-kibana.template.yml",
        "node": "docker-compose-es-node.template.yml",
        "setup": "docker-compose-es-setup.template.yml",
        "services-resources": "services-resources.yml",
    }
    docker_services = "setup:1,node-master:1,node-data:5,node-ingest:3,kibana:1"
    node_prefix_name = "node-"
    node_name_template = "node-{id}"


class ElasticSearchClusterComposeGenerator:

    def __init__(self, options: dict[str, Any]):
        base_folder = options.get("base_folder", Defaults.base_folder)
        self.output_file = Path(options.get("output_file", Defaults.output_file))
        self.templates = options.get("templates", {})
        for key, value in Defaults.templates.items():
            value = self.templates.get(key, value)
            self.templates[key] = Path(base_folder).joinpath(value)

        self.docker_services: dict[str, int] = self.decode_docker_services(
            options.get("docker_services", Defaults.docker_services)
        )

        self.roles_resources = self.load_template(
            self.templates.get("services-resources")
        )
        assert self.roles_resources, "Must be defined resources..."
        self.node_name_template = os.environ.get(
            "NODE_NAME_TEMPLATE", Defaults.node_name_template
        )
        self.node_prefix_name = Defaults.node_prefix_name
        self.service_preprocessor_map = {"setup": self.preprocessor_setup}

    def get_service_limits(self, service_name: str, return_limits: bool = True) -> dict:
        r = self.roles_resources.get("services", {}).get(service_name, {})
        return r.get("limits", {}) if return_limits else r

    def count_services(self):
        return sum(self.docker_services.values())

    def count_node_services(self):
        return sum(
            (
                v
                for k, v in self.docker_services.items()
                if self.get_service_node_role(k)
            )
        )

    def count_node_services_by_role(self, role: str = NodeRoles.master) -> int:
        return sum(
            [
                v
                for k, v in self.docker_services.items()
                if (self.get_service_node_role(k) == role)
            ]
        )

    def get_service_node_role(self, service_name: str) -> None | str:
        s_name = service_name.lower()
        if not s_name.startswith(self.node_prefix_name):
            return None
        return s_name.split("-", 1)[1]

    @staticmethod
    def decode_docker_services(config: str) -> dict[str, int]:
        services = config.strip().split(",")
        r = {}
        for service in services:
            k = service.split(":")[0].strip()
            try:
                v = int(service.split(":")[1].strip())
                v = v if v > 0 else 1
                r[k] = v
            except ValueError:
                logger.error(f"Failed to parse docker_services: {k}")
                continue
        return r

    def get_roles(self):
        return self.roles_resources.get("roles", {})

    @staticmethod
    def replace_env_vars(yaml_data):
        """
        Replaces environment variables in a YAML structure with their actual values.

        Args:
            yaml_data: The loaded YAML data (dictionary or list).

        Returns:
            The YAML data with environment variables replaced.
        """

        def replace_in_value(value):
            if isinstance(value, str):
                # Find environment variables using regex
                matches = re.findall(
                    r"\${(\w+)(?::([^}]*))?}", value
                )  # Matches ${VAR} and ${VAR:default}
                for match in matches:
                    var_name, default_value = match
                    env_value = os.environ.get(var_name, default_value)
                    if env_value is None:
                        raise ValueError(
                            f"Environment variable '{var_name}' not found and no default provided."
                        )
                    value = value.replace(
                        f"${{{var_name}{':' + default_value if default_value else ''}}}",
                        env_value,
                    )
                return value
            return value

        def process_item(item):
            if isinstance(item, dict):
                return {replace_in_value(k): process_item(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [process_item(i) for i in item]
            else:
                return replace_in_value(item)

        return process_item(yaml_data)

    @staticmethod
    def load_template(template_file_path: Path) -> Any | None:
        try:
            with template_file_path.open() as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Error: Template file '{template_file_path.name}' not found.")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
        except ValueError as e:
            logger.error(f"Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    def save_template(self, template: dict, output_file_path: Path = None):
        if output_file_path is None:
            output_file_path = self.output_file
            assert output_file_path, "Must be defined"
        try:
            with output_file_path.open("w+") as f:
                yaml.dump(template, f)
            logger.info(f"Saved results to '{output_file_path.name}'")
        except FileNotFoundError:
            logger.error(f"Error: Template file '{output_file_path.name}' not found.")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
        except ValueError as e:
            logger.error(f"Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    def build_node(self, build_options) -> dict:
        template_node: dict = build_options["template_node"]
        node_name: str = build_options["node_name"]
        node_roles: str = build_options["node_roles"]
        node_id: int = build_options["node_id"]

        os.environ["NODE_NAME"] = node_name
        os.environ["NODE_ROLES"] = node_roles
        os.environ["DATA_PATH"] = os.environ.get(
            "NODE_DATA_DIR_TEMPLATE", "/mnt/data/{node_name}"
        ).format(node_name=node_name)

        os.environ["CPU_LIMIT"] = build_options.get("CPU_LIMIT", "1")
        os.environ["MEMORY_LIMIT"] = build_options.get("MEMORY_LIMIT", "4096M")
        transport_port = int(os.environ.get("NODE_START_TRANSPORT_PORT", 9300)) + (
            node_id - 1
        )
        http_port = int(os.environ.get("NODE_START_HTTP_PORT", 9200)) + (node_id - 1)
        os.environ["TRANSPORT_PORT"] = str(transport_port)
        os.environ["HTTP_PORT"] = str(http_port)
        if (
            node_roles == "data"
            or os.environ.get("CLUSTER_CONFIGURED", "false").strip().lower() == "true"
        ):
            os.environ["MASTER_NODES"] = "[]"

        template_node = self.add_dependency(template_node)
        result = self.replace_env_vars(template_node)

        del os.environ["NODE_NAME"]
        del os.environ["NODE_ROLES"]
        del os.environ["DATA_PATH"]
        del os.environ["CPU_LIMIT"]
        del os.environ["MEMORY_LIMIT"]
        del os.environ["TRANSPORT_PORT"]
        del os.environ["HTTP_PORT"]
        return result

    def gen_seed_hosts(self, nodes: int) -> str:
        NODE_DNS_NAME = os.environ.get("NODE_DNS_NAME", "example.com")
        NODE_START_TRANSPORT_PORT = int(
            os.environ.get("NODE_START_TRANSPORT_PORT", 9300)
        )
        cluster_seeds: list[str] = (
            os.environ.get("NODE_CLUSTER_SEEDS", "").strip().split(",")
        )
        seed_hosts = cluster_seeds if (cluster_seeds and cluster_seeds[0]) else []
        for i in range(0, nodes):
            host = NODE_DNS_NAME
            transport_port = NODE_START_TRANSPORT_PORT + i
            seed_hosts.append(f"{host}:{transport_port}")
        return ",".join(set(seed_hosts))

    def gen_initial_master_nodes(self, node_id: int = 1) -> str:
        node_name = self.node_name_template.format(id=node_id)
        cluster_initial_master_nodes = (
            os.environ.get("NODE_CLUSTER_INITIAL_MASTER_NODES", "").strip().split(",")
        )
        initial_master_nodes: list[str] = (
            cluster_initial_master_nodes
            if (cluster_initial_master_nodes and cluster_initial_master_nodes[0])
            else []
        )
        initial_master_nodes.append(node_name)
        return ",".join(initial_master_nodes)

    def add_dependency(self, template: dict) -> dict:
        is_setup = "setup" in self.docker_services and (
            "setup" not in template.get("services", {})
        )
        if is_setup:
            depends_on = {"setup": {"condition": "service_healthy"}}
            for node in template.get("services"):
                template["services"][node].setdefault("depends_on", {}).update(
                    depends_on
                )
        return template

    def operate_with_node_service(
        self, service: str, template: dict, node_id: int, roles: str
    ):
        node_name: str = self.node_name_template.format(id=node_id)
        service_limits: dict = self.get_service_limits(service)
        build_options = {
            "node_id": node_id,
            "template_node": template,
            "node_name": node_name,
            "node_roles": roles,
            "CPU_LIMIT": service_limits.get("cpu", "1"),
            "MEMORY_LIMIT": service_limits.get("memory", "4096M"),
            "ES_HEAP_SIZE": service_limits.get("heap", "2Gi"),
        }
        return self.build_node(build_options)

    @staticmethod
    def get_node_roles(node_role):
        return NodeRoles.__members__.get(node_role)

    @staticmethod
    def preprocessor_setup(template: dict) -> dict:
        node_ips = os.environ.get("NODE_IPS")
        if node_ips:
            node_ips = node_ips.replace("[", "").replace("]", "")
            ips = node_ips.strip().split(",")
            result = "\n   - ".join(ips)
            os.environ["NODE_IP"] = result
            # logger.debug(f"preprocessor_setup: {result=}")
        return template

    def service_preprocessors(self, service: str, template: dict) -> dict:
        service_funct = self.service_preprocessor_map.get(service)
        if callable(service_funct):
            return service_funct(template)
        return template

    def operate_with_service(self, service: str, template: dict) -> dict:
        service_limits: dict = self.get_service_limits(service)

        build_options = {
            "template": self.service_preprocessors(service, template),
            "CPU_LIMIT": service_limits.get("cpu", "1"),
            "MEMORY_LIMIT": service_limits.get("memory", "512M"),
        }
        return self.build_service(build_options)

    def build_service(self, build_options: dict) -> dict:
        # PUSH ENV
        for key, value in build_options.items():
            if key[0].isupper():
                os.environ[key] = value

        template = build_options.get("template")
        template = self.add_dependency(template)

        result = self.replace_env_vars(template)

        # POP ENV
        for key, value in build_options.items():
            if key[0].isupper():
                del os.environ[key]

        return result

    def log_cluster_info(self):
        total = 0
        total_nodes = 0
        services = []
        for service_name, count_service in self.docker_services.items():
            role = self.get_service_node_role(service_name)
            if role:
                logger.info(
                    f"Node with role in cluster: '{role}', count: {count_service}"
                )
                total_nodes += count_service
            else:
                services.append(service_name)
            total += count_service
        logger.info(f"Total services with nodes roles in cluster: {total_nodes}")
        logger.info(f"Other additional services is: '{', '.join(services)}'")
        logger.info(f"Total services for docker compose file: {total}")

    def run(
        self,
    ):
        logger.info("Running...")
        self.log_cluster_info()
        template_node: dict | None = None
        node_id = 1
        services = []
        nodes = []
        total_master_nodes = self.count_node_services_by_role(NodeRoles.master)

        os.environ["SEED_HOSTS"] = self.gen_seed_hosts(total_master_nodes)
        os.environ["MASTER_NODES"] = self.gen_initial_master_nodes(total_master_nodes)
        os.environ["MASTER_NODE"] = os.environ["MASTER_NODES"].split(",")[0]

        for service, service_count in self.docker_services.items():
            node_role = self.get_service_node_role(service)
            if node_role:
                # Service is a node
                if not template_node:
                    template_node = self.load_template(self.templates.get("node"))
                    assert template_node, "Must be loaded template"
                roles = self.get_node_roles(node_role)
                for i in range(service_count):
                    nodes.append(
                        self.operate_with_node_service(
                            service, template_node, node_id, roles
                        )
                    )
                    node_id += 1
            else:
                # Service is not a node
                template_service: dict = self.load_template(self.templates.get(service))
                services.append(self.operate_with_service(service, template_service))

        base_template = self.load_template(self.templates.get("base"))
        processed_yaml = self.replace_env_vars(base_template) if base_template else {}
        for node in nodes:
            p_services = processed_yaml.setdefault("services", {})
            p_services.update(node.get("services", {}))

        for service in services:
            for key in service.keys():
                p_services = processed_yaml.setdefault(key, {})
                p_services.update(service.get(key, {}))

        self.save_template(processed_yaml)


if __name__ == "__main__":

    docker_services = os.environ.get("DOCKER_SERVICES", Defaults.docker_services)
    options = {
        "docker_services": docker_services,
    }
    ElasticSearchClusterComposeGenerator(options).run()
