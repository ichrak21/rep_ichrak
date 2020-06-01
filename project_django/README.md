# Référentiel V2

## Contexte

Reprise du projet référentiel V1 afin de réaliser une mise à jour technologique
et de normaliser les API.

Utilisation de Django et Python3.7 cf.[requirements](/requirements.txt) ou [Pipfile](/Pipfile)

L'arrivé du développeur Python a vu l'objectif s'élargir à l'intégration de
l'application dans Kubernetes.

### Objectifs du PoC

* Démontrer qu'il est possible de développer des applications de qualités rapidement en maitrisant les coûts
* Démontrer la capacité de l'application à évoluer rapidement afin de mieux maitriser la dette technique
* Mettre en place un socle de bonnes pratiques pour les futurs applications 
* Maitrise la mise en place d'un environnement de développement (Setup d'un poste de développeur)
* Déployer l'application sur un environnement Kubernetes cf. [deployment.yaml](/deployment.yaml)

## Installation

Le déploiement est réalisé via gitlab-ci. cf.
[.gitlab-ci.yml](.gitlab-ci.yml) pour le détail de l'installation.

Les variables à initialiser au niveau de gitlab sont les suivantes :

* REGISTRY_USER : login du registry 
* REGISTRY_PASS : mot de passe associé
* REGISTRY_HOST : host du registry
* DJANGO_ADMIN_LOGIN : identifiant du compte administrateur à créer à l'installation de django
* DJANGO_ADMIN_PASSWORD : mot de passe à initialiser
* DJANGO_ADMIN_MAIL : courrier à utiliser pour le compte admin

## Pré-requis système

### Dans le cas de l'utilisation de docker-compose

Dans le cas du déploiement de l'application via un docker compose
"classique". Les pré-requis pour une installation à partir d'Ubuntu 18.04 LTS
sont disponibles dans le `playbook/install.yml` ansible.

Pour lancer l'installation des pré-requis se placer dans le répertoire
`playbook` vérifier la configuration du fichier `hosts`, puis lancer : 

```bash
ansible-playbook -i hosts --ask-become-pass --ask-pass install.yml
```
#### Exception rencontré sur un environnement de développement local Fedora 30

psycopg2 utilise `libcrypt.so.1`, inexistant sur Fedora 30, le contournement :

```bash
sudo ln -s /usr/lib64/libcrypt.so /usr/lib64/libcrypt.so.1
```

### Dans le cas de l'utilisation de Kubernetes

Disposer d'un accès à un cluster K8S

## Kubernetes

### Accéder aux pods

* Installer le binaire `kubectl` sur votre environnement
* Configurer le fichier [].kube/config]

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: #A DEMANDER AUX PROPRIETAIRES DE L'ENVIRONNEMENT
    server: #A DEMANDER AUX PROPRIETAIRES DE L'ENVIRONNEMENT
  name: kube
contexts:
- context:
    cluster: kube
    user: referential-dev-account
  name: kube-log
current-context: kube-log
kind: Config
preferences: {}
users:
- name: referential-dev-account
  user:
    token: #A DEMANDER AUX PROPRIETAIRES DE L'ENVIRONNEMENT
```

* Utiliser ne le **namespace** *referential-dev* en arguments de `kubectl`, par exemple :
```bash
kubectl get pods --namespace referential-dev
kubectl logs referentiels-deployment-5f7b8c9976-kd8m6  --namespace referential-dev
```

### Quelques définitions 

* pod : encapsule un ou plusieurs conteneurs, ils sont ephémères comme les conteneurs.
* service : défini une politique d'accès aux pods pour [les services ou micro-services](https://kubernetes.io/docs/concepts/services-networking/service/)
* deployment : décrit un état attendu des controlleurs : [pods, replica, scalabilité, etc.](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
* namespace : cluster virtuel pour définir des quotas et séparer les rôles entre les équipes et les projets [à partir d'une dizaine de clusters selon K8S](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)


### Le fichier [deployment.yaml](/deployment.yaml)

Version de l'API K8S et définition du namespace :
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: referential-dev
```

Création du service frontal, avec le label `rbac.authorization.k8s.io`,
[RBAC : Role-Based Access Control](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
Le type **LoadBalancer** indique que le cluster est [exposé sur internet](
https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)
Le pod ciblé porte le label **django-app**.
```yaml
kind: Service
apiVersion: v1
metadata:
  name: example-loadbalancer-service
  namespace: referential-dev
  labels: 
    rbac.authorization.k8s.io/aggregate-to-admin: "true" 
spec:
  selector:
    app: django-app
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

Création du déploiement et donc définition du pod portant le label
**django-app**. Toujours dans le **namespace** *referential-dev*.

La [strategy](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy) 
de remplacement des pods est celle par défaut : `RollingUpdate`. L'option
`maxUnavailable` précise le nombre maximum de pod qui peuvent être
indisponible.

`Selector` cible le(s)s pod(s) à manager définit dans le champ `template`.

```yaml
apiVersion: apps/v1 # for versions before 1.9.0 use apps/v1beta2
kind: Deployment
metadata:
  name: referentiels-deployment
  namespace: referential-dev
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  selector:
    matchLabels:
      app: django-app
  replicas: 2 # tells deployment to run 2 pods matching the template
```

Définition du/des pods, on retrouve bien **django-app**. La partie [affinity](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) définit les liens entre les pods.
[imagePullSecrets](https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod) sécurise l'accès au registre (seul les pods avec le secret peuvent accéder au registre)

```yaml
  template:
    metadata:
      labels:
        app: django-app
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - nginx
              topologyKey: "kubernetes.io/hostname"
      containers:
      - name: referentiel-v2
        image: ccireferential.azurecr.io/referentiels/v2:latest
        ports:
          - containerPort: 8000
        command: ['bash', 'init_server.sh']
        imagePullPolicy: Always
      imagePullSecrets:
        - name: regcred
```

La suite du fichier définit un job qui lance le fichier [update_db.sh](/update_db.sh)
[backoffLimit](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/#pod-backoff-failure-policy) précise le nombre de tentative avant d'arrêter le [job](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/)
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: referential-job
spec:
  template:
    spec:
      containers:
      - name: referential-job
        image: ccireferential.azurecr.io/referentiels/v2:latest
        command: ['bash', 'update_db.sh']
      restartPolicy: Never
      imagePullSecrets:
        - name: regcred
  backoffLimit: 4
```

La partie suivante définit les [roles](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#role-and-clusterrole) pour le **namespace** *referential-dev* et donc les accès aux [ressources](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#referring-to-resources)
```yaml
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: referential-dev
  name: log-manager
rules:
- apiGroups: ["", "extensions", "apps", "batch"]
  resources: ["deployments", "replicasets", "pods", "jobs","pods/log","pods/status"]
  verbs: ["get", "list", "watch"]
```

Applique les rôles à [un utilisateur ou à un ensemble d'utilisateur](
  https://kubernetes.io/docs/reference/access-authn-authz/rbac/#rolebinding-and-clusterrolebinding)
```yaml
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: deployment-manager-binding
  namespace: referential-dev
subjects:
- kind: ServiceAccount
  name: referential-dev-account
  apiGroup: ""
roleRef:
  kind: Role
  name: log-manager
  apiGroup: rbac.authorization.k8s.io
```

## Initialisation du projet

Mise en place d'un environnement de travail local

Installer : python3.7 et pip, puis utiliser un environnement de développement local

```bash
pip install pipenv
pipenv install --skip-lock
```
L'option `--skip-lock` outrepasse la génération du fichier `Pipefile.lock`, qui
permet de conserver la version des packages installés afin d'éviter une mise à
jour de package malencontreuse :

*The Pipfile.lock is intended to specify, based on the packages present in
Pipfile, which specific version of those should be used, avoiding the risks of
automatically upgrading packages that depend upon each other and breaking your
project dependency tree.*

Si vous utilisez powerline (https://github.com/powerline/powerline) :

```bash
pip install -r powerline-requirements.txt
```

Instancier une application :
```bash
django-admin startproject referentiels
cd referentiels
django-admin startapp api
```

Initialiser la base :
```bash
python manage.py makemigrations
python manage.py createsuperuser --email admin@example.com --username admin
python manage.py migrate
```
## Lancer les tests unitaires

Constuire l'image :
```bash
docker build -t referentielsv2 .
```

Lancer les tests via l'image :
```bash
docker run --rm referentielsv2 python manage.py test
```

## Base de données

Le **playbook** ansible : `playbook/update_data.yml` appelle les méthodes de peuplement de la base à partir des fichiers intégrés dans l'image Docker.

Avant de le lancer vérifier le fichier d'inventaire **hosts** puis l'exécution du playbook se lance de la façon suivante :
```bash
ansible-playbook -i hosts -e ref_env=test --ask-pass update_data.yml
```
La variable ref_env doit correspondre à celle définit dans le fichier **.env**

## TODO 

* [ ] réalisation du filtrage (recherche) / Interface de recherche (quels critères)
* [ ] test unitaires à finaliser
* [ ] Créer des appels unitaires pour chaque référentiel (ex : obtenir une commune par son id, son code, son libellé?)
* [x] Versionning des données (utilisation Django ?)
* [x] Intégration fichiers externes
* [ ] Mettre à disposition des fichiers consolidés (csv, gestion des version, appel WS)
* [ ] Tests de montée en charge / Replication
* [ ] Documenter packaging Kubernetes
* [ ] Gérer les environnements K8S dans le fichier de [déploiement](./deployment.yaml) K8S
* [ ] Corriger l'utilisation de variables dans le fichier [.gitlab-ci.yml](.gitlab-ci.yml)



## Documentation

* https://www.django-rest-framework.org/
* https://django-reversion.readthedocs.io/en/stable/
* https://django-import-export.readthedocs.io/en/stable/
* https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html

Pour la gestion des révisions il est possible de créer des révisions
manuellement :
https://django-reversion.readthedocs.io/en/latest/commands.html#createinitialrevisions

par exemple :
```bash
python manage.py createinitialrevisions api.CFE --comment="Version initiale"
```

Il est donc possible de créer une version lors du chargement de fichier CSV en amont de l'import.


## Exemple de requete 

Prérequis : application fonctionnant en local.

Dossier requests_examples

Scripts Python:
* check_token.py : obtenir réponse serveur si Token valide / non valide
* create_cfe.py : génère 10 CFE / POST 
* get_cfe_list.py : print liste CFE / GET

## Test de charge

3 minimums, 10 max 
--pod-eviction-timeout duration 


## 
* tolérance à la panne
* scalabilité verticale 
* diminuer le scheduler (actuel 5 min)
