resource "aws_elasticache_subnet_group" "redis" {
  name       = "redis-subnet-group"
  subnet_ids = data.aws_subnets.default.ids
}

resource "aws_elasticache_cluster" "redis" {

  cluster_id           = "task-manager-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis_sg.id]
}

resource "aws_ssm_parameter" "redis_host" {
  name        = "/task-manager/redis-host"
  description = "The endpoint of the Redis Elasticache cluster"
  type        = "String"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}