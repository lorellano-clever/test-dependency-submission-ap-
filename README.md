# Demostración: SBOM externo → GitHub Dependency Submission API

Esta demostración simula el siguiente flujo:

```text
JFrog / Nexus
  ↓
CycloneDX SBOM
  ↓
Script convertidor
  ↓
Instantánea (snapshot) de GitHub Dependency Submission API
  ↓
Gráfico de dependencias de GitHub (Dependency Graph)
  ↓
Alertas de Dependabot
```

## Archivos

- `external-dependencies-simulated.cdx.json`
  - SBOM de CycloneDX simulado, exportado desde JFrog/Nexus.
- `scripts/cdx_to_github_snapshot.py`
  - Convierte los componentes de CycloneDX en una instantánea (snapshot) de dependencias de GitHub.
- `.github/workflows/submit-external-sbom.yml`
  - Flujo de trabajo (workflow) de GitHub Actions que envía la instantánea a GitHub.

## Setup

1. Realiza un commit de estos archivos en el repositorio.
2. Habilita el Gráfico de dependencias (Dependency graph) y las Alertas de Dependabot (Dependabot alerts) en la configuración de seguridad del repositorio.
3. Ejecuta el flujo de trabajo manualmente desde Actions → Submit external SBOM dependencies → Run workflow.
4. Valida las dependencias en Insights → Dependency graph o en Security → Dependabot alerts.

## Limitación importante

Este flujo es ideal para demostrar que GitHub puede ingestar dependencias externas y generar alertas cuando coinciden con la base de datos de avisos de seguridad de GitHub (GitHub Advisory Database).

Nota importante: Los Pull Requests (PR) de corrección automática no están garantizados si la dependencia solo existe en un SBOM/instantánea externo y no hay un manifiesto o archivo de bloqueo (lockfile) editable dentro del repositorio.

Por lo general, las actualizaciones de seguridad de Dependabot necesitan un archivo concreto que puedan modificar, como por ejemplo: 

- package.json / package-lock.json
- pom.xml
- go.mod

(Entre otros archivos de configuración de dependencias estándar).
