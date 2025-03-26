docker-compose build
#这个命令会根据 Dockerfile 和 docker-compose.yml 配置构建镜像

#启动服务： 启动容器并在后台运行服务：
docker-compose up -d

#查看容器日志： 如果你需要查看容器的日志以调试问题，可以使用以下命令：

docker-compose logs -f python-app

#如果应用仍然出现问题，你可以进入容器进行调试：

docker exec -it python-app /bin/bash