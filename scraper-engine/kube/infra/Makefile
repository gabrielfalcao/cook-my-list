K8S_NAMESPACE	:= ci-butler-data
HELM_INSTALL	:= helm upgrade -i --reuse-values --namespace $(K8S_NAMESPACE)
HELM_UNINSTALL	:= helm uninstall --namespace $(K8S_NAMESPACE)
K8S_MAX_LOG_REQUESTS	:= 100

kibana-ingress:
	kubectl apply --namespace $(K8S_NAMESPACE) -f kibana.yml

deploy-kibana: kibana-ingress
	-$(HELM_INSTALL) kibana --version 7.13.2 elastic/kibana

deploy-elasticsearch:
	helm repo update
	-$(HELM_INSTALL) elasticsearch --version 7.13.2 elastic/elasticsearch


deploy-postgres:
	-$(HELM_INSTALL) postgres bitnami/postgresql-ha -f values/postgres-ha.yml


deploy:
	helm repo update
	$(MAKE) deploy-elasticsearch deploy-kibana deploy-postgres

helm-repos:
	helm repo add elastic https://helm.elastic.co
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo update


undeploy:
	$(HELM_UNINSTALL) postgres
	$(HELM_UNINSTALL) elasticsearch
	$(HELM_UNINSTALL) kibana


k9s:
	-@iterm2 name data 🌩 && iterm2 color purple 3
	k9s -n $(K8S_NAMESPACE)


k8s-delete-ns:
	kubectl delete ns $(K8S_NAMESPACE)
	$(MAKE) k8s-resources

k8s-create-ns:
	kubectl create ns $(K8S_NAMESPACE)
	$(MAKE) k8s-resources

k8s-resources:
	kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl -n $(K8S_NAMESPACE) get --show-kind --ignore-not-found -n $(K8S_NAMESPACE)

k8s-shell-elasticsearch:
	 kubectl -n $(K8S_NAMESPACE) exec -ti service/elasticsearch-master -- bash

k8s-shell-kibana:
	 kubectl -n $(K8S_NAMESPACE) exec -ti service/kibana -- bash

pod-logs-elasticsearch:
	kubectl -n $(K8S_NAMESPACE) logs --max-log-requests $(K8S_MAX_LOG_REQUESTS) --prefix --ignore-errors -l 'chart=elasticsearch' -f --all-containers

pod-logs-kibana:
	kubectl -n $(K8S_NAMESPACE) logs --max-log-requests $(K8S_MAX_LOG_REQUESTS) --prefix --ignore-errors -l 'chart=kibana' -f --all-containers
