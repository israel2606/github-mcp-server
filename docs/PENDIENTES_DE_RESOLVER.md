# Pendientes de resolver (en curso / con bloqueo conocido)

> Cosas ya empezadas o con causa identificada, que faltan por cerrar.
> Fecha: junio 2026.

## 1. Fusionar el PR #10 (arreglo de CI) — EN CURSO
- Estado: abierto; matriz de build en verde. Falta confirmar `lint`,
  `docs-check`, `mcp-diff`, `license-check` y fusionar.
- Acción: vigilar checks restantes (suscripción activa) y mergear cuando esté
  todo verde.

## 2. Regresión de cobertura en `pkg/lockdown` — 79 %
- El refactor de PR #6 reescribió el paquete (`NewRepoAccessCache` con cliente
  REST, `viewerLoginFor`, `checkPushAccess`), dejando **obsoletos** los tests de
  cobertura que añadió PR #5 (eliminados en PR #10).
- Pendiente: **re-cubrir el nuevo diseño** (caché por viewer, `checkPushAccess`
  vía REST, reintentos de `viewerLoginFor`, ramas de `getRepoAccessInfo`).
  Objetivo: volver a ~95 %+.

## 3. Workflow `lint.yml` — verificar estabilidad del toolchain
- Ya está fijado a `setup-go: '1.25'` + `golangci-lint v2.9` (resuelve el crash
  Go 1.26 vs golangci 1.25).
- Pendiente: confirmar que queda verde en el PR #10 y revisar que otras actions
  no sigan en **Node 20** (deprecado el 16-jun-2026).

## 4. Endurecer `.gitignore` (preventivo)
- El repo no usa `.env` ni `data/` hoy, y `.gitignore` no los contempla.
- Pendiente: añadir `.env`, `*.env` y `data/` por precaución, por si se crean
  en local. (No urgente, no hay fugas actuales.)

## 5. Limpieza de workflows duplicados/heredados
- La automatización paralela del fork ha generado workflows solapados y stubs.
- Pendiente (más allá de PR #10): revisar que no queden otros workflows
  redundantes o con actions deprecadas (`@v4`/`cache@v3`).
