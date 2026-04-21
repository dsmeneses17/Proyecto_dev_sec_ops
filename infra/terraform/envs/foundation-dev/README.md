# Foundation Dev (VPC + LB)

Este stack despliega la base de red y perimetro para avanzar por etapas, sin desplegar toda la aplicacion.

Incluye:

- VPC custom
- Subredes separadas por capa (ingress, app, data, mgmt, serverless connector)
- Cloud Router + Cloud NAT
- Cloud Armor (opcional)
- HTTP Global Load Balancer hacia Cloud Run frontend (opcional)
- Bucket privado de Cloud Storage para variantes de imagenes (thumbnail, medium, large)
- Service Account de worker con permisos de escritura en bucket

## Flujo recomendado

1. Fase red:
- `create_frontend_lb=false`
- aplicar solo VPC/subredes/NAT/Cloud Armor

2. Fase perimetro app:
- desplegar frontend en Cloud Run
- definir `frontend_cloud_run_service_name`
- cambiar `create_frontend_lb=true`
- aplicar para crear LB externo

## Inicializacion

```bash
cd infra/terraform/envs/foundation-dev
cp backend.tf.example backend.tf
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
```

## Nota

No incluye Cloud DNS por ahora, segun requerimiento actual.

## Storage de imagenes

El entorno `foundation-dev` crea un bucket privado (Public Access Prevention + Uniform Bucket-Level Access) y define variables de entorno para backend:

- `STORAGE_PROVIDER=gcs`
- `GCP_PROJECT_ID`
- `GCS_BUCKET_NAME`

Tambien crea una Service Account para el worker de imagenes con permiso `roles/storage.objectAdmin` sobre el bucket.
