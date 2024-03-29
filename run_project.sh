echo 'create popug-network'
docker network create popug-network
echo 'network created'

echo 'start project...'

echo 'run kafka service...'
docker-compose -f kafka_service/docker-compose.yml up -d
echo 'kafka service is being started...'
# waiting for kafka
docker-compose -f kafka_service/docker-compose.yml exec kafka kafka-topics --bootstrap-server kafka:29092 --list
echo 'kafka service started'

echo 'run auth service...'
docker-compose -f auth_service/docker-compose.yml up --build -d
echo 'auth service is being started...'

echo 'run accounting service...'
docker-compose -f accounting_service/docker-compose.yml up --build -d
echo 'accounting service is being started...'

echo 'run analytics service...'
docker-compose -f analytics_service/docker-compose.yml up --build -d
echo 'analytics service is being started...'

echo 'run task service...'
docker-compose -f task_service/docker-compose.yml up --build -d
echo 'task service is being started...'

echo 'project has been ran'