-- Schema Supabase para conector Holded → ERP Grupo Tesela
-- Ejecutar en el SQL Editor de Supabase (proyecto: jpojckqnhepiuwefyvdr)

-- Contactos
CREATE TABLE IF NOT EXISTS holded_contacts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sociedad        TEXT NOT NULL,
    holded_id       TEXT NOT NULL,
    tipo            TEXT,
    nombre          TEXT,
    nif             TEXT,
    email           TEXT,
    saldo_pendiente NUMERIC(12,2),
    raw_json        JSONB,
    synced_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE(sociedad, holded_id)
);

-- Facturas de venta (ingresos)
CREATE TABLE IF NOT EXISTS holded_invoices (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sociedad         TEXT NOT NULL,
    holded_id        TEXT NOT NULL,
    numero           TEXT,
    fecha            DATE,
    fecha_vencimiento DATE,
    contact_id       TEXT,
    contact_nombre   TEXT,
    base_imponible   NUMERIC(12,2),
    iva              NUMERIC(12,2),
    total            NUMERIC(12,2),
    pendiente        NUMERIC(12,2),
    estado           TEXT,
    project_id       TEXT,
    raw_json         JSONB,
    synced_at        TIMESTAMPTZ DEFAULT now(),
    UNIQUE(sociedad, holded_id)
);

-- Facturas de compra (costes de material por obra)
CREATE TABLE IF NOT EXISTS holded_bills (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sociedad         TEXT NOT NULL,
    holded_id        TEXT NOT NULL,
    numero           TEXT,
    fecha            DATE,
    fecha_vencimiento DATE,
    proveedor_id     TEXT,
    proveedor_nombre TEXT,
    base_imponible   NUMERIC(12,2),
    iva              NUMERIC(12,2),
    total            NUMERIC(12,2),
    pendiente        NUMERIC(12,2),
    estado           TEXT,
    project_id       TEXT,
    cuenta_contable  TEXT,
    raw_json         JSONB,
    synced_at        TIMESTAMPTZ DEFAULT now(),
    UNIQUE(sociedad, holded_id)
);

-- Proyectos / Obras
CREATE TABLE IF NOT EXISTS holded_projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sociedad        TEXT NOT NULL,
    holded_id       TEXT NOT NULL,
    codigo          TEXT,
    nombre          TEXT,
    estado          TEXT,
    fecha_inicio    DATE,
    fecha_fin       DATE,
    presupuesto     NUMERIC(12,2),
    coste_acumulado NUMERIC(12,2),
    raw_json        JSONB,
    synced_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE(sociedad, holded_id)
);

-- Vista: aging de cobros vencidos
CREATE OR REPLACE VIEW v_aging_cobros AS
SELECT sociedad,
       contact_nombre,
       SUM(pendiente)         AS total_pendiente,
       MAX(fecha_vencimiento) AS ultimo_vencimiento
FROM holded_invoices
WHERE estado IN ('pending', 'overdue') AND pendiente > 0
GROUP BY sociedad, contact_nombre
ORDER BY total_pendiente DESC;

-- Vista: coste de material por obra (sin IVA, sin mano de obra)
CREATE OR REPLACE VIEW v_costes_por_obra AS
SELECT b.sociedad,
       p.nombre AS obra,
       p.codigo,
       SUM(b.base_imponible) AS coste_material
FROM holded_bills b
JOIN holded_projects p
  ON b.project_id = p.holded_id AND b.sociedad = p.sociedad
GROUP BY b.sociedad, p.nombre, p.codigo
ORDER BY coste_material DESC;

-- Vista: margen bruto por obra
CREATE OR REPLACE VIEW v_margen_por_obra AS
SELECT p.codigo,
       p.nombre,
       p.sociedad,
       COALESCE(v.total_ventas,   0) AS ingresos,
       COALESCE(c.coste_material, 0) AS costes,
       COALESCE(v.total_ventas,   0)
         - COALESCE(c.coste_material, 0) AS margen_bruto
FROM holded_projects p
LEFT JOIN (
    SELECT project_id, sociedad, SUM(base_imponible) AS total_ventas
    FROM holded_invoices GROUP BY project_id, sociedad
) v ON v.project_id = p.holded_id AND v.sociedad = p.sociedad
LEFT JOIN (
    SELECT project_id, sociedad, SUM(base_imponible) AS coste_material
    FROM holded_bills GROUP BY project_id, sociedad
) c ON c.project_id = p.holded_id AND c.sociedad = p.sociedad;
