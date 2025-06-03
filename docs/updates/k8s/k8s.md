下面为你提供一系列 Kubernetes 的 YAML 文件，用于部署 20 个 FastAPI 服务实例并使用 Nginx 进行负载均衡。假设你的 FastAPI 服务 Docker 镜像为 `my-fastapi-app:latest`，且已经推送到镜像仓库可供 K8s 集群拉取。

### 1. FastAPI 服务部署文件（`fastapi-deployment.yaml`）
这个文件将部署 20 个 FastAPI 服务副本。
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
spec:
  replicas: 20
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
        - name: fastapi
          image: my-fastapi-app:latest
          ports:
            - containerPort: 8000
```

### 2. FastAPI 服务 Service 文件（`fastapi-service.yaml`）
此文件用于创建一个 Kubernetes Service，将 20 个 FastAPI 服务副本暴露出来。
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

### 3. Nginx 部署文件（`nginx-deployment.yaml`）
部署 Nginx 服务，用于对 20 个 FastAPI 服务进行负载均衡。
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.23
          ports:
            - containerPort: 80
          volumeMounts:
            - name: nginx-config
              mountPath: /etc/nginx/conf.d
      volumes:
        - name: nginx-config
          configMap:
            name: nginx-config
```

### 4. Nginx 配置 ConfigMap 文件（`nginx-configmap.yaml`）
创建一个 ConfigMap 来存储 Nginx 的配置文件，用于将请求转发到 FastAPI 服务。
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  default.conf: |
    upstream fastapi_backend {
      server fastapi-service:80;
    }

    server {
      listen 80;

      location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
      }
    }
```

### 5. Nginx 服务 Service 文件（`nginx-service.yaml`）
创建一个 Kubernetes Service 来暴露 Nginx 服务，以便外部可以访问。
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

### 使用方法
将上述 YAML 文件保存到本地，然后按以下顺序应用到 Kubernetes 集群：
```bash
kubectl apply -f fastapi-deployment.yaml
kubectl apply -f fastapi-service.yaml
kubectl apply -f nginx-configmap.yaml
kubectl apply -f nginx-deployment.yaml
kubectl apply -f nginx-service.yaml
```

### 注意事项
- 请将 `my-fastapi-app:latest` 替换为你实际的 FastAPI 服务 Docker 镜像。
- 确保你的 Kubernetes 集群支持 `LoadBalancer` 类型的 Service，否则可以将 `nginx-service.yaml` 中的 `type` 改为 `NodePort`。
- 可以根据实际需求调整副本数量和 Nginx 配置。 