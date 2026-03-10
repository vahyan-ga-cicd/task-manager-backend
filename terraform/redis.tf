resource "aws_elasticache_cluster" "redis" {

  cluster_id           = "task-manager-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  security_group_ids = [aws_security_group.redis_sg.id]
}