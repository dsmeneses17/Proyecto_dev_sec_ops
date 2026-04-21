# Terraform GCP Bootstrap

Este directorio contiene el bootstrap de infraestructura para la Entrega 2 en GCP.

## Estructura

- `modules/`: modulos reutilizables por recurso.
- `envs/foundation-dev`: red base (VPC + subredes + NAT + WAF opcional + LB opcional).
- `envs/dev`: composicion del entorno de aplicacion completo.
- `envs/stg`, `envs/prod`: reservados para siguientes etapas.

## Estrategia por fases

1. Empezar con `envs/foundation-dev` para crear solo red y perimetro.
2. Continuar con `envs/dev` para desplegar servicios de aplicacion y datos.

## Prerrequisitos

1. Terraform >= 1.6
2. gcloud CLI autenticado
3. Proyecto GCP con billing habilitado

## Inicio rapido (dev)

1. Autenticar:

```bash
gcloud auth login
gcloud auth application-default login
```

2. Crear bucket remoto para estado (una sola vez):

```bash
PROJECT_ID=<tu-project-id>
STATE_BUCKET=<tu-bucket-tfstate-unico>
REGION=us-central1

gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://$STATE_BUCKET"
gsutil versioning set on "gs://$STATE_BUCKET"
```

3. Ir a entorno dev:

```bash
cd infra/terraform/envs/dev
```

4. Copiar variables:

```bash
cp terraform.tfvars.example terraform.tfvars
```

5. Configurar backend remoto:

```bash
cp backend.tf.example backend.tf
# editar backend.tf con bucket/prefix reales
```

6. Inicializar y desplegar:

```bash
terraform init -upgrade
terraform fmt -recursive
terraform validate
terraform plan -out tfplan
terraform apply tfplan
```

## Notas

- Este bootstrap prioriza avanzar rapido con entorno `dev`.
- El backend se deja como ejemplo para no commitear datos sensibles.
- Los secretos se crean en Secret Manager desde variables de Terraform; no usar `.env` en produccion.
