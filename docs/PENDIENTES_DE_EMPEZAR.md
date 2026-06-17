# Pendientes de empezar (aún sin comenzar)

> Trabajo identificado pero todavía no iniciado.
> Fecha: junio 2026. Cobertura global actual: **70,4 %**.

## Contexto
El repo ha crecido mucho (ahora incluye el servidor HTTP remoto, OAuth, etc.) y
varias áreas que antes señalé ya fueron cubiertas por automatización paralela
(p. ej. `internal/ghmcp` *URL helpers*, `pkg/translations`, completions de
recursos). La foto de huecos ha cambiado; conviene partir de una **medición
fresca** antes de atacar cada uno.

## Paquetes con menor cobertura (objetivos prioritarios)

| Paquete | Cobertura | Notas |
|---|---:|---|
| `internal/ghmcp` | **2,5 %** | Creció con el servidor HTTP; arranque, hosts GHES/GHEC, transporte. Mayor hueco. |
| `cmd/mcpcurl` | **8,9 %** | Lógica pura de construcción de args/JSON-RPC; fácil de testear. |
| `internal/githubv4mock` | 18,1 % | Utilidad de test; cobertura indirecta. |
| `pkg/http` | 36,5 % | Capa HTTP del servidor remoto. |
| `pkg/ifc` | 40,0 % | Interfaces/contratos. |
| `pkg/http/transport` | 46,7 % | Transporte HTTP. |
| `pkg/log` | 47,4 % | Logging E/S. |
| `pkg/http/middleware` | 50,6 % | Middleware del servidor. |
| `pkg/utils` | 56,2 % | Helpers de resultados de herramientas. |

## Tareas concretas sin empezar
1. **`internal/ghmcp`**: tests del arranque del servidor, derivación de hosts
   GHES/GHEC, wrappers de transporte/`RoundTrip` y middleware. (Mayor impacto.)
2. **`cmd/mcpcurl`**: tests de `buildArgumentsMap`, `buildJSONRPCRequest`,
   `addCommandFromTool` (transformaciones puras, sin E/S).
3. **`pkg/http` y submódulos** (`transport`, `middleware`, `oauth`): cubrir
   rutas del servidor remoto.
4. **`pkg/github/actions.go`**: handlers de workflow jobs/artifacts/rerun
   (revisar primero qué cubrió ya PR #6 para no duplicar).
5. **Re-análisis de cobertura**: ejecutar un barrido limpio
   (`go test -cover ./...`) y regenerar la priorización, dado el ritmo de cambios
   del repo.

## Recomendación de orden
`internal/ghmcp` → `cmd/mcpcurl` → `pkg/http*`. Empezar siempre confirmando la
cobertura actual del paquete para no repetir trabajo ya hecho en paralelo.
