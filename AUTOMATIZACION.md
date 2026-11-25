# Publicación independiente de Cada Mañana

Esta propuesta no modifica la web ni las lecturas existentes. Publica **solo** una lectura completa previamente aprobada desde `lecturas-programadas.json`, una noche antes de su fecha, a las 21:10 de Costa Rica.

## Activación

1. Revisar y aprobar el contenido bíblico RV1909 y la reflexión original de cada fecha. Agregar cada entrada a `lecturas-programadas.json` con los campos del ejemplo.
2. En GitHub → Settings → Secrets and variables → Actions → New repository secret, agregar `SUPABASE_SERVICE_ROLE_KEY` de **este** proyecto Supabase. Nunca poner la clave en código, mensajes, capturas ni archivos públicos.
3. Fusionar el PR a `main` únicamente después de verificar la clave, el contenido y el flujo manual.
4. En Actions, ejecutar manualmente el flujo con una fecha **preparada** de prueba. Verificar la fila en Supabase. Las ejecuciones programadas pueden retrasarse por GitHub.
5. Mantener vigilancia de lectura y audio por separado: este flujo no crea reflexiones ni MP3 y no garantiza que ElevenLabs continúe después del 17 de noviembre.

Seguridad: `fecha` tiene restricción UNIQUE en Supabase; el proceso usa `on_conflict=fecha` con `ignore-duplicates`, jamás actualiza una fila existente. Si falta una lectura preparada o hay datos incompletos, falla con aviso en GitHub Actions en vez de publicar contenido provisional.

**Pendiente antes de considerarlo autónomo:** preparar un lote de lecturas verificadas para fechas futuras, configurar el secreto y comprobar una ejecución real. Para audio gratuito se requiere una segunda implementación y prueba de voces.
