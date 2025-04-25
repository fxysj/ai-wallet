docker-compose build
#这个命令会根据 Dockerfile 和 docker-compose.yml 配置构建镜像

#启动服务： 启动容器并在后台运行服务：
docker-compose up -d

#查看容器日志： 如果你需要查看容器的日志以调试问题，可以使用以下命令：

docker-compose logs -f python-app

#如果应用仍然出现问题，你可以进入容器进行调试：

docker exec -it python-app /bin/bash


docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=ai_wallet_db -p 3306:3306 -v /Users/sin/ai/ai-wallet/mysql/data:/var/lib/mysql -d mysql:8.0

docker build -f base_dockerfile -t registry.cn-hangzhou.aliyuncs.com/sinrpc/mypython:latest .

docker push registry.cn-hangzhou.aliyuncs.com/sinrpc/mypython:latest

docker rmi registry.cn-hangzhou.aliyuncs.com/sinrpc/ai-wallet:latest

docker rmi redis:alpine

docker-compose down

sudo certbot --nginx -d ai.testtikee.com

sudo certbot --webroot -w /usr/local/openresty/nginx/html -d testapi1.tikee.com

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'I5xlwT@2025';
FLUSH PRIVILEGES;

CREATE USER 'ai-wallet'@'%' IDENTIFIED BY 'I5xlwT@2025';
GRANT ALL PRIVILEGES ON *.* TO 'ai-wallet'@'%' WITH GRANT OPTION;

OPENAI_API_KEY=sk-I5XLWtJAWOXAEQjJOuSb6FXQsWNuInkuNxin4jVwVM4rPCmy
OPENAI_API_BASE_URL=https://www.dmxapi.cn/v1

docker-compose -f docker-compose-test.yaml up --build

sudo docker logs  ai-wallet-python-app-1