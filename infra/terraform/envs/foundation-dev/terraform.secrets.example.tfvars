# Copia este archivo a terraform.local.tfvars solo si necesitas override local.
# Este archivo NO debe contener secretos reales ni debe subirse a git.

# Opcional: override local de password de DB.
# Si no lo defines, Terraform usara Secret Manager (db_password_secret_name + secret_version).
# db_password = "REPLACE_WITH_LOCAL_SECRET"
