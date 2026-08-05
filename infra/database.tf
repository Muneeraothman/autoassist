resource "aws_db_subnet_group" "main" {
  name       = "autoassist-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "autoassist-db-subnet-group"
  }
}

resource "aws_db_instance" "main" {
  identifier     = "autoassist-db"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "autoassist"
  username = "postgres"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # Without this, password/config changes queue for the next maintenance
  # window instead of applying right away - terraform apply reports success
  # immediately, but RDS keeps running the OLD password until that window
  # opens, silently breaking anything that was just given the new one.
  apply_immediately = true

  # Deliberate for the destroy-between-sessions workflow: a "real" production
  # DB would want deletion_protection + a final snapshot. Here, easy
  # destroy/recreate is the actual goal, not durability across teardowns —
  # seed.sql is the durable source of truth, not this instance.
  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "autoassist-db"
  }
}
